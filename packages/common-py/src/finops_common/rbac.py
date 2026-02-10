"""RBAC (Role-Based Access Control) decorators and guards."""
from enum import Enum
from functools import wraps
from typing import Callable, List, Optional, Union

from fastapi import Depends, HTTPException, Request, status

from finops_common.context import get_org_id, get_user_id


class Permission(str, Enum):
    """Permission enumeration for RBAC."""

    # Cost permissions
    COSTS_READ = "costs:read"
    COSTS_WRITE = "costs:write"

    # Budget permissions
    BUDGETS_READ = "budgets:read"
    BUDGETS_WRITE = "budgets:write"

    # Recommendation permissions
    RECOMMENDATIONS_READ = "recommendations:read"
    RECOMMENDATIONS_WRITE = "recommendations:write"

    # Workflow permissions
    WORKFLOWS_READ = "workflows:read"
    WORKFLOWS_WRITE = "workflows:write"

    # Tenant permissions
    TENANTS_READ = "tenants:read"
    TENANTS_WRITE = "tenants:write"

    # User permissions
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"

    # Admin permissions
    ADMIN = "admin:all"


class Role(str, Enum):
    """Role enumeration for RBAC."""

    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    TENANT_ADMIN = "tenant_admin"
    FINOPS_ENGINEER = "finops_engineer"
    DEVELOPER = "developer"
    VIEWER = "viewer"


# Role to permissions mapping (example configuration)
ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: [Permission.ADMIN],
    Role.ORG_ADMIN: [
        Permission.COSTS_READ,
        Permission.COSTS_WRITE,
        Permission.BUDGETS_READ,
        Permission.BUDGETS_WRITE,
        Permission.RECOMMENDATIONS_READ,
        Permission.WORKFLOWS_READ,
        Permission.WORKFLOWS_WRITE,
        Permission.TENANTS_READ,
        Permission.USERS_READ,
        Permission.USERS_WRITE,
    ],
    Role.TENANT_ADMIN: [
        Permission.COSTS_READ,
        Permission.BUDGETS_READ,
        Permission.BUDGETS_WRITE,
        Permission.RECOMMENDATIONS_READ,
        Permission.WORKFLOWS_READ,
        Permission.WORKFLOWS_WRITE,
    ],
    Role.FINOPS_ENGINEER: [
        Permission.COSTS_READ,
        Permission.COSTS_WRITE,
        Permission.BUDGETS_READ,
        Permission.BUDGETS_WRITE,
        Permission.RECOMMENDATIONS_READ,
        Permission.RECOMMENDATIONS_WRITE,
        Permission.WORKFLOWS_READ,
    ],
    Role.DEVELOPER: [
        Permission.COSTS_READ,
        Permission.RECOMMENDATIONS_READ,
    ],
    Role.VIEWER: [
        Permission.COSTS_READ,
        Permission.BUDGETS_READ,
        Permission.RECOMMENDATIONS_READ,
    ],
}


class RBACGuard:
    """RBAC guard for checking permissions."""

    def __init__(self):
        """Initialize RBAC guard."""
        self.role_permissions = ROLE_PERMISSIONS

    async def get_user_permissions(self, user_id: str, org_id: str) -> List[Permission]:
        """Get user permissions (placeholder - implement with your auth service).

        Args:
            user_id: User ID
            org_id: Organization ID

        Returns:
            List of permissions
        """
        # TODO: Implement actual permission lookup from auth service
        # For now, return empty list - services should override this
        return []

    async def has_permission(
        self,
        user_id: str,
        org_id: str,
        required_permission: Permission,
    ) -> bool:
        """Check if user has required permission.

        Args:
            user_id: User ID
            org_id: Organization ID
            required_permission: Required permission

        Returns:
            True if user has permission
        """
        permissions = await self.get_user_permissions(user_id, org_id)

        # Super admin permission grants all permissions
        if Permission.ADMIN in permissions:
            return True

        return required_permission in permissions


# Global RBAC guard instance
_rbac_guard = RBACGuard()


def get_rbac_guard() -> RBACGuard:
    """Get RBAC guard instance."""
    return _rbac_guard


def require_permission(permission: Union[Permission, List[Permission]]) -> Callable:
    """Decorator to require specific permission(s).

    Args:
        permission: Required permission or list of permissions (any match)

    Returns:
        Decorator function

    Raises:
        HTTPException: If user doesn't have required permission
    """
    permissions = [permission] if isinstance(permission, Permission) else permission

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user and org from context
            user_id = get_user_id()
            org_id = get_org_id()

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if not org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization context required",
                )

            # Check permissions
            guard = get_rbac_guard()
            has_any_permission = False

            for perm in permissions:
                if await guard.has_permission(user_id, org_id, perm):
                    has_any_permission = True
                    break

            if not has_any_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required permission: {permissions[0].value}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role: Union[Role, List[Role]]) -> Callable:
    """Decorator to require specific role(s).

    Args:
        role: Required role or list of roles (any match)

    Returns:
        Decorator function

    Raises:
        HTTPException: If user doesn't have required role
    """
    roles = [role] if isinstance(role, Role) else role
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from context
            user_id = get_user_id()
            org_id = get_org_id()

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if not org_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Organization context required",
                )

            # TODO: Implement actual role lookup
            # For now, this is a placeholder
            # Services should implement their own role checking

            return await func(*args, **kwargs)

        return wrapper

    return decorator
