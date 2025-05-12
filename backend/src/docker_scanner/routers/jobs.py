from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse

from docker_scanner.schemas.job_status import ErrorResponse, JobStatusResponse
from docker_scanner.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


# Dependency to get JobService from app state
def get_job_service(request: Request) -> JobService:
    """Get the app-level JobService instance"""
    return request.app.state.job_service


# Use the dependency
job_service_dependency = Depends(get_job_service)


job_service_dependency = Depends(get_job_service)


@router.post(
    "/",
    response_model=None,
    responses={
        200: {"model": dict, "description": "Job ID returned"},
        400: {"model": ErrorResponse, "description": "Invalid Dockerfile"},
    },
)
async def create_job(
    file: UploadFile,
    job_service: JobService = job_service_dependency,
):
    """
    Submit a Dockerfile and get a job ID if valid.
    Starts processing the job in the background.
    """
    try:
        job_id = job_service.create_job(file)
        return JSONResponse(status_code=200, content={"job_id": job_id})
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from err


@router.get(
    "/status/{job_id}",
    response_model=JobStatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def check_job_status(
    job_id: str,
    job_service: JobService = job_service_dependency,
) -> JobStatusResponse:
    """
    Retrieve the status and performance of a job by job_id.
    """
    try:
        return job_service.get_job_status(job_id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)) from err
