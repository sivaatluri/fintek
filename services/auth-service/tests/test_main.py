"""Tests for auth service main endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch

# Import after mocking dependencies
@pytest.fixture
def mock_config():
    """Mock configuration."""
    with patch("main.config") as mock:
        mock.service_name = "auth-service"
        mock.port = 8001
        mock.environment = "test"
        mock.log_level = "INFO"
        mock.database_url = "postgresql://test:test@localhost/test"
        mock.redis_url = "redis://localhost:6379/0"
        mock.keycloak.server_url = "http://keycloak:8081"
        mock.keycloak.realm = "finops"
        mock.keycloak.jwks_uri = "http://keycloak:8081/realms/finops/certs"
        mock.keycloak.logout_endpoint = "http://keycloak:8081/realms/finops/logout"
        mock.jwt.audience = "finops-api"
        mock.saml.enabled = False
        mock.scim.enabled = False
        mock.kafka.bootstrap_servers = "kafka:9092"
        yield mock


@pytest.fixture
def mock_oidc_auth():
    """Mock OIDC auth."""
    with patch("main.oidc_auth") as mock:
        mock.get_current_user = AsyncMock()
        yield mock


@pytest.fixture
def client(mock_config, mock_oidc_auth):
    """Create test client."""
    # Import here to use mocked dependencies
    from main import app
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_ready_endpoint(client):
    """Test readiness check endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_get_current_user_success(client, mock_oidc_auth):
    """Test GET /auth/me with valid token."""
    # Mock user data
    mock_oidc_auth.get_current_user.return_value = {
        "user_id": "user-123",
        "username": "testuser",
        "email": "test@example.com",
        "name": "Test User",
        "roles": ["finops_engineer"],
        "org_id": "org-456",
        "tenant_id": "tenant-789",
    }
    
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer valid-token"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user-123"
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["roles"] == ["finops_engineer"]
    assert data["org_id"] == "org-456"


def test_get_current_user_unauthorized(client, mock_oidc_auth):
    """Test GET /auth/me without token."""
    from fastapi import HTTPException
    
    mock_oidc_auth.get_current_user.side_effect = HTTPException(
        status_code=401,
        detail="Missing authorization header",
    )
    
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_logout_success(client, mock_oidc_auth):
    """Test POST /auth/logout."""
    mock_oidc_auth.get_current_user.return_value = {
        "user_id": "user-123",
        "username": "testuser",
    }
    
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer valid-token"},
        json={"everywhere": False},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logged out successfully"
    assert "redirect_url" in data


def test_logout_everywhere(client, mock_oidc_auth):
    """Test logout from all sessions."""
    mock_oidc_auth.get_current_user.return_value = {
        "user_id": "user-123",
        "username": "testuser",
    }
    
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer valid-token"},
        json={"everywhere": True},
    )
    
    assert response.status_code == 200


def test_oidc_config_endpoint(client):
    """Test OIDC configuration endpoint."""
    response = client.get("/auth/oidc/config")
    
    assert response.status_code == 200
    data = response.json()
    assert "issuer" in data
    assert "authorization_endpoint" in data
    assert "token_endpoint" in data
    assert "jwks_uri" in data


def test_saml_acs_disabled(client, mock_config):
    """Test SAML ACS when SAML is disabled."""
    mock_config.saml.enabled = False
    
    response = client.post("/auth/saml/acs")
    
    assert response.status_code == 404
    assert "not enabled" in response.json()["detail"]


def test_saml_metadata_disabled(client, mock_config):
    """Test SAML metadata when SAML is disabled."""
    mock_config.saml.enabled = False
    
    response = client.get("/auth/saml/metadata")
    
    assert response.status_code == 404


def test_scim_list_users_disabled(client, mock_config):
    """Test SCIM list users when SCIM is disabled."""
    mock_config.scim.enabled = False
    
    response = client.get("/auth/scim/v2/Users")
    
    assert response.status_code == 404
    assert "not enabled" in response.json()["detail"]


def test_scim_create_user_disabled(client, mock_config):
    """Test SCIM create user when SCIM is disabled."""
    mock_config.scim.enabled = False
    
    response = client.post("/auth/scim/v2/Users")
    
    assert response.status_code == 404


def test_request_id_header(client):
    """Test that request ID is returned in response."""
    response = client.get("/health")
    
    assert "x-request-id" in response.headers


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options(
        "/auth/me",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    
    # CORS middleware should add headers
    assert "access-control-allow-origin" in response.headers
