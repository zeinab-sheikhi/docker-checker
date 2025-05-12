import json
import subprocess
from typing import BinaryIO, Protocol

import docker
from docker.models.containers import Container

from docker_scanner.logger import get_logger
from docker_scanner.schemas.docker import (
    DockerBuildImageResponse,
    DockerRunContainerResponse,
)
from docker_scanner.schemas.trivy import (
    ScanResult,
    TrivyReportModel,
    VulnerabilitySummary,
)
from docker_scanner.settings import settings

logger = get_logger()


class DockerServiceInterface(Protocol):
    """Interface for Docker operations"""

    def build_image(self, dockerfile: BinaryIO, job_id: str) -> DockerBuildImageResponse:
        """Build a Docker image from a Dockerfile."""
        ...

    def scan_image(self, image_id: str) -> ScanResult:
        """Scan a Docker image for vulnerabilities using Trivy."""
        ...

    def run_container(self, image_id: str, job_id: str) -> DockerRunContainerResponse:
        """Run a container from an image and process its output."""
        ...

    def cleanup_container(self, container: Container | None) -> None:
        """Clean up container resources"""
        ...


class DockerService(DockerServiceInterface):
    """
    Service for handling Docker operations.
    Manages container lifecycle, volume mounting, and data handling.
    """

    def __init__(self):
        """Initialize Docker client and setup workspace"""
        self.client = docker.from_env()
        self.timeout = settings.docker_timeout

    def build_image(self, dockerfile: BinaryIO, job_id: str) -> DockerBuildImageResponse:
        """
        Build a Docker image from a Dockerfile.

        Args:
            dockerfile (BinaryIO): A file-like object opened in binary mode containing the Dockerfile content.
            job_id (str): A unique identifier for the job, used to tag the built image.

        Returns:
            DockerBuildResponse: An object contains image id and tags.

        Raises:
            RuntimeError: If the Docker build fails for any reason.
        """
        try:
            logger.info(f"Building image for job {job_id}")
            image, _ = self.client.images.build(
                fileobj=dockerfile,
                tag=f"docker-check-{job_id}",
                rm=True,
                forcerm=True,
            )
            logger.info(f"Successfully built image with ID: {image.id}\n")
            return DockerBuildImageResponse(image_id=image.id, tags=image.tags)
        except (docker.errors.BuildError, docker.errors.APIError) as e:
            logger.error(f"Docker build failed: {str(e)}")
            raise ValueError(f"Docker build failed: {str(e)}") from e
        except TypeError as e:
            logger.error(f"Docker File Type Error: {str(e)}")
            raise ValueError(f"Docker File Type Error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Docker build failed: {str(e)}")
            raise RuntimeError(str(e)) from e

    def scan_image(self, image_id: str) -> ScanResult:
        """
        Scan a Docker image for vulnerabilities using Trivy.

        Args:
            image_id (str): The ID or tag of the Docker image to scan.

        Returns:
            ScanResult: An object containing a boolean `is_safe` (True if no HIGH/CRITICAL vulnerabilities)
                        and a list of all found vulnerabilities (as VulnerabilitySummary objects).

        Raises:
            ValueError: If image is not found, the scan fails, or the output is invalid.
            RuntimeError: For any other unexpected errors during the scan process.
        """
        cmd = ["trivy", "image", "--format", "json", "--severity", "HIGH,CRITICAL", image_id]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            report = TrivyReportModel(**data)
            vulnerabilities: list[VulnerabilitySummary] = []
            is_safe = True
            for scan_result in report.Results:
                if scan_result.Vulnerabilities:
                    for vuln in scan_result.Vulnerabilities:
                        vulnerabilities.append(VulnerabilitySummary(**vuln.model_dump()))
                        if vuln.Severity in ("HIGH", "CRITICAL"):
                            is_safe = False
            return ScanResult(is_safe=is_safe, vulnerabilities=vulnerabilities)

        except FileNotFoundError as e:
            logger.error("Trivy is not installed or not found in PATH.")
            raise ValueError(
                "Trivy is not installed or not found in PATH. Please install Trivy and ensure it is available in your system PATH."
            ) from e
        except subprocess.CalledProcessError as e:
            logger.error(f"Trivy scan failed: {e.stderr}")
            raise ValueError(f"Trivy scan failed: {e.stderr}") from e
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Trivy output as JSON.")
            raise ValueError("Failed to parse Trivy output as JSON.") from e
        except Exception as e:
            logger.error(f"Unexpected error during Trivy scan: {str(e)}")
            raise RuntimeError(f"Unexpected error during Trivy scan: {str(e)}") from e

    def run_container(self, image_id: str, job_id: str) -> DockerRunContainerResponse:
        """
        Run a container with a mounted volume and process its output
        Args:
            image_id: ID of the Docker image to run
            job_id: Unique identifier for this job
        Returns:
            DockerRunContainerResponse with image_id, container_id, status, performance, and data_path
        Raises:
            ValueError: For user errors (e.g., image not found, API error, container failed)
            RuntimeError: For unexpected server errors
        """
        container = None
        volume_name = f"job-data-{job_id}"
        try:
            # Create a Docker volume for this job
            logger.info(f"Creating volume {volume_name}")
            self.client.volumes.create(name=volume_name)

            # Configure volume for container
            volume_config = {volume_name: {"bind": "/data", "mode": "rw"}}
            # job_data_dir, volume_config = self._prepare_volume_and_job_dir(job_id)

            logger.info(f"Running container with image {image_id} for job {job_id}")
            logger.info(f"Volume config: {volume_config}")

            container = self.client.containers.run(
                image=image_id,
                detach=True,
                volumes=volume_config,  # Add this to ensure /data exists and is writable
            )
            # Wait for container to complete
            result = container.wait(timeout=self.timeout)
            exit_code = result.get("StatusCode")
            if exit_code != 0:
                raise ValueError(f"Container exited with non-zero status {exit_code}.")

            container.reload()  # Ensure status is up-to-date
            status = container.status if hasattr(container, "status") else "unknown"
            # self._copy_data_from_container(container, job_data_dir)
            # performance = self._read_performance_metric(job_data_dir)

            # Extract performance data from the volume
            performance = self._extract_performance_from_volume(volume_name)

            return DockerRunContainerResponse(
                image_id=image_id,
                container_id=container.id,
                status=status,
                performance=performance,
            )

        except docker.errors.ImageNotFound as e:
            logger.error(f"Docker image not found: {image_id}")
            raise ValueError(f"Docker image not found: {image_id}") from e
        except docker.errors.APIError as e:
            logger.error(f"Docker API error: {str(e)}")
            raise ValueError(f"Docker API error: {str(e)}") from e
        except docker.errors.ContainerError as e:
            logger.error(f"Container error: {str(e)}")
            raise RuntimeError(f"Docker container error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error in run_container: {str(e)}")
            raise RuntimeError(f"Unexpected error in run_container: {str(e)}") from e

    def _extract_performance_from_volume(self, volume_name: str) -> float | None:
        """
        Extract performance data from a Docker volume using a temporary container

        Args:
            volume_name: The name of the Docker volume containing the performance data

        Returns:
            The performance metric as a float if available, otherwise None
        """
        temp_container = None
        try:
            # Create a temporary container to access the volume
            temp_container = self.client.containers.create(
                "alpine:latest",
                command="cat /data/perf.json",
                volumes={
                    volume_name: {
                        "bind": "/data",
                        "mode": "ro",  # Read-only access
                    }
                },
            )

            # Start and wait for the container
            temp_container.start()
            exit_code = temp_container.wait()["StatusCode"]

            if exit_code != 0:
                logger.warning(f"Failed to read performance data, exit code: {exit_code}")
                return None

            # Get the logs (which will contain the file contents)
            logs = temp_container.logs().decode("utf-8").strip()

            if not logs:
                logger.warning("No performance data found")
                return None

            # Parse the JSON
            try:
                data = json.loads(logs)
                return data.get("perf")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in performance data: {logs}")
                return None

        except Exception as e:
            logger.error(f"Error extracting performance data: {str(e)}")
            return None
        finally:
            self.cleanup_container(temp_container)

    def cleanup_container(self, container: Container | None) -> None:
        """Clean up container resources"""
        if container:
            try:
                container.remove(force=True)
                logger.info(f"Container {container.id} removed successfully")
            except docker.errors.APIError as e:
                raise ValueError(f"Error removing container: {str(e)}") from e

    def cleanup_all_resources(self) -> None:
        """Clean up all Docker resources created by this service"""
        try:
            # Clean up all containers with our prefix
            containers = self.client.containers.list(all=True, filters={"name": "docker-check-"})
            for container in containers:
                try:
                    container.remove(force=True)
                    logger.info(f"Removed container: {container.id}")
                except Exception as e:
                    logger.error(f"Error removing container {container.id}: {e}")

            # Clean up all volumes with our prefix
            volumes = self.client.volumes.list(filters={"name": "job-data-"})
            for volume in volumes:
                try:
                    volume.remove(force=True)
                    logger.info(f"Removed volume: {volume.name}")
                except Exception as e:
                    logger.error(f"Error removing volume {volume.name}: {e}")

            logger.info("All Docker resources cleaned up")
        except Exception as e:
            logger.error(f"Error during Docker cleanup: {e}")
