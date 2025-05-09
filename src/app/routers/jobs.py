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
    job_service: JobService = job_service_dependency,
) -> JobResponse:
    """
    Submit a dockerfile and create a new job.
    Returns the job status and performance if successful.
    """
    try:
        return job_service.process_dockerfile(file)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing dockerfile: {str(e)}",
        ) from e
