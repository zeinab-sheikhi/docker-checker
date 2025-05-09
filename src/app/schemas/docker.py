from pydantic import BaseModel, Field


class DockerBuildResponse(BaseModel):
    """Response model for Docker build operation"""

    success: bool = Field(..., description="Whether the build succeeded")
    image_id: str | None = Field(None, description="ID of the built image if successful")
    error: str | None = Field(None, description="Error message if build failed")

    class Config:
        json_schema_extra = {"example": {"success": True, "image_id": "sha256:1234567890abcdef", "error": None}}


class DockerRunResponse(BaseModel):
    """Response model for Docker run operation"""

    success: bool = Field(..., description="Whether the container ran successfully")
    container_id: str | None = Field(None, description="ID of the container if created")
    performance: float | None = Field(None, description="Performance metric from container execution")
    error: str | None = Field(None, description="Error message if run failed")

    class Config:
        json_schema_extra = {
            "example": {"success": True, "container_id": "abcdef1234567890", "performance": 0.99, "error": None}
        }
