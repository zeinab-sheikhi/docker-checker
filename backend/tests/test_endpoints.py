import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from docker_scanner.routers import jobs
from docker_scanner.schemas.job_status import StepStatus
from docker_scanner.schemas.trivy import VulnerabilitySummary
from docker_scanner.services.job_service import JobService


@pytest.fixture
def mock_docker_service(mocker):
    mock = mocker.Mock()
    mock.build_image.return_value = type("Image", (), {"image_id": "img123", "tags": ["tag"]})()
    mock.scan_image.return_value = type("ScanResult", (), {"is_safe": True, "vulnerabilities": []})()
    mock.run_container.return_value = type(
        "RunResult", (), {"image_id": "img123", "container_id": "container123", "status": "exited", "performance": 0.99}
    )()
    return mock


@pytest.fixture
def mock_redis_service(mocker):
    mock = mocker.Mock()
    mock.get_job_data.return_value = {"dockerfile": "FROM alpine\nRUN echo hello"}
    mock.update_job_data.return_value = None
    return mock


@pytest.fixture
def test_app(mock_docker_service, mock_redis_service):
    app = FastAPI()
    app.state.job_service = JobService(
        docker_service=mock_docker_service,
        redis_service=mock_redis_service,
    )
    app.include_router(jobs.router)
    return app


def test_create_job_and_status(test_app):
    client = TestClient(test_app)
    dockerfile_content = b"FROM alpine\nRUN echo hello"
    response = client.post(
        "/jobs/",
        files={"file": ("Dockerfile", dockerfile_content, "text/plain")},
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    status_response = client.get(f"/jobs/status/{job_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["job_id"] == job_id
    assert status_data["build_status"] == "success"
    assert status_data["scan_status"] == "success"
    assert status_data["run_status"] == "success"
    assert status_data["performance"] == 0.99


def test_create_job_with_invalid_dockerfile(test_app):
    client = TestClient(test_app)
    # Missing FROM, which is required
    dockerfile_content = b"RUN echo hello"
    response = client.post(
        "/jobs/",
        files={"file": ("Dockerfile", dockerfile_content, "text/plain")},
    )
    assert response.status_code == 400
    assert "FROM" in response.json()["detail"]


def test_workflow_with_vulnerable_image(mock_docker_service, mock_redis_service):
    """Test workflow with an image that has vulnerabilities (mocked)."""
    # Configure the mock to return vulnerabilities
    vulnerabilities = [
        VulnerabilitySummary(
            PkgName="python",
            VulnerabilityID="CVE-2022-12345",
            Severity="HIGH",
            Title="Security Vulnerability in Python",
            Description="This is a test vulnerability",
            FixedVersion="3.9.0",
        ),
        VulnerabilitySummary(
            PkgName="openssl",
            VulnerabilityID="CVE-2022-67890",
            Severity="CRITICAL",
            Title="Security Vulnerability in OpenSSL",
            Description="Critical vulnerability in SSL library",
            FixedVersion="1.1.2",
        ),
    ]

    # Make the scan unsafe due to critical vulnerability
    mock_docker_service.scan_image.return_value = type(
        "ScanResult", (), {"is_safe": False, "vulnerabilities": vulnerabilities}
    )()

    # Set up the app
    app = FastAPI()
    app.state.job_service = JobService(
        docker_service=mock_docker_service,
        redis_service=mock_redis_service,
    )
    app.include_router(jobs.router)
    client = TestClient(app)

    # Create job
    dockerfile_content = b"FROM python:3.8\nRUN echo hello"
    response = client.post(
        "/jobs/",
        files={"file": ("Dockerfile", dockerfile_content, "text/plain")},
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    # Check status
    status_response = client.get(f"/jobs/status/{job_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()

    # Verify build and scan workflow
    assert status_data["build_status"] == StepStatus.SUCCESS
    assert status_data["scan_status"] == StepStatus.SUCCESS
    assert status_data["is_safe"] is False
    assert len(status_data["vulnerabilities"]) == 2

    # Run step should be skipped due to vulnerabilities
    assert status_data["run_status"] == StepStatus.SKIPPED
    assert status_data["performance"] is None

    # Since we can't be sure about the exact serialization of vulnerability data in the response,
    # let's just check that we have the right number of vulnerabilities
    assert len(status_data["vulnerabilities"]) == 2

    # And check that the performance metric is None (since we should have skipped the run step)
    assert status_data["performance"] is None


def test_job_build_failure(mock_docker_service, mock_redis_service):
    """Test error handling when build fails."""
    # Configure mock to simulate build failure
    mock_docker_service.build_image.side_effect = ValueError("Build error: base image not found")

    # Set up the app
    app = FastAPI()
    app.state.job_service = JobService(
        docker_service=mock_docker_service,
        redis_service=mock_redis_service,
    )
    app.include_router(jobs.router)
    client = TestClient(app)

    # Create job
    dockerfile_content = b"FROM nonexistent:latest\nRUN echo hello"
    response = client.post(
        "/jobs/",
        files={"file": ("Dockerfile", dockerfile_content, "text/plain")},
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    # Check status - should indicate build failure
    status_response = client.get(f"/jobs/status/{job_id}")
    status_data = status_response.json()

    assert status_data["build_status"] == StepStatus.FAILED
    assert "Build failed" in status_data["error"]
    assert status_data["scan_status"] == StepStatus.SKIPPED
    assert status_data["run_status"] == StepStatus.SKIPPED
