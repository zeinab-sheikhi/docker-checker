import logging
import uuid

from fastapi import UploadFile

from docker_scanner.schemas.job import (
    JobResponse,
    JobStatus,
    VulnerabilitySeverityCount,
)
from docker_scanner.schemas.trivy import format_vulnerabilities
from docker_scanner.services.docker_service import DockerServiceInterface
from docker_scanner.services.redis_service import RedisService

logging.basicConfig(level=logging.INFO)


class JobService:
    """Service for handling job lifecycle"""

    def __init__(self, docker_service: DockerServiceInterface):
        """
        Initialize job service
        Args:
            docker_service: Service for Docker operations
        """
        self.docker_service = docker_service
        self.redis_service = RedisService()

    def check_dockerfile(self, file: UploadFile) -> str:
        """
        Validates the uploaded file as a Dockerfile and returns a job_id if valid.
        Raises ValueError if the file is not a valid Dockerfile.
        """
        try:
            content = file.file.read().decode("utf-8", errors="ignore")
            # Get all non-empty, non-comment lines
            lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
            if not lines or not lines[0].upper().startswith("FROM"):
                raise ValueError("The uploaded file is not a valid Dockerfile. The first instruction must be FROM.")
            job_id = str(uuid.uuid4())
            self.redis_service.save_job_data(job_id, {"dockerfile": content})
            return job_id
        finally:
            file.file.close()

    def scan_dockerfile(self, file: UploadFile) -> JobResponse:
        """
        Process uploaded Dockerfile:
        1. Build image from uploaded file
        2. Scan image for vulnerabilities
        3. If scan passes, run container and get performance from output
        Returns: JobResponse with status and performance
        """
        job_id = str(uuid.uuid4())
        try:
            # Build image
            image = self.docker_service.build_image(
                dockerfile=file.file,
                job_id=job_id,
            )
            logging.info(f"Job ID: {job_id}")
            logging.info(f"Image built: {image.image_id}")

            # Scan image with Trivy
            logging.info(f"Scanning image {image.image_id} for vulnerabilities")
            if image.image_id is not None:
                scan_result = self.docker_service.scan_image(image.image_id)
                vulnerabilities = VulnerabilitySeverityCount.summarize(scan_result.vulnerabilities)
                scan_report_str = format_vulnerabilities(scan_result.vulnerabilities)

                # Only run container if scan passes (is_safe)
                if not scan_result.is_safe:
                    logging.error(f"Image {image.image_id} is not safe to run. Skipping container execution.")
                    return JobResponse(
                        status=JobStatus.FAILED,
                        performance=None,
                        job_id=job_id,
                        scan_report=scan_report_str,
                        vulnerabilities=vulnerabilities,
                    )

                # Run container
                logging.info(f"Starting container run for image {image.image_id}")
                run_result = self.docker_service.run_container(image.image_id, job_id)

                return JobResponse(
                    status=JobStatus.SUCCESS,
                    performance=run_result.performance,
                    job_id=job_id,
                    scan_report=scan_report_str,
                    vulnerabilities=vulnerabilities,
                )

            return JobResponse(
                status=JobStatus.FAILED,
                performance=None,
                job_id=job_id,
                scan_report=None,
                vulnerabilities=None,
            )

        finally:
            file.file.close()
