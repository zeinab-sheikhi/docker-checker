import logging
import uuid

from fastapi import UploadFile

from app.schemas.job import JobResponse, JobStatus
from app.schemas.trivy import format_vulnerabilities
from app.services.docker_service import DockerServiceInterface

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

            # # Run container
            # logging.info(f"Starting container run for image {build_result.image_id}")
            # run_result = self.docker_service.run_container(build_result.image_id, job_id)
            # logging.info(f"Run result: {run_result}")

            # if not run_result.success:
            #     error_msg = run_result.error or "Unknown run error"
            #     logging.error(f"Container run failed: {error_msg}")
            #     return JobResponse(
            #         status=JobStatus.FAILED,
            #         message=error_msg,
            #         job_id=job_id,
            #         scan_report=scan_report_str,
            #     )

            return JobResponse(
                status=JobStatus.SUCCESS,
                performance=None,
                job_id=job_id,
                scan_report=scan_report_str,
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
