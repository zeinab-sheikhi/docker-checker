import uvicorn
from docker_checker.settings import settings


def main():
    uvicorn.run(
        "docker_checker.app:app",
        host=settings.server_host,
        port=settings.server_port,
        workers=settings.server_workers,
    )


if __name__ == "__main__":
    main()
