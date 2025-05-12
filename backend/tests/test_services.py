from fastapi import FastAPI

from docker_scanner.services.docker_service import DockerService
from docker_scanner.services.job_service import JobService
from docker_scanner.services.redis_service import RedisService


def create_test_app():
    app = FastAPI()
    app.state.docker_service = DockerService()
    app.state.redis_service = RedisService()
    app.state.job_service = JobService(
        docker_service=app.state.docker_service,
        redis_service=app.state.redis_service,
    )
    return app


def test_services_on_app_state():
    app = create_test_app()
    assert isinstance(app.state.docker_service, DockerService)
    assert isinstance(app.state.redis_service, RedisService)
    assert isinstance(app.state.job_service, JobService)
    # Check that job_service uses the same docker_service and redis_service
    assert app.state.job_service.docker_service is app.state.docker_service
    assert app.state.job_service.redis_service is app.state.redis_service
