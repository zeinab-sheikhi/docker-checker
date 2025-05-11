import io
import logging
import uuid

from fastapi import UploadFile

from docker_scanner.schemas.job_status import (
    BuildImageResult,
    JobStatus,
    JobStatusResponse,
    RunContainerResult,
    ScanImageResult,
)
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

    def create_job(self, file: UploadFile) -> str:
        """
        Validates the uploaded file as a Dockerfile and returns a job_id if valid.
        Raises ValueError if the file is not a valid Dockerfile.
        """
        try:
            content = file.file.read().decode("utf-8", errors="ignore")
            # Get non-empty and non-comment lines
            lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]

            # Check if file is empty
            if not lines:
                raise ValueError("The uploaded file is empty or contains only comments.")

            # List of common Dockerfile instructions
            dockerfile_instructions = [
                "FROM",
                "RUN",
                "CMD",
                "LABEL",
                "EXPOSE",
                "ENV",
                "ADD",
                "COPY",
                "ENTRYPOINT",
                "VOLUME",
                "USER",
                "WORKDIR",
                "ARG",
                "ONBUILD",
                "STOPSIGNAL",
                "HEALTHCHECK",
                "SHELL",
            ]

            # Check if any line starts with a valid Dockerfile instruction
            valid_instructions = [
                line.upper().split()[0]
                for line in lines
                if any(line.upper().startswith(instruction) for instruction in dockerfile_instructions)
            ]

            # Must have at least FROM and one other instruction
            if not valid_instructions:
                raise ValueError("The uploaded file is not a valid Dockerfile. No valid Dockerfile instructions found.")

            if "FROM" not in list(valid_instructions):
                raise ValueError("The uploaded file is not a valid Dockerfile. Missing FROM instruction.")

            job_id = str(uuid.uuid4())
            self.redis_service.update_job_data(job_id, {"dockerfile": content})
            return job_id
        finally:
            file.file.close()

    def build_image(self, job_id: str):
        try:
            # 1. Update status to BUILDING
            self.redis_service.update_job_data(job_id, {"status": "building"})
            # 2. Build image
            job_data = self.redis_service.get_job_data(job_id)
            if job_data is None:
                raise ValueError(f"No job data found for job_id: {job_id}")

            dockerfile = job_data["dockerfile"]
            image = self.docker_service.build_image(
                dockerfile=io.BytesIO(dockerfile.encode("utf-8")),
                job_id=job_id,
            )
            build_succeed_result = BuildImageResult(
                success=True,
                image_id=image.image_id,
                error=None,
            )
            self.redis_service.update_job_data(job_id, {"build_result": build_succeed_result.model_dump()})

        except Exception as e:
            build_failed_result = BuildImageResult(
                success=False,
                image_id=None,
                error=str(e),
            )
            self.redis_service.update_job_data(
                job_id, {"status": "failed", "build_result": build_failed_result.model_dump()}
            )

    def scan_image(self, job_id: str):
        try:
            # 1. Update status to SCANNING
            self.redis_service.update_job_data(job_id, {"status": "scanning"})
            # 2. Get job data
            job_data = self.redis_service.get_job_data(job_id)
            if job_data is None:
                raise ValueError(f"No job data found for job_id: {job_id}")

            build_result = job_data.get("build_result")
            if build_result is None:
                raise ValueError(f"No build result found for job_id: {job_id}")

            image_id = build_result.get("image_id")
            if image_id is None:
                raise ValueError(f"No image_id found in build result for job_id: {job_id}")

            # 3. Scan image
            scan_result = self.docker_service.scan_image(image_id)
            scan_succeed_result = ScanImageResult(
                success=True,
                is_safe=scan_result.is_safe,
                vulnerabilities=scan_result.vulnerabilities,
                error=None,
            )
            self.redis_service.update_job_data(job_id, {"scan_result": scan_succeed_result.model_dump()})
        except Exception as e:
            scan_failed_result = ScanImageResult(
                success=False,
                is_safe=None,
                vulnerabilities=None,
                error=str(e),
            )
            self.redis_service.update_job_data(
                job_id, {"status": "failed", "scan_result": scan_failed_result.model_dump()}
            )

    def run_container(self, job_id: str):
        try:
            # 1. Update status to RUNNING
            self.redis_service.update_job_data(job_id, {"status": "running"})
            # 2. Get job data
            job_data = self.redis_service.get_job_data(job_id)
            if job_data is None:
                raise ValueError(f"No job data found for job_id: {job_id}")

            build_result = job_data.get("build_result")
            if build_result is None:
                raise ValueError(f"No build result found for job_id: {job_id}")

            image_id = build_result.get("image_id")
            if image_id is None:
                raise ValueError(f"No image_id found in build result for job_id: {job_id}")

            # 3. Run container
            run_result = self.docker_service.run_container(image_id, job_id)
            run_succeed_result = RunContainerResult(
                success=True,
                performance=run_result.performance,
                error=None,
            )
            self.redis_service.update_job_data(job_id, {"run_result": run_succeed_result.model_dump()})
        except Exception as e:
            run_failed_result = RunContainerResult(
                success=False,
                performance=None,
                error=str(e),
            )
            self.redis_service.update_job_data(
                job_id, {"status": "failed", "run_result": run_failed_result.model_dump()}
            )

    def process_job(self, job_id: str):
        try:
            # Initialize job status
            self.redis_service.update_job_data(job_id, {"status": JobStatus.PENDING})

            # Step 1: Build Image
            self.build_image(job_id)
            job_data = self.redis_service.get_job_data(job_id)
            if job_data is None:
                raise ValueError(f"No job data found for job_id: {job_id}")

            build_result = job_data.get("build_result", {})
            if not build_result.get("success"):
                return

            # Step 2: Scan Image
            self.scan_image(job_id)
            job_data = self.redis_service.get_job_data(job_id)
            if job_data is None:
                raise ValueError(f"No job data found for job_id: {job_id}")

            scan_result = job_data.get("scan_result", {})
            if not scan_result.get("success"):
                return

            if not scan_result.get("is_safe"):
                self.redis_service.update_job_data(job_id, {"status": JobStatus.FAILED})
                return

            # Step 3: Run Container
            self.run_container(job_id)
            job_data = self.redis_service.get_job_data(job_id)
            if job_data is None:
                raise ValueError(f"No job data found for job_id: {job_id}")

            run_result = job_data.get("run_result", {})

            # Update final status
            final_status = JobStatus.SUCCESS if run_result.get("success") else JobStatus.FAILED
            self.redis_service.update_job_data(job_id, {"status": final_status})

        except Exception as e:
            self.redis_service.update_job_data(job_id, {"status": JobStatus.FAILED, "error": str(e)})

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
        if data is None or "dockerfile" not in data:
            raise ValueError(f"Job ID {job_id} not found")

        # Get status, defaulting to PENDING if not set
        status = data.get("status", JobStatus.PENDING)

        # Convert status string to JobStatus enum if it's a string
        if isinstance(status, str):
            status = JobStatus(status)

        # Create response object with all available data
        response = JobStatusResponse(
            job_id=job_id,
            status=status,
            error=data.get("error"),
            dockerfile=data.get("dockerfile"),
            build_result=BuildImageResult(**data["build_result"]) if "build_result" in data else None,
            scan_result=ScanImageResult(**data["scan_result"]) if "scan_result" in data else None,
            run_result=RunContainerResult(**data["run_result"]) if "run_result" in data else None,
        )

        return response
