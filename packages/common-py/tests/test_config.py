"""Tests for configuration."""
from finops_common.config import Settings


def test_default_settings():
    """Test default settings."""
    settings = Settings()

    assert settings.service_name == "finops-service"
    assert settings.service_version == "1.0.0"
    assert settings.environment == "development"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.log_level == "INFO"
    assert settings.log_json is True


def test_custom_settings():
    """Test custom settings."""
    settings = Settings(
        service_name="custom-service",
        service_version="2.0.0",
        port=9000,
        log_level="DEBUG",
    )

    assert settings.service_name == "custom-service"
    assert settings.service_version == "2.0.0"
    assert settings.port == 9000
    assert settings.log_level == "DEBUG"


def test_otel_service_name_resolved():
    """Test OpenTelemetry service name resolution."""
    # Without custom otel_service_name
    settings = Settings(service_name="my-service")
    assert settings.otel_service_name_resolved == "my-service"

    # With custom otel_service_name
    settings = Settings(
        service_name="my-service",
        otel_service_name="custom-otel-name",
    )
    assert settings.otel_service_name_resolved == "custom-otel-name"


def test_database_settings():
    """Test database settings."""
    settings = Settings(
        database_url="postgresql://user:pass@localhost/db",
        database_pool_size=10,
        database_max_overflow=20,
    )

    assert settings.database_url == "postgresql://user:pass@localhost/db"
    assert settings.database_pool_size == 10
    assert settings.database_max_overflow == 20


def test_cors_settings():
    """Test CORS settings."""
    settings = Settings(
        cors_enabled=True,
        cors_origins=["http://localhost:3000", "https://app.example.com"],
        cors_credentials=True,
    )

    assert settings.cors_enabled is True
    assert len(settings.cors_origins) == 2
    assert "http://localhost:3000" in settings.cors_origins
    assert settings.cors_credentials is True
