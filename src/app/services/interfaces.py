from typing import BinaryIO, Protocol

from app.schemas.docker import DockerBuildResponse, DockerRunResponse


class DockerServiceInterface(Protocol):
    """Interface for Docker operations"""

    def build_image(self, dockerfile: BinaryIO, job_id: str) -> DockerBuildResponse:
        """Build a Docker image"""
        ...

    def run_container_with_volume(self, image_id: str) -> DockerRunResponse:
        """Run a container with volume"""
        ...

    def cleanup_image(self, image_id: str) -> None:
        """Clean up Docker image"""
        ...
