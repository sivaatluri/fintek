"""Gateway API Service - Main application."""
from fastapi import APIRouter

from finops_common import Permission, Settings, create_app, get_logger, require_permission

# Initialize logger
logger = get_logger(__name__)

# Load settings
settings = Settings(
    service_name="gateway-api",
    service_version="1.0.0",
    port=8000,
)

# Create FastAPI app
app = create_app(
    title="FinOps Gateway API",
    version="1.0.0",
    description="API Gateway and Backend-for-Frontend for FinOps SaaS Platform",
    settings=settings,
)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["Gateway"])


@router.get("/status")
async def get_status():
    """Get gateway status."""
    logger.info("Status endpoint called")
    return {
        "service": "gateway-api",
        "status": "operational",
        "version": "1.0.0",
    }


@router.get("/protected")
@require_permission(Permission.COSTS_READ)
async def protected_endpoint():
    """Example protected endpoint requiring RBAC permission."""
    return {"message": "Access granted", "permission": "costs:read"}


# Include router
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Gateway API service starting up")
    # TODO: Initialize connections, caches, etc.


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Gateway API service shutting down")
    # TODO: Close connections, cleanup resources


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
