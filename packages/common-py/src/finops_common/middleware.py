"""Custom middleware for FastAPI applications."""
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from finops_common.context import set_org_id, set_request_id, set_tenant_id, set_user_id
from finops_common.logging import get_logger

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to set request context from headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and set context variables."""
        # Set request ID (from header or generate new)
        request_id = request.headers.get("X-Request-ID") or request.headers.get("X-Request-Id")
        request_id = set_request_id(request_id)

        # Set organization/tenant context from headers
        org_id = request.headers.get("X-Org-ID") or request.headers.get("X-Organization-Id")
        set_org_id(org_id)

        tenant_id = request.headers.get("X-Tenant-ID") or request.headers.get("X-Tenant-Id")
        set_tenant_id(tenant_id)

        # Set user ID from auth headers (placeholder)
        user_id = request.headers.get("X-User-ID") or request.headers.get("X-User-Id")
        set_user_id(user_id)

        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response information."""
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query) if request.url.query else None,
                "client_host": request.client.host if request.client else None,
            },
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                },
            )

            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_ms": round(duration * 1000, 2),
                },
                exc_info=True,
            )
            raise
