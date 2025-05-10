from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job status enumeration"""

    PENDING = "pending"
    BUILDING = "building"
    RUNNING = "running"
    FAILED = "failed"
    SUCCESS = "success"


class JobResponse(BaseModel):
    """Response model for job status"""

    job_id: str = Field(..., description="Unique identifier for the job")
    status: JobStatus = Field(..., description="Current status of the job")
    performance: float | None = Field(None, description="Performance metric if job succeeded")
    message: str | None = Field(None, description="Error message if job failed")
    scan_report: str | None = Field(None, description="Scan report")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "success",
                "performance": 0.99,
                "message": None,
            }
        }
