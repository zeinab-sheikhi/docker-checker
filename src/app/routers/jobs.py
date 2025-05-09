from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.schemas.job import JobResponse
from app.services.docker_service import DockerService
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_job_service() -> JobService:
    """Dependency injection for JobService"""
    docker_service = DockerService()
    return JobService(docker_service)


job_service_dependency = Depends(get_job_service)


@router.post("/", response_model=JobResponse)
async def create_job(
    file: UploadFile,
    job_service: JobService = job_service_dependency,  # Use the module-level dependency
) -> Any:
    """
    Submit a dockerfile and create a new job.
    Returns a job ID and initial status.
    """
    try:
        job_id = await job_service.process_dockerfile(file)
        return await job_service.get_job_status(job_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing dockerfile: {str(e)}",
        ) from e


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    job_service: JobService = job_service_dependency,  # Use the same dependency
) -> Any:
    """
    Get job status and performance by ID.
    Returns current status, and performance value if job completed successfully.
    """
    try:
        job_status = await job_service.get_job_status(job_id)
        if not job_status:
            raise HTTPException(status_code=404, detail="Job not found")
        return job_status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving job status: {str(e)}",
        ) from e
