from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseModel):
    """Application configuration"""

    title: str = "Docker Performance Service"
    description: str = """
    A service that processes Dockerfiles, builds images, and measures container performance.
    The service provides endpoints to:
    - Submit Dockerfiles and get a job ID
    - Check job status and get performance metrics
    """
    version: str = "0.1.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    api_prefix: str = "/api/v1"


class Settings(BaseSettings):
    """Application settings"""

    # Server settings
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    server_workers: int = 1
    reload: bool = True  # Enable auto-reload in development

    # Application settings
    app_config: AppConfig = AppConfig()

    # Docker settings
    docker_cleanup_images: bool = True  # Whether to cleanup images after use
    docker_timeout: int = 30

    # Volume settings
    volume_base_path: Path = Path("tmp/data")  # Base path for all job volumes
    volume_mode: str = "rw"  # Read-write mode for volumes
    volume_container_path: str = "/data"  # Mount point inside container

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    def get_app_kwargs(self) -> dict[str, Any]:
        """Get FastAPI application arguments"""
        return self.app_config.model_dump()

    def get_job_volume_path(self, job_id: str) -> Path:
        """Get the volume path for a specific job"""
        return self.volume_base_path / job_id


# Create global settings instance
settings = Settings()
