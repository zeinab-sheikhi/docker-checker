import os
import uuid
from typing import Dict, Optional
from fastapi import UploadFile
from app.schemas.job import JobResponse, JobStatus
from app.services.interfaces import DockerServiceInterface
from app.core.settings import settings


class JobService:
    """Service for handling job lifecycle"""
    
    def __init__(self, docker_service: DockerServiceInterface):
        """
        Initialize job service
        Args:
            docker_service: Service for Docker operations
        """
        self.docker_service = docker_service
        self.jobs: Dict[str, JobResponse] = {}
        self.storage_path = os.path.join(os.getcwd(), settings.storage_path)
        os.makedirs(self.storage_path, exist_ok=True)

    async def process_dockerfile(self, file: UploadFile) -> str:
        """
        Process uploaded Dockerfile through the workflow:
        1. Save Dockerfile
        2. Build image
        3. Run container and get performance
        Returns: job_id
        """
        # Create job
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = JobResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            performance=None
        )

        try:
            # Save Dockerfile
            dockerfile_path = await self._save_dockerfile(file, job_id)
            
            # Build image
            self.jobs[job_id].status = JobStatus.BUILDING
            build_result = self.docker_service.build_image(dockerfile_path)
            if not build_result.success:
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

        return job_id

    async def get_job_status(self, job_id: str) -> Optional[JobResponse]:
        """Get current status and performance of a job"""
        return self.jobs.get(job_id)

    async def _save_dockerfile(self, file: UploadFile, job_id: str) -> str:
        """Save Dockerfile to disk"""
        job_dir = os.path.join(self.storage_path, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        file_path = os.path.join(job_dir, "Dockerfile")
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        return job_dir  # Return directory containing Dockerfile 