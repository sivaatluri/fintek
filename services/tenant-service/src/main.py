"""Tenant Service - Main application."""
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from finops_common import Permission, Settings, create_app, get_logger, require_permission

logger = get_logger(__name__)

settings = Settings(
    service_name="tenant-service",
    service_version="1.0.0",
    port=8002,
)

app = create_app(
    title="FinOps Tenant Service",
    version="1.0.0",
    description="Tenant, Organization, and Workspace Management Service",
    settings=settings,
)

router = APIRouter(prefix="/api/v1", tags=["Tenants"])


# Models
class OrganizationCreate(BaseModel):
    """Organization creation request."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = None


class Organization(BaseModel):
    """Organization model."""

    id: str
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    created_at: str
    status: str = "active"


class TenantCreate(BaseModel):
    """Tenant creation request."""

    org_id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cloud_accounts: List[str] = Field(default_factory=list)


class Tenant(BaseModel):
    """Tenant model."""

    id: str
    org_id: str
    name: str
    description: Optional[str] = None
    cloud_accounts: List[str]
    created_at: str
    status: str = "active"


# Organization endpoints
@router.post("/organizations", response_model=Organization, status_code=status.HTTP_201_CREATED)
@require_permission(Permission.TENANTS_WRITE)
async def create_organization(org: OrganizationCreate):
    """Create a new organization."""
    logger.info(f"Creating organization: {org.name}")
    
    # TODO: Save to database
    from datetime import datetime
    
    return Organization(
        id=f"org-{uuid4()}",
        name=org.name,
        description=org.description,
        industry=org.industry,
        created_at=datetime.utcnow().isoformat(),
        status="active",
    )


@router.get("/organizations", response_model=List[Organization])
@require_permission(Permission.TENANTS_READ)
async def list_organizations():
    """List all organizations."""
    logger.info("Listing organizations")
    
    # TODO: Query from database
    return []


@router.get("/organizations/{org_id}", response_model=Organization)
@require_permission(Permission.TENANTS_READ)
async def get_organization(org_id: str):
    """Get organization by ID."""
    logger.info(f"Getting organization: {org_id}")
    
    # TODO: Query from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Organization {org_id} not found",
    )


@router.put("/organizations/{org_id}", response_model=Organization)
@require_permission(Permission.TENANTS_WRITE)
async def update_organization(org_id: str, org: OrganizationCreate):
    """Update organization."""
    logger.info(f"Updating organization: {org_id}")
    
    # TODO: Update in database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Organization {org_id} not found",
    )


@router.delete("/organizations/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission(Permission.TENANTS_WRITE)
async def delete_organization(org_id: str):
    """Delete organization (soft delete)."""
    logger.info(f"Deleting organization: {org_id}")
    
    # TODO: Soft delete in database
    return None


# Tenant endpoints
@router.post("/tenants", response_model=Tenant, status_code=status.HTTP_201_CREATED)
@require_permission(Permission.TENANTS_WRITE)
async def create_tenant(tenant: TenantCreate):
    """Create a new tenant."""
    logger.info(f"Creating tenant: {tenant.name} for org: {tenant.org_id}")
    
    # TODO: Save to database
    from datetime import datetime
    
    return Tenant(
        id=f"tenant-{uuid4()}",
        org_id=tenant.org_id,
        name=tenant.name,
        description=tenant.description,
        cloud_accounts=tenant.cloud_accounts,
        created_at=datetime.utcnow().isoformat(),
        status="active",
    )


@router.get("/tenants", response_model=List[Tenant])
@require_permission(Permission.TENANTS_READ)
async def list_tenants(org_id: Optional[str] = None):
    """List tenants, optionally filtered by organization."""
    logger.info(f"Listing tenants for org: {org_id}")
    
    # TODO: Query from database
    return []


@router.get("/tenants/{tenant_id}", response_model=Tenant)
@require_permission(Permission.TENANTS_READ)
async def get_tenant(tenant_id: str):
    """Get tenant by ID."""
    logger.info(f"Getting tenant: {tenant_id}")
    
    # TODO: Query from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Tenant {tenant_id} not found",
    )


app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Tenant service starting up")
    # TODO: Initialize database connection
    # TODO: Run migrations


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Tenant service shutting down")
    # TODO: Close database connections


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
