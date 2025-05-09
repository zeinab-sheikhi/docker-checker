# main.py
from fastapi import FastAPI, UploadFile, HTTPException
from api.models import DockerfileUploadResponse, JobStatus, ErrorResponse
import uuid
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post(
    "/upload-dockerfile/",
    response_model=DockerfileUploadResponse,
    responses={400: {"model": ErrorResponse}}
)
async def upload_dockerfile(file: UploadFile):
    """
    Upload a Dockerfile
    Returns error response for invalid files
    Only generates job_id for valid Dockerfiles
    """
    try:
        # Basic validation
        if not file.filename:
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    success=False,
                    message="No file provided"
                ).model_dump()
            )

        # Check if it's a Dockerfile
        if file.filename.lower() not in ['dockerfile', 'dockerfile.txt']:
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    success=False,
                    message="File must be named 'Dockerfile' or 'Dockerfile.txt'"
                ).model_dump()
            )

        # Read file content
        content = await file.read()
        
        # Validate content
        try:
            content_str = content.decode('utf-8')
            if 'FROM' not in content_str:
                return JSONResponse(
                    status_code=400,
                    content=ErrorResponse(
                        success=False,
                        message="Invalid Dockerfile: missing FROM instruction"
                    ).model_dump()
                )
        except UnicodeDecodeError:
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    success=False,
                    message="File is not a valid text file"
                ).model_dump()
            )

        # Only create job_id for valid Dockerfiles
        return DockerfileUploadResponse(
            job_id=str(uuid.uuid4()),
            status=JobStatus.PENDING,
            message="Dockerfile uploaded successfully"
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                message=f"Internal server error: {str(e)}"
            ).model_dump()
        )