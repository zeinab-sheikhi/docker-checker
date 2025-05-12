from enum import Enum

from pydantic import BaseModel, ConfigDict

from docker_scanner.schemas.trivy import VulnerabilitySummary


class StepStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class JobStatusResponse(BaseModel):
    job_id: str
    dockerfile: str | None = None

    # Build step
    build_status: StepStatus
    image_id: str | None = None

    # Scan step
    scan_status: StepStatus
    is_safe: bool | None = None
    vulnerabilities: list[VulnerabilitySummary] | None = None

    # Run step
    run_status: StepStatus
    performance: float | None = None

    error: str | None = None


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str

    model_config = ConfigDict(json_schema_extra={"example": {"detail": "Error message"}})
