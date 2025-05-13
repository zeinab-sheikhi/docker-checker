import io
import os
import uuid

from fastapi import UploadFile

from docker_scanner.logger import get_logger
from docker_scanner.schemas.job_status import JobStatusResponse, StepStatus
from docker_scanner.services.docker_service import DockerServiceInterface
from docker_scanner.services.redis_service import RedisService

logger = get_logger()


class JobService:
    """Service for handling job lifecycle"""

    def __init__(self, docker_service: DockerServiceInterface, redis_service: RedisService):
        """
        Initialize job service
        Args:
            docker_service: Service for Docker operations
            redis_service: Service for Redis
        """
        self.docker_service = docker_service
        self.redis_service = redis_service

    def create_job(self, file: UploadFile) -> str:
        """
        Validates the uploaded file as a Dockerfile and returns a job_id if valid.
        Raises ValueError if the file is not a valid Dockerfile.
        """
        try:
            # Check filename and extension
            filename = file.filename
            if filename and os.path.splitext(filename)[1]:  # Check if file has any extension
                raise ValueError("Not a Dockerfile.")

            content = file.file.read().decode("utf-8", errors="ignore")
            # Get non-empty and non-comment lines
            lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]

            # Check if file is empty
            if not lines:
                raise ValueError("The uploaded file is empty or contains only comments.")

            valid_docker_instructions = {"FROM", "RUN", "CMD", "COPY", "ADD", "ENTRYPOINT", "WORKDIR", "EXPOSE", "ENV"}
            matched_instructions = []

            for line in lines:
                first_token = line.split()[0].upper()
                if first_token in valid_docker_instructions:
                    matched_instructions.append(first_token)

            # Ensure "FROM" is present and at least one more instruction
            if "FROM" not in matched_instructions:
                raise ValueError("The uploaded file is not a valid Dockerfile. Missing FROM instruction.")
            if len(matched_instructions) < 2:
                raise ValueError("The uploaded file is not a valid Dockerfile. Too few valid instructions.")

            job_id = str(uuid.uuid4())
            self.redis_service.update_job_data(job_id, {"dockerfile": content})
            return job_id

        finally:
            file.file.close()

    def get_job_status(self, job_id: str) -> JobStatusResponse:
        """
        Get the status of a job by job_id

        Args:
            job_id: The unique identifier of the job

        Returns:
            JobStatusResponse containing all job information

        Raises:
            ValueError: If job_id is not found or data is invalid
        """
        # Get data from Redis
        data = self.redis_service.get_job_data(job_id)

        # If job exists in Redis, return its current status
        if data is not None and "dockerfile" in data:
            return JobStatusResponse(**data)
        
        if data is None or "dockerfile" not in data:
            raise ValueError(f"Job ID {job_id} not found")
        

        dockerfile = data["dockerfile"]
        response = JobStatusResponse(
            job_id=job_id,
            dockerfile=dockerfile,
            build_status=StepStatus.SKIPPED,
            scan_status=StepStatus.SKIPPED,
            run_status=StepStatus.SKIPPED,
        )

        try:
            # Step 1: Build Image
            try:
                image = self.docker_service.build_image(
                    dockerfile=io.BytesIO(dockerfile.encode("utf-8")),
                    job_id=job_id,
                )
                response.build_status = StepStatus.SUCCESS
                response.image_id = image.image_id
            except Exception as e:
                response.build_status = StepStatus.FAILED
                response.error = f"Build failed: {str(e)}"
                return response

            # Step 2: Scan Image
            try:
                scan_result = self.docker_service.scan_image(image.image_id)  # type: ignore[arg-type]
                response.scan_status = StepStatus.SUCCESS
                response.is_safe = scan_result.is_safe
                response.vulnerabilities = scan_result.vulnerabilities
            except Exception as e:
                response.scan_status = StepStatus.FAILED
                response.error = f"Scan failed: {str(e)}"
                return response

            # Step 3: Run Container (only if image is safe)
            if scan_result.is_safe:
                try:
                    run_result = self.docker_service.run_container(image.image_id, job_id)  # type: ignore[arg-type]
                    logger.info(f"Run result: {run_result}")
                    response.run_status = StepStatus.SUCCESS
                    response.performance = run_result.performance
                except Exception as e:
                    response.run_status = StepStatus.FAILED
                    response.error = f"Run failed: {str(e)}"
            return response

        except Exception as e:
            # This catch-all is for any unexpected errors
            response.error = f"Unexpected error: {str(e)}"
            return response
