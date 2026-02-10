"""Tests for gateway API service."""
import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "FinOps Gateway API"


def test_ready_endpoint():
    """Test readiness endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert data["service"] == "FinOps Gateway API"


def test_status_endpoint():
    """Test status endpoint."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "gateway-api"
    assert data["status"] == "operational"
    assert data["version"] == "1.0.0"


def test_protected_endpoint_without_auth():
    """Test protected endpoint without authentication."""
    response = client.get("/api/v1/protected")
    assert response.status_code == 401


def test_request_id_header():
    """Test that request ID is returned in headers."""
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
