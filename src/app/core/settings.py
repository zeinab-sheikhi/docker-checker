from typing import Any, Dict, Optional
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
    api_prefix: str = ""


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
    docker_registry: Optional[str] = None  # Optional private registry
    docker_storage_path: str = "storage/dockerfiles"
    docker_cleanup_images: bool = True  # Whether to cleanup images after use

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",  # Environment variables should be prefixed with APP_
        case_sensitive=False,
    )

    def get_app_kwargs(self) -> Dict[str, Any]:
        """Get FastAPI application arguments"""
        return self.app_config.model_dump()


# Create global settings instance
settings = Settings() 