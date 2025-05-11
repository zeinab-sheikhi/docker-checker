from enum import Enum

from pydantic import BaseModel

from docker_scanner.schemas.trivy import VulnerabilitySummary


class JobStatus(str, Enum):
    PENDING = "pending"
    BUILDING = "building"
    SCANNING = "scanning"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class BuildImageResult(BaseModel):
    success: bool
    image_id: str | None = None
    error: str | None = None


class RunContainerResult(BaseModel):
    success: bool
    performance: float | None = None
    error: str | None = None


class ScanImageResult(BaseModel):
    success: bool  # Indicates if the scan step itself succeeded (not just if the image is safe)
    is_safe: bool | None = None  # True if image is safe to run, False if not, None if scan failed
    vulnerabilities: list[VulnerabilitySummary] | None = None  # List of found vulnerabilities
    error: str | None = None  # Error message if scan failed


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    # dockerfile: Optional[str] = None
    build_result: BuildImageResult | None = None
    scan_result: ScanImageResult | None = None
    run_result: RunContainerResult | None = None
    error: str | None = None
