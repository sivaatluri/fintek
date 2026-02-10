"""Workflows Service - Main application."""
from fastapi import APIRouter

from finops_common import Settings, create_app, get_logger

logger = get_logger(__name__)

settings = Settings(
    service_name="workflows-service",
    service_version="1.0.0",
    port=8010,
)

app = create_app(
    title="FinOps Workflows Service",
    version="1.0.0",
    description="Workflows Service for FinOps SaaS Platform",
    settings=settings,
)

router = APIRouter(prefix="/api/v1", tags=["Workflows Service"])


@router.get("/status")
async def get_status():
    """Get service status."""
    logger.info("Status endpoint called")
    return {
        "service": "workflows-service",
        "status": "operational",
        "version": "1.0.0",
    }


app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Workflows Service starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Workflows Service shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
