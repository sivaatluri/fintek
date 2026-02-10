"""RBAC models for fintek platform."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class Permission(str, Enum):
    """System permissions."""
    
    # Tenant management
    TENANT_READ = "tenant:read"
    TENANT_WRITE = "tenant:write"
    TENANT_DELETE = "tenant:delete"
    
    # Cost data
    COST_READ = "cost:read"
    COST_WRITE = "cost:write"
    COST_DELETE = "cost:delete"
    
    # Budget management
    BUDGET_READ = "budget:read"
    BUDGET_WRITE = "budget:write"
    BUDGET_DELETE = "budget:delete"
    
    # Integration management
    INTEGRATION_READ = "integration:read"
    INTEGRATION_WRITE = "integration:write"
    INTEGRATION_DELETE = "integration:delete"
    
    # User management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Query execution
    QUERY_EXECUTE = "query:execute"
    QUERY_ADMIN = "query:admin"


class Role(str, Enum):
    """System roles."""
    
    TENANT_ADMIN = "tenant_admin"
    TENANT_USER = "tenant_user"
    TENANT_VIEWER = "tenant_viewer"
    PLATFORM_ADMIN = "platform_admin"


class User(BaseModel):
    """User model with RBAC info."""
    
    id: str
    tenant_id: str
    email: str
    roles: List[Role] = Field(default_factory=list)
    permissions: List[Permission] = Field(default_factory=list)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions
    
    def has_role(self, role: Role) -> bool:
        """Check if user has a specific role."""
        return role in self.roles


# Role to permissions mapping (placeholder - should be configurable)
ROLE_PERMISSIONS = {
    Role.PLATFORM_ADMIN: list(Permission),
    Role.TENANT_ADMIN: [
        Permission.TENANT_READ,
        Permission.TENANT_WRITE,
        Permission.COST_READ,
        Permission.COST_WRITE,
        Permission.BUDGET_READ,
        Permission.BUDGET_WRITE,
        Permission.INTEGRATION_READ,
        Permission.INTEGRATION_WRITE,
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.QUERY_EXECUTE,
    ],
    Role.TENANT_USER: [
        Permission.TENANT_READ,
        Permission.COST_READ,
        Permission.BUDGET_READ,
        Permission.INTEGRATION_READ,
        Permission.QUERY_EXECUTE,
    ],
    Role.TENANT_VIEWER: [
        Permission.TENANT_READ,
        Permission.COST_READ,
        Permission.BUDGET_READ,
    ],
}
