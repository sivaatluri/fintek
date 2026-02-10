"""Tests for middleware."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from finops_common.context import get_org_id, get_request_id, get_tenant_id, get_user_id
from finops_common.middleware import LoggingMiddleware, RequestContextMiddleware


def test_request_context_middleware():
    """Test request context middleware."""
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {
            "request_id": get_request_id(),
            "org_id": get_org_id(),
            "tenant_id": get_tenant_id(),
            "user_id": get_user_id(),
        }

    client = TestClient(app)

    # Test with headers
    response = client.get(
        "/test",
        headers={
            "X-Request-ID": "req-123",
            "X-Org-ID": "org-456",
            "X-Tenant-ID": "tenant-789",
            "X-User-ID": "user-101",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "req-123"
    assert data["org_id"] == "org-456"
    assert data["tenant_id"] == "tenant-789"
    assert data["user_id"] == "user-101"
    assert response.headers["X-Request-ID"] == "req-123"


def test_request_context_middleware_generates_id():
    """Test that middleware generates request ID if not provided."""
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"request_id": get_request_id()}

    client = TestClient(app)

    response = client.get("/test")
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] is not None
    assert len(data["request_id"]) == 36  # UUID format
    assert response.headers["X-Request-ID"] == data["request_id"]


def test_logging_middleware():
    """Test logging middleware."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)

    response = client.get("/test")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_logging_middleware_on_error():
    """Test logging middleware handles errors."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    client = TestClient(app)

    with pytest.raises(ValueError):
        client.get("/error")
