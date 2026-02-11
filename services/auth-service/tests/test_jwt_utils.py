"""Tests for JWT validation."""
import jwt
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from oidc.jwt_utils import JWTGenerator, JWTValidator


@pytest.fixture
def mock_jwks_client():
    """Mock JWKS client."""
    with patch("oidc.jwt_utils.PyJWKClient") as mock:
        yield mock


@pytest.fixture
def jwt_generator():
    """Create JWT generator for testing."""
    return JWTGenerator(
        secret_key="test-secret-key",
        algorithm="HS256",
        issuer="test-issuer",
        audience="test-audience",
    )


def test_jwt_generator_create_access_token(jwt_generator):
    """Test creating access token."""
    token = jwt_generator.create_access_token(
        subject="user-123",
        claims={
            "username": "testuser",
            "email": "test@example.com",
        },
    )
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode and verify
    payload = jwt.decode(
        token,
        jwt_generator.secret_key,
        algorithms=[jwt_generator.algorithm],
        audience=jwt_generator.audience,
        issuer=jwt_generator.issuer,
    )
    
    assert payload["sub"] == "user-123"
    assert payload["username"] == "testuser"
    assert payload["email"] == "test@example.com"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_generator_create_refresh_token(jwt_generator):
    """Test creating refresh token."""
    token = jwt_generator.create_refresh_token(subject="user-123")
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode and verify
    payload = jwt.decode(
        token,
        jwt_generator.secret_key,
        algorithms=[jwt_generator.algorithm],
        issuer=jwt_generator.issuer,
    )
    
    assert payload["sub"] == "user-123"
    assert payload["type"] == "refresh"


def test_jwt_generator_custom_expiry(jwt_generator):
    """Test creating token with custom expiry."""
    custom_expiry = timedelta(minutes=30)
    token = jwt_generator.create_access_token(
        subject="user-123",
        expires_delta=custom_expiry,
    )
    
    payload = jwt.decode(
        token,
        jwt_generator.secret_key,
        algorithms=[jwt_generator.algorithm],
        audience=jwt_generator.audience,
        issuer=jwt_generator.issuer,
    )
    
    # Check expiry is approximately 30 minutes from now
    exp_time = datetime.fromtimestamp(payload["exp"])
    iat_time = datetime.fromtimestamp(payload["iat"])
    diff = exp_time - iat_time
    
    assert diff.total_seconds() == pytest.approx(1800, abs=5)  # 30 minutes ±5 seconds


def test_jwt_validator_extract_user_info():
    """Test extracting user info from token payload."""
    validator = JWTValidator(
        jwks_uri="http://test/jwks",
        issuer="test-issuer",
        audience="test-audience",
    )
    
    payload = {
        "sub": "user-123",
        "preferred_username": "testuser",
        "email": "test@example.com",
        "name": "Test User",
        "given_name": "Test",
        "family_name": "User",
        "realm_access": {
            "roles": ["finops_engineer", "viewer"],
        },
        "groups": ["engineering", "finance"],
        "org_id": "org-456",
        "tenant_id": "tenant-789",
    }
    
    user_info = validator.extract_user_info(payload)
    
    assert user_info["user_id"] == "user-123"
    assert user_info["username"] == "testuser"
    assert user_info["email"] == "test@example.com"
    assert user_info["name"] == "Test User"
    assert user_info["roles"] == ["finops_engineer", "viewer"]
    assert user_info["groups"] == ["engineering", "finance"]
    assert user_info["org_id"] == "org-456"
    assert user_info["tenant_id"] == "tenant-789"


def test_jwt_validator_expired_token():
    """Test validation of expired token."""
    # Create expired token
    generator = JWTGenerator(
        secret_key="test-secret",
        algorithm="HS256",
    )
    
    token = generator.create_access_token(
        subject="user-123",
        expires_delta=timedelta(seconds=-10),  # Already expired
    )
    
    validator = JWTValidator(
        jwks_uri="http://test/jwks",
    )
    
    # Mock the JWKS client to return a signing key
    mock_key = Mock()
    mock_key.key = "test-secret"
    validator.jwks_client.get_signing_key_from_jwt = Mock(return_value=mock_key)
    
    # Validation should raise HTTPException for expired token
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        validator.validate_token(token)
    
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_jwt_validator_invalid_signature():
    """Test validation of token with invalid signature."""
    # Create token with one key
    generator = JWTGenerator(
        secret_key="test-secret",
        algorithm="HS256",
    )
    
    token = generator.create_access_token(subject="user-123")
    
    # Try to validate with different key
    validator = JWTValidator(
        jwks_uri="http://test/jwks",
    )
    
    mock_key = Mock()
    mock_key.key = "wrong-secret"  # Different key
    validator.jwks_client.get_signing_key_from_jwt = Mock(return_value=mock_key)
    
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        validator.validate_token(token)
    
    assert exc_info.value.status_code == 401


def test_jwt_validator_missing_claims():
    """Test extracting user info with missing claims."""
    validator = JWTValidator(
        jwks_uri="http://test/jwks",
    )
    
    # Minimal payload
    payload = {
        "sub": "user-123",
    }
    
    user_info = validator.extract_user_info(payload)
    
    assert user_info["user_id"] == "user-123"
    assert user_info["username"] is None
    assert user_info["email"] is None
    assert user_info["roles"] == []
    assert user_info["groups"] == []
