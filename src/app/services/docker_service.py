import json
import logging
from pathlib import Path
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

    def run_container(self, image_id: str, job_id: str) -> DockerRunResponse:
        """Run a container and get its output"""
        ...


class DockerService(DockerServiceInterface):
    """Service for handling Docker operations"""

    def __init__(self):
        """Initialize Docker client"""
        self.client = docker.from_env()
        self.timeout = settings.docker_timeout
        # Create tmp directory if it doesn't exist
        self.tmp_dir = Path("tmp")
        self.tmp_dir.mkdir(exist_ok=True)

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

    def run_container(self, image_id: str, job_id: str) -> DockerRunResponse:
        """
        Run a container with a mounted volume and process its output
        Args:
            image_id: ID of the Docker image to run
            job_id: Unique identifier for this job
        Returns:
            DockerRunResponse with status and container info
        """
        container = None
        try:
            # Create a unique directory for this job
            job_data_dir = self.tmp_dir / "data" / job_id
            job_data_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"Created job directory: {job_data_dir}")

            # Start container with mounted volume
            container = self._start_container(image_id, job_data_dir)

            # Wait for container to finish
            exit_status, logs = self._wait_for_container(container)

            # Log the container output
            for line in logs.split("\n"):
                logging.info(f"Container output: {line}")

            if exit_status != 0:
                return self._create_error_response(
                    container, f"Container exited with status {exit_status}. Logs: {logs}"
                )

            # Check if files were created in the job's directory
            if not job_data_dir.exists() or not any(job_data_dir.iterdir()):
                return self._create_error_response(container, f"No data was written to the job directory {job_id}")

            # Log the contents of the job's directory
            logging.info(f"Files in job directory {job_id}:")
            for file_path in job_data_dir.iterdir():
                logging.info(f"  {file_path.name}")

            return DockerRunResponse(
                success=True,
                container_id=container.id,
                performance=None,  # We're not reading performance data at this stage
            )

        except Exception as e:
            return self._handle_container_error(container, e)
        finally:
            self._cleanup_container(container)

    def _start_container(self, image_id: str, job_data_dir: Path) -> Container:
        """
        Start a container with the given image ID and mount volume
        Args:
            image_id: ID of the Docker image to run
            job_data_dir: Path to the job's data directory
        Returns:
            Container instance
        """
        logging.info(f"Starting container with image {image_id}")

        # Convert to absolute path for Docker
        host_path = str(job_data_dir.absolute())
        logging.info(f"Mounting host directory {host_path} to container /data")

        return self.client.containers.run(
            image=image_id, detach=True, volumes={host_path: {"bind": "/data", "mode": "rw"}}
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
