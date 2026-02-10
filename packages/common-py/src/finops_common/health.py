"""Health and readiness check endpoints."""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(default="healthy", description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")


class ReadyResponse(BaseModel):
    """Readiness check response model."""

    ready: bool = Field(..., description="Service readiness status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    checks: Dict[str, Any] = Field(
        default_factory=dict,
        description="Individual dependency checks",
    )


class HealthChecker:
    """Health and readiness checker."""

    def __init__(self, service_name: str, version: str):
        """Initialize health checker."""
        self.service_name = service_name
        self.version = version
        self._ready_checks: Dict[str, callable] = {}

    def register_ready_check(self, name: str, check_func: callable) -> None:
        """Register a readiness check function.

        Args:
            name: Name of the check
            check_func: Async function that returns bool or dict with status
        """
        self._ready_checks[name] = check_func

    async def health(self) -> HealthResponse:
        """Perform basic health check."""
        return HealthResponse(
            service=self.service_name,
            version=self.version,
        )

    async def ready(self) -> ReadyResponse:
        """Perform readiness check with all registered checks."""
        checks = {}
        all_ready = True

        for name, check_func in self._ready_checks.items():
            try:
                result = await check_func()
                if isinstance(result, bool):
                    checks[name] = {"status": "ready" if result else "not_ready"}
                    all_ready = all_ready and result
                elif isinstance(result, dict):
                    checks[name] = result
                    all_ready = all_ready and result.get("status") == "ready"
                else:
                    checks[name] = {"status": "ready"}
            except Exception as e:
                checks[name] = {"status": "error", "error": str(e)}
                all_ready = False

        return ReadyResponse(
            ready=all_ready,
            service=self.service_name,
            version=self.version,
            checks=checks,
        )
