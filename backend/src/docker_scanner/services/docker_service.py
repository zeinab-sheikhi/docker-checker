import io
import json
import logging
import subprocess
import tarfile
from pathlib import Path
from typing import BinaryIO, Protocol

import docker
from docker.models.containers import Container
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
        self._setup_volume_directory()

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
            logging.info(f"Building image for job {job_id}")
            image, _ = self.client.images.build(
                fileobj=dockerfile,
                tag=f"docker-check-{job_id}",
                rm=True,
                forcerm=True,
            )
            logging.info(f"Successfully built image with ID: {image.id}\n")
            return DockerBuildImageResponse(image_id=image.id, tags=image.tags)
        except (docker.errors.BuildError, docker.errors.APIError) as e:
            logging.error(f"Docker build failed: {str(e)}")
            raise ValueError(f"Docker build failed: {str(e)}") from e
        except TypeError as e:
            logging.error(f"Docker File Type Error: {str(e)}")
            raise ValueError(f"Docker File Type Error: {str(e)}") from e
        except Exception as e:
            logging.error(f"Docker build failed: {str(e)}")
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
            logging.error("Trivy is not installed or not found in PATH.")
            raise ValueError(
                "Trivy is not installed or not found in PATH. Please install Trivy and ensure it is available in your system PATH."
            ) from e
        except subprocess.CalledProcessError as e:
            logging.error(f"Trivy scan failed: {e.stderr}")
            raise ValueError(f"Trivy scan failed: {e.stderr}") from e
        except json.JSONDecodeError as e:
            logging.error("Failed to parse Trivy output as JSON.")
            raise ValueError("Failed to parse Trivy output as JSON.") from e
        except Exception as e:
            logging.error(f"Unexpected error during Trivy scan: {str(e)}")
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
        try:
            job_data_dir, volume_config = self._prepare_volume_and_job_dir(job_id)
            container = self.client.containers.run(image=image_id, detach=True, volumes=volume_config)
            result = container.wait(timeout=self.timeout)
            exit_code = result.get("StatusCode")
            if exit_code != 0:
                raise ValueError(f"Container exited with non-zero status {exit_code}.")
            container.reload()  # Ensure status is up-to-date
            status = container.status if hasattr(container, "status") else "unknown"
            self._copy_data_from_container(container, job_data_dir)
            performance = self._read_performance_metric(job_data_dir)
            return DockerRunContainerResponse(
                image_id=image_id,
                container_id=container.id,
                status=status,
                performance=performance,
            )

        except docker.errors.ImageNotFound as e:
            logging.error(f"Docker image not found: {image_id}")
            raise ValueError(f"Docker image not found: {image_id}") from e
        except docker.errors.APIError as e:
            logging.error(f"Docker API error: {str(e)}")
            raise ValueError(f"Docker API error: {str(e)}") from e
        except docker.errors.ContainerError as e:
            logging.error(f"Container error: {str(e)}")
            raise RuntimeError(f"Docker container error: {str(e)}") from e
        except Exception as e:
            logging.error(f"Unexpected error in run_container: {str(e)}")
            raise RuntimeError(f"Unexpected error in run_container: {str(e)}") from e
        finally:
            if container:
                self.cleanup_container(container)

    def _copy_data_from_container(
        self, container: Container, host_data_dir: Path, container_data_path: str = "/data"
    ) -> None:
        """
        Copy the contents of the container's /data directory to the host job data directory.
        Args:
            container: The Docker container object
            host_data_dir: The Path object for the host's job data directory
            container_data_path: The path inside the container to copy (default: /data)
        """
        try:
            bits, stat = container.get_archive(container_data_path)
            file_like = io.BytesIO(b"".join(bits))
            with tarfile.open(fileobj=file_like) as tar:
                tar.extractall(path=host_data_dir)
            logging.info(f"Copied data from container {container.id} to {host_data_dir}")
        except Exception as e:
            logging.warning(f"Failed to copy data from container: {e}")

    def _read_performance_metric(self, job_data_dir: Path) -> float | None:
        """
        Read the performance metric from perf.json in the job data directory.
        Args:
            job_data_dir: The Path object for the host's job data directory
        Returns:
            The performance metric as a float if available, otherwise None.
        """
        perf_file = job_data_dir / "perf.json"
        if perf_file.exists():
            try:
                with open(perf_file) as f:
                    perf_data = json.load(f)
                    return perf_data.get("perf")
            except Exception as e:
                logging.warning(f"Failed to read performance metric: {e}")
        return None

    def cleanup_container(self, container: Container | None) -> None:
        """Clean up container resources"""
        if container:
            try:
                container.remove(force=True)
                logging.info("Container removed successfully")
            except docker.errors.APIError as e:
                raise ValueError(f"Error removing container: {str(e)}") from e

    def _setup_volume_directory(self) -> None:
        """Setup volume directory"""
        settings.volume_base_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Initialized volume base path: {settings.volume_base_path}")

    def _prepare_volume_and_job_dir(self, job_id: str) -> tuple[Path, dict]:
        """
        Prepare the job-specific directory and return the volume config for Docker.
        Returns:
            (job_data_dir, volume_config)
        """
        job_data_dir = settings.get_job_volume_path(job_id)
        job_data_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created job directory: {job_data_dir}")

        volume_config = {
            str(job_data_dir.absolute()): {
                "bind": settings.volume_container_path,
                "mode": settings.volume_mode,
            }
        }
        return job_data_dir, volume_config
