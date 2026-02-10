"""Cost Normalization Service - Main application."""
from fastapi import APIRouter

from finops_common import Settings, create_app, get_logger

logger = get_logger(__name__)

settings = Settings(
    service_name="cost-normalization-service",
    service_version="1.0.0",
    port=8005,
)

app = create_app(
    title="FinOps Cost Normalization Service",
    version="1.0.0",
    description="Cost Normalization Service for FinOps SaaS Platform",
    settings=settings,
)

router = APIRouter(prefix="/api/v1", tags=["Cost Normalization Service"])


@router.get("/status")
async def get_status():
    """Get service status."""
    logger.info("Status endpoint called")
    return {
        "service": "cost-normalization-service",
        "status": "operational",
        "version": "1.0.0",
    }


app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Cost Normalization Service starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Cost Normalization Service shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
