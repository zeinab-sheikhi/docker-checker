import uuid

from fastapi import UploadFile

from app.schemas.job import JobResponse, JobStatus
from app.services.docker_service import DockerServiceInterface


class JobService:
    """Service for handling job lifecycle"""

    def __init__(self, docker_service: DockerServiceInterface):
        """
        Initialize job service
        Args:
            docker_service: Service for Docker operations
        """
        self.docker_service = docker_service
        self.jobs: dict[str, JobResponse] = {}

    def process_dockerfile(self, file: UploadFile) -> str:
        """
        Process uploaded Dockerfile through the workflow:
        1. Build image from uploaded file
        2. Run container and get performance
        Returns: job_id
        """
        # Create job
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = JobResponse(job_id=job_id, status=JobStatus.PENDING, performance=None)

        try:
            # Build image
            self.jobs[job_id].status = JobStatus.BUILDING
            build_result = self.docker_service.build_image(dockerfile=file.file, job_id=job_id)

            if not build_result.success or not build_result.image_id:
                self.jobs[job_id].status = JobStatus.FAILED
                self.jobs[job_id].message = build_result.error
                return job_id

            # Run container
            self.jobs[job_id].status = JobStatus.RUNNING
            run_result = self.docker_service.run_container_with_volume(build_result.image_id)

            if run_result.success and run_result.performance is not None:
                self.jobs[job_id].status = JobStatus.SUCCESS
                self.jobs[job_id].performance = run_result.performance
            else:
                self.jobs[job_id].status = JobStatus.FAILED
                self.jobs[job_id].message = run_result.error

            # Cleanup
            if build_result.image_id:
                self.docker_service.cleanup_image(build_result.image_id)

        except Exception as e:
            self.jobs[job_id].status = JobStatus.FAILED
            self.jobs[job_id].message = str(e)
        finally:
            # Clean up the BytesIO object
            file.file.close()

        return job_id

    async def get_job_status(self, job_id: str) -> JobResponse | None:
        """Get current status and performance of a job"""
        return self.jobs.get(job_id)
