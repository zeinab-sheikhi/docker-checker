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

    image_id: str = Field(..., description="ID of the image used to create the container")
    container_id: str = Field(..., description="ID of the container")
    status: str = Field(..., description="Status of the container (e.g., exited, running)")
    performance: float | None = Field(None, description="Performance metric from container execution")

    class Config:
        json_schema_extra = {
            "example": {
                "image_id": "sha256:1234567890abcdef",
                "container_id": "abcdef1234567890",
                "status": "exited",
                "performance": 0.99,
            }
        }
