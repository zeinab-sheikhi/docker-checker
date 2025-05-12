import time

import pytest
from fastapi.testclient import TestClient

from docker_scanner.app import app
from docker_scanner.schemas.job_status import StepStatus

# Register the integration mark to avoid warnings
pytest.mark.integration = pytest.mark.skip(reason="Integration tests require running services")


@pytest.fixture(scope="module", autouse=True)
def setup_app_for_testing():
    """
    Set up the application for testing with proper initialization of services.
    This simulates the startup event that would normally occur in a running app.
    """
    # Initialize services that would normally be created in the startup event
    from docker_scanner.services.docker_service import DockerService
    from docker_scanner.services.job_service import JobService
    from docker_scanner.services.redis_service import RedisService

    # Create instances for testing
    app.state.redis_service = RedisService(host="localhost", port=6379, db=0)
    app.state.docker_service = DockerService()
    app.state.job_service = JobService(app.state.docker_service, app.state.redis_service)

    yield

    # Cleanup that would normally occur in the shutdown event
    if hasattr(app.state, "redis_service"):
        try:
            app.state.redis_service.close()
        except Exception as e:
            pass

    if hasattr(app.state, "docker_service"):
        try:
            app.state.docker_service.cleanup_all_resources()
        except Exception as e:
            pass


