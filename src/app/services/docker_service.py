import logging
from typing import BinaryIO, Protocol

import docker

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
        """
        Run container and capture its output
        Args:
            image_id: ID of the Docker image to run
        Returns:
            DockerRunResponse with status and performance data
        """
        container = None
        try:
            logging.info(f"Running container with image {image_id}")
            # Run container and wait for it to complete
            container = self.client.containers.run(
                image=image_id,
                detach=True,
            )

            # Wait for container to finish
            result = container.wait(timeout=self.timeout)
            logs = container.logs().decode("utf-8").strip()
            logging.info(f"Container logs: {logs}")

            if result["StatusCode"] != 0:
                error_msg = f"Container exited with status {result['StatusCode']}. Logs: {logs}"
                logging.error(error_msg)
                return DockerRunResponse(success=False, container_id=container.id, error=error_msg)

            try:
                # Parse the output as JSON and extract performance
                import json

                perf_data = json.loads(logs)
                performance = float(perf_data["perf"])
                logging.info(f"Successfully parsed performance: {performance}")

                return DockerRunResponse(success=True, container_id=container.id, performance=performance)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                error_msg = f"Failed to parse container output as JSON: {str(e)}"
                logging.error(error_msg)
                return DockerRunResponse(success=False, container_id=container.id, error=error_msg)

        except Exception as e:
            error_msg = f"Error running container: {str(e)}"
            logging.error(error_msg)
            if container:
                logs = container.logs().decode("utf-8")
                logging.error(f"Container logs before error: {logs}")
            return DockerRunResponse(success=False, container_id=container.id if container else None, error=error_msg)
        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception as e:
                    logging.error(f"Error removing container: {str(e)}")
