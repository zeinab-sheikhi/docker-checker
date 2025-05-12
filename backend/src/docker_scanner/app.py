from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from docker_scanner.logger import get_logger
from docker_scanner.routers.jobs import router as jobs_router
from docker_scanner.services.docker_service import DockerService
from docker_scanner.services.job_service import JobService
from docker_scanner.services.redis_service import RedisService
from docker_scanner.settings import settings

logger = get_logger()

app = FastAPI(**settings.get_app_kwargs())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize application services"""
    logger.info("Application starting up, initializing services")

    # Initialize Redis service
    app.state.redis_service = RedisService(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)

    # Initialize Docker service
    app.state.docker_service = DockerService()

    # Initialize Job service with the other services
    app.state.job_service = JobService(app.state.docker_service, app.state.redis_service)

    logger.info("All services initialized successfully")


@app.on_event("shutdown")
def shutdown_event():
    """Clean up application resources"""

    logger.info("Application shutting down, cleaning up resources")

    if hasattr(app.state, "redis_service"):
        try:
            app.state.redis_service.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")

    if hasattr(app.state, "docker_service"):
        try:
            app.state.docker_service.cleanup_all_resources()
            logger.info("Docker resources cleaned up")
        except Exception as e:
            logger.error(f"Error in cleaning up Docker resources: {e}")

    logger.info("Cleanup complete")


app.include_router(jobs_router, prefix=settings.app_config.api_prefix)


@app.get("/")
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(content={"message": "API is running."}, status_code=200)
