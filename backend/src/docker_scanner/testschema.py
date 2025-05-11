# example_job_status_serialization.py

from docker_scanner.schemas.job_status import (
    BuildImageResult,
    JobStatus,
    JobStatusResponse,
    RunContainerResult,
    ScanImageResult,
)
from docker_scanner.schemas.trivy import VulnerabilitySummary

# Create example vulnerability summaries
vuln1 = VulnerabilitySummary(
    package="openssl",  # PkgName
    vulnerability_id="CVE-2023-1234",  # VulnerabilityID
    severity="HIGH",  # Severity
    title="Buffer Overflow in OpenSSL",  # Title
    description="A buffer overflow was found in OpenSSL that could allow remote attackers to execute arbitrary code.",  # Description
    fixed_version="1.1.1k",
)

# Create example step results
build_result = BuildImageResult(success=True, image_id="sha256:abcd1234", error=None)
scan_result = ScanImageResult(success=True, is_safe=True, vulnerabilities=[vuln1], error=None)
run_result = RunContainerResult(success=True, performance=0.98, error=None)

# Create the main job status response
job_status = JobStatusResponse(
    job_id="abc123",
    status=JobStatus.SUCCESS,
    dockerfile="FROM ubuntu:latest\n...",
    build_result=build_result,
    scan_result=scan_result,
    run_result=run_result,
    error=None,
)

# Serialize to JSON (Pydantic v2)
json_str = job_status.model_dump_json(indent=2)
print(json_str)

# If you are using Pydantic v1, use:
# json_str = job_status.json(indent=2)
# print(json_str)
