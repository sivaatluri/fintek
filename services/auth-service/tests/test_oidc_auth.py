"""Tests for OIDC authentication."""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from oidc.auth import OIDCAuth
from oidc.jwt_utils import JWTValidator


@pytest.fixture
def mock_jwt_validator():
    """Create mock JWT validator."""
    validator = Mock(spec=JWTValidator)
    return validator


@pytest.fixture
def oidc_auth(mock_jwt_validator):
    """Create OIDC auth instance."""
    return OIDCAuth(mock_jwt_validator)


@pytest.mark.asyncio
async def test_get_current_user_success(oidc_auth, mock_jwt_validator):
    """Test successful user extraction from token."""
    # Mock token validation
    mock_jwt_validator.validate_token.return_value = {
        "sub": "user-123",
        "preferred_username": "testuser",
        "email": "test@example.com",
    }
    
    mock_jwt_validator.extract_user_info.return_value = {
        "user_id": "user-123",
        "username": "testuser",
        "email": "test@example.com",
        "org_id": "org-456",
        "tenant_id": "tenant-789",
    }
    
    # Test with valid Bearer token
    user = await oidc_auth.get_current_user(
        authorization="Bearer valid-token-here"
    )
    
    assert user["user_id"] == "user-123"
    assert user["username"] == "testuser"
    assert user["email"] == "test@example.com"
    assert user["org_id"] == "org-456"
    
    # Verify validator was called
    mock_jwt_validator.validate_token.assert_called_once_with("valid-token-here")
    mock_jwt_validator.extract_user_info.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_missing_header(oidc_auth):
    """Test error when Authorization header is missing."""
    with pytest.raises(HTTPException) as exc_info:
        await oidc_auth.get_current_user(authorization=None)
    
    assert exc_info.value.status_code == 401
    assert "Missing authorization header" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_current_user_invalid_format(oidc_auth):
    """Test error when Authorization header format is invalid."""
    # Missing Bearer prefix
    with pytest.raises(HTTPException) as exc_info:
        await oidc_auth.get_current_user(authorization="just-a-token")
    
    assert exc_info.value.status_code == 401
    assert "Invalid authorization header format" in exc_info.value.detail
    
    # Wrong scheme
    with pytest.raises(HTTPException) as exc_info:
        await oidc_auth.get_current_user(authorization="Basic dXNlcjpwYXNz")
    
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(oidc_auth, mock_jwt_validator):
    """Test error when token validation fails."""
    # Mock token validation failure
    mock_jwt_validator.validate_token.side_effect = HTTPException(
        status_code=401,
        detail="Invalid token",
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await oidc_auth.get_current_user(authorization="Bearer invalid-token")
    
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_optional_user_with_token(oidc_auth, mock_jwt_validator):
    """Test optional user extraction with valid token."""
    mock_jwt_validator.validate_token.return_value = {"sub": "user-123"}
    mock_jwt_validator.extract_user_info.return_value = {
        "user_id": "user-123",
        "username": "testuser",
    }
    
    user = await oidc_auth.get_optional_user(
        authorization="Bearer valid-token"
    )
    
    assert user is not None
    assert user["user_id"] == "user-123"


@pytest.mark.asyncio
async def test_get_optional_user_without_token(oidc_auth):
    """Test optional user extraction without token."""
    user = await oidc_auth.get_optional_user(authorization=None)
    
    assert user is None


@pytest.mark.asyncio
async def test_get_optional_user_with_invalid_token(oidc_auth, mock_jwt_validator):
    """Test optional user extraction with invalid token."""
    mock_jwt_validator.validate_token.side_effect = HTTPException(
        status_code=401,
        detail="Invalid token",
    )
    
    user = await oidc_auth.get_optional_user(
        authorization="Bearer invalid-token"
    )
    
    assert user is None


@pytest.mark.asyncio  
async def test_context_setting(oidc_auth, mock_jwt_validator):
    """Test that user context is set during authentication."""
    mock_jwt_validator.validate_token.return_value = {"sub": "user-123"}
    mock_jwt_validator.extract_user_info.return_value = {
        "user_id": "user-123",
        "username": "testuser",
        "org_id": "org-456",
        "tenant_id": "tenant-789",
    }
    
    with patch("oidc.auth.set_context_values") as mock_set_context:
        await oidc_auth.get_current_user(authorization="Bearer token")
        
        # Verify context was set
        mock_set_context.assert_called_once_with(
            user_id="user-123",
            org_id="org-456",
            tenant_id="tenant-789",
        )
