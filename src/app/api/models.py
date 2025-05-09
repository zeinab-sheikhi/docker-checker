# models.py
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class JobStatus(str, Enum):
    """Simple status enum for jobs"""
    PENDING = "pending"
    FAILED = "failed"
    SUCCESS = "success"


class DockerfileUploadResponse(BaseModel):
    """Simple response for dockerfile upload"""
    job_id: str = Field(..., description="Unique identifier for the job")
    status: JobStatus = Field(..., description="Status of the job")
    message: str = Field(..., description="Response message")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response without job_id"""
    success: bool = Field(default=False)
    message: str = Field(..., description="Error message")