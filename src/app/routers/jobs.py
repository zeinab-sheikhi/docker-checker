from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

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
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from err
