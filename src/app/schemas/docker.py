from pydantic import BaseModel, Field


class DockerBuildImageResponse(BaseModel):
    """Response model for Docker build operation"""

    image_id: str | None = Field(None, description="ID of the built image")
    tags: list[str] = Field(..., description="Tags associated with the built image")

    class Config:
        json_schema_extra = {
            "example": {
                "image_id": "sha256:1234567890abcdef",
                "tags": ["latest"],
            }
        }


class DockerRunContainerResponse(BaseModel):
    """Response model for Docker run operation"""

    success: bool = Field(..., description="Whether the container ran successfully")
    container_id: str | None = Field(None, description="ID of the container if created")
    performance: float | None = Field(None, description="Performance metric from container execution")
    error: str | None = Field(None, description="Error message if run failed")

    class Config:
        json_schema_extra = {
            "example": {"success": True, "container_id": "abcdef1234567890", "performance": 0.99, "error": None}
        }
