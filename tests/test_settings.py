from app.settings import Settings


def test_settings() -> None:
    """Test the settings."""
    settings = Settings()

    assert settings.server_host == "127.0.0.1"
    assert settings.server_port == 8000
    assert settings.docker_cleanup_images is True
    assert settings.log_level == "INFO"

    # Test get_app_kwargs
    app_kwargs = settings.get_app_kwargs()
    assert "title" in app_kwargs
    assert "description" in app_kwargs
