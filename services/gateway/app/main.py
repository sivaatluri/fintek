"""Gateway service for fintek platform."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from datetime import datetime

from .config import get_settings
from .health import router as health_router

settings = get_settings()

app = FastAPI(
    title="Fintek Gateway",
    description="API Gateway for fintek multi-tenant FinOps platform",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "fintek-gateway",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    """Proxy requests to backend services.
    
    This is a placeholder implementation. In production, this would:
    - Route to appropriate backend services
    - Handle authentication/authorization
    - Implement rate limiting
    - Add request/response logging
    """
    # Service routing map (placeholder)
    service_map = {
        "auth": settings.auth_service_url,
        "tenants": settings.tenant_service_url,
        "costs": settings.ingestion_service_url,
        "budgets": settings.budgets_service_url,
        "query": settings.query_service_url,
        "integrations": settings.integrations_service_url,
        "workflows": settings.workflows_service_url,
    }
    
    base_url = service_map.get(service)
    if not base_url:
        return JSONResponse(
            status_code=404,
            content={"error": f"Service '{service}' not found"}
        )
    
    # Placeholder: Forward request to backend service
    return JSONResponse(
        status_code=501,
        content={
            "error": "Proxy not implemented",
            "message": f"Would forward to {base_url}/{path}",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
