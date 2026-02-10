"""FinOps Common - Shared utilities for FastAPI services."""

__version__ = "0.1.0"

from finops_common.app import create_app
from finops_common.config import Settings
from finops_common.context import get_org_id, get_request_id, get_tenant_id, get_user_id
from finops_common.health import HealthResponse, ReadyResponse
from finops_common.logging import get_logger, setup_logging
from finops_common.rbac import Permission, require_permission, require_role

__all__ = [
    "create_app",
    "Settings",
    "get_request_id",
    "get_org_id",
    "get_tenant_id",
    "get_user_id",
    "HealthResponse",
    "ReadyResponse",
    "get_logger",
    "setup_logging",
    "Permission",
    "require_permission",
    "require_role",
]
