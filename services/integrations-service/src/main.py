"""Integrations Service - Main application."""
from fastapi import APIRouter

from finops_common import Settings, create_app, get_logger

logger = get_logger(__name__)

settings = Settings(
    service_name="integrations-service",
    service_version="1.0.0",
    port=8011,
)

app = create_app(
    title="FinOps Integrations Service",
    version="1.0.0",
    description="Integrations Service for FinOps SaaS Platform",
    settings=settings,
)

router = APIRouter(prefix="/api/v1", tags=["Integrations Service"])


@router.get("/status")
async def get_status():
    """Get service status."""
    logger.info("Status endpoint called")
    return {
        "service": "integrations-service",
        "status": "operational",
        "version": "1.0.0",
    }


app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Integrations Service starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Integrations Service shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
