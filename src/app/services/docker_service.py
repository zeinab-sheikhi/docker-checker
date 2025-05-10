import json
import logging
import subprocess
from pathlib import Path
from typing import BinaryIO, Protocol

import docker
from docker.models.containers import Container

from app.schemas.docker import DockerBuildResponse, DockerRunResponse
from app.schemas.trivy import ScanResult, TrivyReportModel, VulnerabilitySummary
from app.settings import settings


class DockerServiceInterface(Protocol):
    """Interface for Docker operations"""

    def build_image(self, dockerfile: BinaryIO, job_id: str) -> DockerBuildResponse:
        """Build a Docker image"""
        ...

    def run_container(self, image_id: str, job_id: str) -> DockerRunResponse:
        """Run a container and get its output"""
        ...

    def scan_image_with_trivy(self, image_id: str) -> ScanResult:
        """Scan a Docker image using Trivy and return the parsed result."""
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
        self._setup_workspace()

    # Public methods (API)
    # ------------------

    def build_image(self, dockerfile: BinaryIO, job_id: str) -> DockerBuildResponse:
        """
        Build a Docker image from a dockerfile
        Args:
            dockerfile: File object containing Dockerfile content
            job_id: Unique identifier for this job
        Returns:
            DockerBuildResponse indicating build success/failure
        """
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
            # Prepare job directory and start container
            job_data_dir = self._prepare_job_directory(job_id)
            container = self._start_container(image_id, job_data_dir)

            # Process container execution
            return self._process_container_execution(container, job_id, job_data_dir)
        except Exception as e:
            return self._handle_container_error(container, e)
        finally:
            self._cleanup_container(container)

    # Container lifecycle methods
    # -------------------------

    def _start_container(self, image_id: str, job_data_dir: Path) -> Container:
        """Start a container with volume mounted"""
        logging.info(f"Starting container with image {image_id}")

        volume_config = {
            str(job_data_dir.absolute()): {"bind": settings.volume_container_path, "mode": settings.volume_mode}
        }

        logging.info(
            f"Mounting host directory {job_data_dir} to container "
            f"{settings.volume_container_path} in mode {settings.volume_mode}"
        )

        return self.client.containers.run(image=image_id, detach=True, volumes=volume_config)

    def _wait_for_container(self, container: Container) -> tuple[int, str]:
        """Wait for container completion and get logs"""
        result = container.wait(timeout=self.timeout)
        logs = container.logs().decode("utf-8").strip()
        self._log_container_output(logs)
        return result["StatusCode"], logs

    def _cleanup_container(self, container: Container | None) -> None:
        """Clean up container resources"""
        if container:
            try:
                container.remove(force=True)
                logging.info("Container removed successfully")
            except Exception as e:
                logging.error(f"Error removing container: {str(e)}")

    # Data handling methods
    # -------------------

    def _setup_workspace(self) -> None:
        """Setup workspace directories"""
        settings.volume_base_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Initialized volume base path: {settings.volume_base_path}")

    def _prepare_job_directory(self, job_id: str) -> Path:
        """Create and prepare job-specific directory"""
        job_data_dir = settings.get_job_volume_path(job_id)
        job_data_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created job directory: {job_data_dir}")
        return job_data_dir

    def _verify_job_data(self, job_data_dir: Path, job_id: str) -> bool:
        """Verify data was written to job directory"""
        if not job_data_dir.exists() or not any(job_data_dir.iterdir()):
            logging.error(f"No data written to job directory {job_id}")
            return False

        logging.info(f"Files in job directory {job_id}:")
        for file_path in job_data_dir.iterdir():
            logging.info(f"  {file_path.name}")
        return True

    # Helper methods
    # -------------

    def _process_container_execution(self, container: Container, job_id: str, job_data_dir: Path) -> DockerRunResponse:
        """Process container execution and verify results"""
        exit_status, logs = self._wait_for_container(container)

        if exit_status != 0:
            return self._create_error_response(container, f"Container exited with status {exit_status}. Logs: {logs}")

        if not self._verify_job_data(job_data_dir, job_id):
            return self._create_error_response(container, f"No data was written to the job directory {job_id}")

        return DockerRunResponse(
            success=True,
            container_id=container.id,
            performance=None,  # We're not reading performance data at this stage
        )

    def _create_error_response(self, container: Container | None, error: str) -> DockerRunResponse:
        """Create standardized error response"""
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

    def _log_container_output(self, logs: str) -> None:
        """Log container output in a consistent format"""
        for line in logs.split("\n"):
            logging.info(f"Container output: {line}")

    def scan_image_with_trivy(self, image_id: str) -> ScanResult:
        """
        Scan a Docker image using Trivy and return the parsed result.
        """
        cmd = ["trivy", "image", "--format", "json", "--severity", "HIGH,CRITICAL", image_id]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            report = TrivyReportModel(**data)
            vulnerabilities: list[VulnerabilitySummary] = []
            is_safe = True
            for result in report.Results:
                if result.Vulnerabilities:
                    for vuln in result.Vulnerabilities:
                        vulnerabilities.append(
                            VulnerabilitySummary(
                                package=vuln.PkgName,
                                vulnerability_id=vuln.VulnerabilityID,
                                severity=vuln.Severity,
                                title=vuln.Title,
                                description=vuln.Description,
                                fixed_version=vuln.FixedVersion,
                            )
                        )
                        if vuln.Severity in ("HIGH", "CRITICAL"):
                            is_safe = False
            return ScanResult(is_safe=is_safe, vulnerabilities=vulnerabilities)

        except subprocess.CalledProcessError as e:
            logging.error(f"Trivy scan failed: {e.stderr}")
            raise
        except json.JSONDecodeError:
            logging.error("Failed to parse Trivy output as JSON.")
            raise
