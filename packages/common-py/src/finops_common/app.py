"""FastAPI application factory."""
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from finops_common.config import Settings
from finops_common.health import HealthChecker, HealthResponse, ReadyResponse
from finops_common.logging import setup_logging
from finops_common.middleware import LoggingMiddleware, RequestContextMiddleware
from finops_common.telemetry import instrument_fastapi, setup_telemetry


def create_app(
    title: str,
    version: str = "1.0.0",
    description: Optional[str] = None,
    settings: Optional[Settings] = None,
) -> FastAPI:
    """Create a FastAPI application with standard configuration.

    Args:
        title: Application title
        version: Application version
        description: Application description
        settings: Application settings (will create default if not provided)

    Returns:
        Configured FastAPI application
    """
    # Load settings
    if settings is None:
        settings = Settings(service_name=title, service_version=version)

    # Setup logging
    setup_logging(
        level=settings.log_level,
        json_logs=settings.log_json,
        service_name=settings.service_name,
    )

    # Setup OpenTelemetry
    setup_telemetry(
        service_name=settings.otel_service_name_resolved,
        service_version=version,
        otel_endpoint=settings.otel_endpoint,
        enabled=settings.otel_enabled,
    )

    # Create FastAPI app
    app = FastAPI(
        title=title,
        version=version,
        description=description,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )

    # Add middleware
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(LoggingMiddleware)

    # Add CORS middleware
    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=settings.cors_credentials,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Instrument with OpenTelemetry
    if settings.otel_enabled:
        instrument_fastapi(app)

    # Create health checker
    health_checker = HealthChecker(service_name=title, version=version)

    # Add health and readiness endpoints
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health() -> HealthResponse:
        """Health check endpoint."""
        return await health_checker.health()

    @app.get("/ready", response_model=ReadyResponse, tags=["Health"])
    async def ready() -> ReadyResponse:
        """Readiness check endpoint."""
        return await health_checker.ready()

    # Store health checker for later use
    app.state.health_checker = health_checker

    return app
