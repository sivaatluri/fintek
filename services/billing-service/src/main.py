"""Billing Service - Main application."""
from fastapi import APIRouter

from finops_common import Settings, create_app, get_logger

logger = get_logger(__name__)

settings = Settings(
    service_name="billing-service",
    service_version="1.0.0",
    port=8003,
)

app = create_app(
    title="FinOps Billing Service",
    version="1.0.0",
    description="Billing Service for FinOps SaaS Platform",
    settings=settings,
)

router = APIRouter(prefix="/api/v1", tags=["Billing Service"])


@router.get("/status")
async def get_status():
    """Get service status."""
    logger.info("Status endpoint called")
    return {
        "service": "billing-service",
        "status": "operational",
        "version": "1.0.0",
    }


app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Billing Service starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Billing Service shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