@pytest.mark.integration
class TestDockerScannerIntegration:
    """Integration tests for the Docker Scanner service."""

    @pytest.fixture(scope="class")
    def client(self) -> TestClient:
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def api_prefix(self) -> str:
        """Get API prefix from settings."""
        from docker_scanner.settings import settings

        return settings.app_config.api_prefix

    def wait_for_job_completion(self, client: TestClient, job_id: str, timeout_seconds: int = 30) -> dict:
        """Helper method to wait for job completion and return final status."""
        for _ in range(timeout_seconds):
            status_response = client.get(f"/api/v1/jobs/status/{job_id}")
            status_data = status_response.json()

            # Check for failure
            if status_data.get("error"):
                return status_data

            # Check if all steps are complete (either success or failed)
            if (
                status_data["build_status"] in [StepStatus.SUCCESS, StepStatus.FAILED]
                and status_data["scan_status"] in [StepStatus.SUCCESS, StepStatus.FAILED]
                and status_data["run_status"] in [StepStatus.SUCCESS, StepStatus.FAILED]
            ):
                return status_data

            time.sleep(1)

        pytest.fail(f"Job {job_id} did not complete within {timeout_seconds} seconds")
        return {}  # This will never execute due to pytest.fail, but makes type checkers happy

    def test_full_workflow(self, client: TestClient, api_prefix: str):
        """Test the full Dockerfile scan and run workflow."""
        # Simple valid Dockerfile that writes performance metrics
        dockerfile_content = b"FROM alpine:latest\nRUN echo hello\nCMD echo '{\"perf\": 0.42}' > /data/perf.json"

        # Submit job
        response = client.post(
            f"{api_prefix}/jobs/",
            files={"file": ("Dockerfile", dockerfile_content, "text/plain")},
        )
        assert response.status_code == 200, f"POST /jobs/ failed: {response.text}"
        data = response.json()
        assert "job_id" in data, f"Response JSON: {data}"
        job_id = data["job_id"]

        # Wait for job completion
        status_data = self.wait_for_job_completion(client, job_id)

        # Verify successful job
        assert status_data["build_status"] == StepStatus.SUCCESS, f"Build failed: {status_data.get('error')}"
        assert status_data["scan_status"] == StepStatus.SUCCESS, f"Scan failed: {status_data.get('error')}"
        assert status_data["run_status"] == StepStatus.SUCCESS, f"Run failed: {status_data.get('error')}"
        assert status_data["performance"] is not None, "Performance metric not found"
        assert status_data["performance"] == 0.42, f"Expected performance value 0.42, got {status_data['performance']}"

        # Additional validations
        assert status_data["is_safe"] is True, "Alpine should be safe"
        assert status_data["vulnerabilities"] == [], "No vulnerabilities expected for Alpine"
        assert status_data["dockerfile"] == dockerfile_content.decode("utf-8"), "Dockerfile content mismatch"

    def test_invalid_dockerfile(self, client: TestClient, api_prefix: str):
        """Test submitting an invalid Dockerfile."""
        # Invalid Dockerfile (missing FROM instruction)
        invalid_dockerfile = b"RUN echo hello"

        # Submit job - should be rejected
        response = client.post(
            f"{api_prefix}/jobs/",
            files={"file": ("Dockerfile", invalid_dockerfile, "text/plain")},
        )

        # Verify rejection
        assert response.status_code == 400, "Invalid Dockerfile should be rejected"
        error_data = response.json()
        assert "detail" in error_data, "Error response should contain 'detail'"
        assert "FROM" in error_data["detail"], "Error should mention missing FROM instruction"

    def test_dockerfile_with_extension(self, client: TestClient, api_prefix: str):
        """Test submitting a Dockerfile with an extension (should be rejected)."""
        # Valid Dockerfile content but with extension in filename
        dockerfile_content = b"FROM alpine\nRUN echo hello"

        # Submit with .txt extension - should be rejected
        response = client.post(
            f"{api_prefix}/jobs/",
            files={"file": ("Dockerfile.txt", dockerfile_content, "text/plain")},
        )

        # Verify rejection
        assert response.status_code == 400, "Dockerfile with extension should be rejected"
        error_data = response.json()
        assert "detail" in error_data, "Error response should contain 'detail'"
        assert "Not a Dockerfile" in error_data["detail"], "Error should indicate invalid Dockerfile"

    def test_health_endpoint(self, client: TestClient):
        """Test the health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200, "Health endpoint should return 200"
        assert response.json() == {"message": "API is running."}, "Health endpoint response mismatch"

    def test_root_redirect(self, client: TestClient):
        """Test that root path redirects to docs."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307, "Root should redirect"
        assert response.headers["location"] == "/docs", "Root should redirect to /docs"

    @pytest.mark.skip(
        reason="This test uses an older version of Python that likely has vulnerabilities. "
        "It should be run manually in a controlled environment."
    )
    def test_vulnerable_dockerfile(self, client: TestClient, api_prefix: str):
        """
        Test a Dockerfile with potential vulnerabilities.

        This test is marked to be skipped by default as it uses an older Python version
        that likely has known vulnerabilities. This is useful for testing the vulnerability
        scanning functionality, but should be run carefully and manually.
        """
        # Using an older Python version that likely has vulnerabilities
        dockerfile_content = (
            b"FROM python:3.8-slim\n"
            b"RUN pip install flask==2.0.0\n"  # Older version that might have vulnerabilities
            b"WORKDIR /app\n"
            b"COPY . .\n"
            b"CMD echo '{\"perf\": 0.75}' > /data/perf.json"
        )

        # Submit job
        response = client.post(
            f"{api_prefix}/jobs/",
            files={"file": ("Dockerfile", dockerfile_content, "text/plain")},
        )
        assert response.status_code == 200, f"POST /jobs/ failed: {response.text}"
        data = response.json()
        job_id = data["job_id"]

        # Wait for job completion
        status_data = self.wait_for_job_completion(
            client, job_id, timeout_seconds=60
        )  # Longer timeout for larger image

        # Verify build and scan worked
        assert status_data["build_status"] == StepStatus.SUCCESS, f"Build failed: {status_data.get('error')}"
        assert status_data["scan_status"] == StepStatus.SUCCESS, f"Scan failed: {status_data.get('error')}"

        # Check for vulnerabilities - this might vary based on the image chosen
        # We don't assert on specific vulnerabilities, but just check the scan worked
        assert status_data["vulnerabilities"] is not None, "Vulnerabilities should be populated"

        # Log some info about found vulnerabilities (for debugging purposes)
        if status_data["vulnerabilities"]:
            critical_vulns = [v for v in status_data["vulnerabilities"] if v.get("severity", "") == "CRITICAL"]
            high_vulns = [v for v in status_data["vulnerabilities"] if v.get("severity", "") == "HIGH"]
            print(f"Found {len(critical_vulns)} CRITICAL and {len(high_vulns)} HIGH vulnerabilities")

        # Check if run was performed based on scan results
        if status_data["is_safe"] is True:
            assert status_data["run_status"] == StepStatus.SUCCESS, "Container should have run if image is safe"
            assert status_data["performance"] is not None, "Performance metric should be present"
        else:
            assert status_data["run_status"] == StepStatus.SKIPPED, "Container should not run if image is unsafe"
