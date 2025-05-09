import json
import logging
import time
from typing import BinaryIO, Protocol

import docker
from docker.models.containers import Container

from app.schemas.docker import DockerBuildResponse, DockerRunResponse
from app.settings import settings


class DockerServiceInterface(Protocol):
    """Interface for Docker operations"""

    def build_image(self, dockerfile: BinaryIO, job_id: str) -> DockerBuildResponse:
        """Build a Docker image"""
        ...

    def run_container(self, image_id: str) -> DockerRunResponse:
        """Run a container and get its output"""
        ...


class DockerService(DockerServiceInterface):
    """Service for handling Docker operations"""

    def __init__(self):
        """Initialize Docker client"""
        self.client = docker.from_env()
        self.timeout = settings.docker_timeout

    def build_image(self, dockerfile: BinaryIO, job_id: str) -> DockerBuildResponse:
        """Build a Docker image from a dockerfile"""
        try:
            logging.info(f"Building image for job {job_id}")
            image, _ = self.client.images.build(
                fileobj=dockerfile,
                tag=f"docker-check-{job_id}",
                rm=True,
                forcerm=True,
            )
            logging.info(f"Successfully built image: {image.id}")
            return DockerBuildResponse(success=True, image_id=image.id)
        except Exception as e:
            logging.error(f"Failed to build image: {str(e)}")
            return DockerBuildResponse(success=False, error=str(e))

    def run_container(self, image_id: str) -> DockerRunResponse:
        """Run a container and process its output"""
        container = None
        try:
            container = self._start_container(image_id)

            # Give the container a moment to write the file
            time.sleep(1)  # Wait 1 second

            # Try to read performance data while container is running
            performance = self._read_performance_data(container)
            if performance is not None:
                return DockerRunResponse(success=True, container_id=container.id, performance=performance)

            # If we couldn't read the data, wait for container to finish and check logs
            exit_status, logs = self._wait_for_container(container)
            if exit_status != 0:
                return self._create_error_response(
                    container, f"Container exited with status {exit_status}. Logs: {logs}"
                )

            return self._create_error_response(container, "Failed to read performance data")

        except Exception as e:
            return self._handle_container_error(container, e)
        finally:
            self._cleanup_container(container)

    def _start_container(self, image_id: str) -> Container:
        """Start a container with the given image ID"""
        logging.info(f"Starting container with image {image_id}")
        return self.client.containers.run(
            image=image_id,
            detach=True,
        )

    def _wait_for_container(self, container: Container) -> tuple[int, str]:
        """Wait for container to finish and get its logs"""
        result = container.wait(timeout=self.timeout)
        logs = container.logs().decode("utf-8").strip()

        # Log container output
        for line in logs.split("\n"):
            logging.info(f"  {line}")

        return result["StatusCode"], logs

    def _read_performance_data(self, container: Container) -> float | None:
        """Read performance data from /data/perf.json in the container"""
        try:
            # Execute cat command in the running container
            exit_code, output = container.exec_run(cmd=["cat", "/data/perf.json"], workdir="/data")

            if exit_code != 0:
                logging.error(f"Failed to read performance file: {output.decode('utf-8')}")
                return None

            # Parse the performance data
            perf_data = json.loads(output.decode("utf-8"))
            performance = float(perf_data["perf"])
            logging.info(f"Successfully read performance data: {performance}")
            return performance

        except Exception as e:
            logging.error(f"Failed to read performance data: {str(e)}")
            return None

    def _create_error_response(self, container: Container | None, error: str) -> DockerRunResponse:
        """Create an error response"""
        logging.error(error)
        return DockerRunResponse(success=False, container_id=container.id if container else None, error=error)

    def _handle_container_error(self, container: Container | None, error: Exception) -> DockerRunResponse:
        """Handle container runtime errors"""
        error_msg = f"Error running container: {str(error)}"
        logging.error(error_msg)
        if container:
            logs = container.logs().decode("utf-8")
            logging.error(f"Container logs before error: {logs}")
        return self._create_error_response(container, error_msg)

    def _cleanup_container(self, container: Container | None) -> None:
        """Clean up container resources"""
        if container:
            try:
                container.remove(force=True)
            except Exception as e:
                logging.error(f"Error removing container: {str(e)}")
