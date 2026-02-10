"""Tenant management service for fintek platform."""

from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr

from .health import router as health_router

app = FastAPI(
    title="Fintek Tenant Service",
    description="Tenant management and configuration service",
    version="0.1.0",
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])


class TenantCreate(BaseModel):
    """Tenant creation request."""
    name: str
    slug: str
    primary_contact_email: EmailStr
    primary_contact_name: str


class TenantResponse(BaseModel):
    """Tenant response."""
    id: str
    name: str
    slug: str
    status: str
    primary_contact_email: EmailStr
    primary_contact_name: str
    created_at: datetime


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "fintek-tenant",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(skip: int = 0, limit: int = 100):
    """List all tenants (placeholder)."""
    # Placeholder implementation
    return []


@app.post("/tenants", response_model=TenantResponse, status_code=201)
async def create_tenant(tenant: TenantCreate):
    """Create a new tenant (placeholder)."""
    # Placeholder implementation
    return {
        "id": "tenant-123",
        "name": tenant.name,
        "slug": tenant.slug,
        "status": "trial",
        "primary_contact_email": tenant.primary_contact_email,
        "primary_contact_name": tenant.primary_contact_name,
        "created_at": datetime.utcnow(),
    }


@app.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: str):
    """Get tenant by ID (placeholder)."""
    # Placeholder implementation
    return {
        "id": tenant_id,
        "name": "Sample Tenant",
        "slug": "sample-tenant",
        "status": "active",
        "primary_contact_email": "admin@sample.com",
        "primary_contact_name": "Admin User",
        "created_at": datetime.utcnow(),
    }


@app.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: str, tenant: TenantCreate):
    """Update tenant (placeholder)."""
    return {
        "id": tenant_id,
        "name": tenant.name,
        "slug": tenant.slug,
        "status": "active",
        "primary_contact_email": tenant.primary_contact_email,
        "primary_contact_name": tenant.primary_contact_name,
        "created_at": datetime.utcnow(),
    }


@app.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str):
    """Delete tenant (placeholder)."""
    return {"message": f"Tenant {tenant_id} deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
