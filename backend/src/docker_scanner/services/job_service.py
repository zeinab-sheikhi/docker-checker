import logging
import uuid

from fastapi import UploadFile

from docker_scanner.schemas.job import JobResponse, JobStatus
from docker_scanner.schemas.trivy import format_vulnerabilities
from docker_scanner.services.docker_service import DockerServiceInterface

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

    def process_dockerfile(self, file: UploadFile) -> JobResponse:
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

            # Scan image with Trivy
            logging.info(f"Scanning image {image.image_id} for vulnerabilities")
            if image.image_id is not None:
                scan_result = self.docker_service.scan_image(image.image_id)
                scan_report_str = format_vulnerabilities(scan_result.vulnerabilities)

                # Only run container if scan passes (is_safe)
                if not scan_result.is_safe:
                    logging.error(f"Image {image.image_id} is not safe to run. Skipping container execution.")
                    return JobResponse(
                        status=JobStatus.FAILED,
                        performance=None,
                        job_id=job_id,
                        scan_report=scan_report_str,
                    )

                # Run container
                logging.info(f"Starting container run for image {image.image_id}")
                run_result = self.docker_service.run_container(image.image_id, job_id)

                return JobResponse(
                    status=JobStatus.SUCCESS,
                    performance=run_result.performance,
                    job_id=job_id,
                    scan_report=scan_report_str,
                )

            return JobResponse(
                status=JobStatus.FAILED,
                performance=None,
                job_id=job_id,
                scan_report=None,
            )

        finally:
            file.file.close()

    async def get_job_status(self, job_id: str) -> JobResponse:
        """
        This method doesn't make sense without a database
        We should either remove it or implement proper database storage
        """
        raise NotImplementedError(
            "Job status tracking requires a database. This method should not be used until database support is added."
        )
