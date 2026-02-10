"""Tests for FastAPI application factory."""
import pytest
from fastapi.testclient import TestClient

from finops_common import create_app
from finops_common.config import Settings


def test_create_app():
    """Test basic app creation."""
    app = create_app("test-service", "1.0.0")
    assert app.title == "test-service"
    assert app.version == "1.0.0"


def test_health_endpoint():
    """Test health endpoint."""
    app = create_app("test-service", "1.0.0")
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "test-service"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data


def test_ready_endpoint():
    """Test readiness endpoint."""
    app = create_app("test-service", "1.0.0")
    client = TestClient(app)

    response = client.get("/ready")
    assert response.status_code == 200

    data = response.json()
    assert "ready" in data
    assert data["service"] == "test-service"
    assert data["version"] == "1.0.0"
    assert "checks" in data


def test_create_app_with_settings():
    """Test app creation with custom settings."""
    settings = Settings(
        service_name="custom-service",
        log_level="DEBUG",
        docs_enabled=False,
    )

    app = create_app("test-service", "1.0.0", settings=settings)
    assert app.docs_url is None
    assert app.redoc_url is None


def test_request_id_middleware():
    """Test request ID middleware."""
    app = create_app("test-service", "1.0.0")
    client = TestClient(app)

    # Without X-Request-ID header
    response = client.get("/health")
    assert "X-Request-ID" in response.headers

    # With X-Request-ID header
    response = client.get("/health", headers={"X-Request-ID": "test-123"})
    assert response.headers["X-Request-ID"] == "test-123"


def test_cors_enabled():
    """Test CORS middleware."""
    settings = Settings(cors_enabled=True, cors_origins=["http://localhost:3000"])
    app = create_app("test-service", "1.0.0", settings=settings)
    client = TestClient(app)

    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
