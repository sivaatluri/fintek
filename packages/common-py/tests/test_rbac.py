"""Tests for RBAC guards."""
import pytest
from fastapi import HTTPException

from finops_common.context import set_org_id, set_user_id
from finops_common.rbac import Permission, Role, require_permission, require_role


@pytest.mark.asyncio
async def test_require_permission_without_auth():
    """Test require_permission decorator without authentication."""

    @require_permission(Permission.COSTS_READ)
    async def protected_function():
        return "success"

    with pytest.raises(HTTPException) as exc_info:
        await protected_function()

    assert exc_info.value.status_code == 401
    assert "Authentication required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_require_permission_without_org():
    """Test require_permission decorator without org context."""
    set_user_id("user-123")

    @require_permission(Permission.COSTS_READ)
    async def protected_function():
        return "success"

    with pytest.raises(HTTPException) as exc_info:
        await protected_function()

    assert exc_info.value.status_code == 400
    assert "Organization context required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_require_role_without_auth():
    """Test require_role decorator without authentication."""

    @require_role(Role.FINOPS_ENGINEER)
    async def protected_function():
        return "success"

    with pytest.raises(HTTPException) as exc_info:
        await protected_function()

    assert exc_info.value.status_code == 401


def test_permissions_enum():
    """Test Permission enum values."""
    assert Permission.COSTS_READ.value == "costs:read"
    assert Permission.BUDGETS_WRITE.value == "budgets:write"
    assert Permission.ADMIN.value == "admin:all"


def test_roles_enum():
    """Test Role enum values."""
    assert Role.SUPER_ADMIN.value == "super_admin"
    assert Role.ORG_ADMIN.value == "org_admin"
    assert Role.VIEWER.value == "viewer"
