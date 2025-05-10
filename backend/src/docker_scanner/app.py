from docker_checker.routers.jobs import router as jobs_router
from docker_checker.settings import settings
from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse

app = FastAPI(**settings.get_app_kwargs())

app.include_router(jobs_router, prefix=settings.app_config.api_prefix)


@app.get("/")
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(content={"message": "API is running."}, status_code=200)
