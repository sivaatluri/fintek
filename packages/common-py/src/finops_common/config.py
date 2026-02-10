"""Configuration management using Pydantic settings."""
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Identity
    service_name: str = Field(default="finops-service", description="Service name")
    service_version: str = Field(default="1.0.0", description="Service version")
    environment: str = Field(default="development", description="Environment (dev/staging/prod)")

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    workers: int = Field(default=1, description="Number of worker processes")
    reload: bool = Field(default=False, description="Auto-reload on code changes")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_json: bool = Field(default=True, description="Enable JSON logging")

    # OpenTelemetry
    otel_enabled: bool = Field(default=True, description="Enable OpenTelemetry")
    otel_endpoint: str = Field(
        default="http://otel-collector:4317",
        description="OTLP exporter endpoint",
    )
    otel_service_name: Optional[str] = Field(
        default=None,
        description="Service name for tracing (defaults to service_name)",
    )

    # Database
    database_url: Optional[str] = Field(
        default=None,
        description="Database connection URL",
    )
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Max overflow connections")

    # Redis
    redis_url: Optional[str] = Field(
        default="redis://redis:6379/0",
        description="Redis connection URL",
    )

    # Kafka
    kafka_bootstrap_servers: str = Field(
        default="kafka:9092",
        description="Kafka bootstrap servers",
    )

    # CORS
    cors_enabled: bool = Field(default=True, description="Enable CORS")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS origins",
    )
    cors_credentials: bool = Field(default=True, description="Allow CORS credentials")

    # API
    api_prefix: str = Field(default="/api/v1", description="API route prefix")
    docs_enabled: bool = Field(default=True, description="Enable OpenAPI docs")

    # Security
    jwt_secret: Optional[str] = Field(default=None, description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiry_minutes: int = Field(default=60, description="JWT expiry in minutes")

    @property
    def otel_service_name_resolved(self) -> str:
        """Get resolved OpenTelemetry service name."""
        return self.otel_service_name or self.service_name
