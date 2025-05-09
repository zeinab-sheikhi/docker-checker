import json

import docker
from docker.errors import APIError, BuildError
from docker.models.containers import Container
from docker.models.volumes import Volume

from app.core.settings import settings
from app.schemas.docker import DockerBuildResponse, DockerRunResponse
from app.services.interfaces import DockerServiceInterface


class DockerService(DockerServiceInterface):
    """Service for handling Docker operations"""

    def __init__(self):
        """Initialize Docker client"""
        self.client = docker.from_env()
        self.timeout = settings.docker_timeout
        self.cleanup_images = settings.docker_cleanup_images

    def build_image(self, dockerfile_path: str) -> DockerBuildResponse:
        """
        Build a Docker image from a Dockerfile
        Returns: Build response with status and image ID
        """
        try:
            image, _ = self.client.images.build(
                path=dockerfile_path,
                rm=True,  # Remove intermediate containers
                forcerm=True,  # Always remove intermediate containers
                timeout=self.timeout,
            )
            return DockerBuildResponse(success=True, image_id=image.id)
        except (BuildError, APIError) as e:
            return DockerBuildResponse(success=False, error=str(e))
        except Exception as e:
            return DockerBuildResponse(success=False, error=f"Unexpected error during build: {str(e)}")

    def run_container_with_volume(self, image_id: str) -> DockerRunResponse:
        """
        Run container with a volume mounted at /data
        Returns: Run response with status and performance
        """
        volume = None
        container = None
        try:
            # Create volume for /data
            volume = self.client.volumes.create()

            # Run main container
            container = self.client.containers.run(
                image_id, detach=True, volumes={volume.name: {"bind": "/data", "mode": "rw"}}, timeout=self.timeout
            )

            # Wait for container to finish
            result = container.wait(timeout=self.timeout)
            if result["StatusCode"] != 0:
                return DockerRunResponse(
                    success=False,
                    container_id=container.id,
                    error=f"Container exited with status {result['StatusCode']}",
                )

            # Read performance from volume using a temporary container
            performance = self._read_performance_from_volume(volume)
            if performance is None:
                return DockerRunResponse(
                    success=False, container_id=container.id, error="Failed to read performance data"
                )

            return DockerRunResponse(success=True, container_id=container.id, performance=performance)

        except Exception as e:
            return DockerRunResponse(success=False, container_id=container.id if container else None, error=str(e))
        finally:
            # Cleanup
            self._cleanup_resources(container, volume)

    def _read_performance_from_volume(self, volume: Volume) -> float | None:
        """Read performance value from the volume"""
        try:
            # Use alpine for small footprint
            result = self.client.containers.run(
                "alpine",
                "cat /data/perf.json",
                volumes={volume.name: {"bind": "/data", "mode": "ro"}},
                remove=True,
                timeout=self.timeout,
            )

            perf_data = json.loads(result.decode("utf-8"))
            return float(perf_data["perf"])
        except Exception:
            return None

    def _cleanup_resources(self, container: Container | None, volume: Volume | None):
        """Clean up Docker resources"""
        try:
            if container:
                container.remove(force=True)
            if volume:
                volume.remove(force=True)
        except Exception as e:
            print(f"Error cleaning up resources: {e}")
            pass  # Best effort cleanup

    def cleanup_image(self, image_id: str) -> None:
        """Remove a Docker image"""
        try:
            if self.cleanup_images:
                self.client.images.remove(image_id, force=True)
        except Exception as e:
            print(f"Error cleaning up image: {e}")
            pass  # Best effort cleanup
