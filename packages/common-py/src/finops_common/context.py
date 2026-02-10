"""Request context management using context variables."""
import uuid
from contextvars import ContextVar
from typing import Optional

# Context variables for request tracking
_request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
_org_id_var: ContextVar[Optional[str]] = ContextVar("org_id", default=None)
_tenant_id_var: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)
_user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set request ID in context. Generate new UUID if not provided."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    _request_id_var.set(request_id)
    return request_id


def get_request_id() -> Optional[str]:
    """Get current request ID from context."""
    return _request_id_var.get()


def set_org_id(org_id: Optional[str]) -> None:
    """Set organization ID in context."""
    _org_id_var.set(org_id)


def get_org_id() -> Optional[str]:
    """Get current organization ID from context."""
    return _org_id_var.get()


def set_tenant_id(tenant_id: Optional[str]) -> None:
    """Set tenant ID in context."""
    _tenant_id_var.set(tenant_id)


def get_tenant_id() -> Optional[str]:
    """Get current tenant ID from context."""
    return _tenant_id_var.get()


def set_user_id(user_id: Optional[str]) -> None:
    """Set user ID in context."""
    _user_id_var.set(user_id)


def get_user_id() -> Optional[str]:
    """Get current user ID from context."""
    return _user_id_var.get()


def clear_context() -> None:
    """Clear all context variables."""
    _request_id_var.set(None)
    _org_id_var.set(None)
    _tenant_id_var.set(None)
    _user_id_var.set(None)
