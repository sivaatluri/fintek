"""Tenant Service - Main application."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from finops_common import (
    Permission,
    Settings,
    create_app,
    get_logger,
    get_org_id,
    get_request_id,
    get_user_id,
    require_permission,
)

from crud import CloudAccountCRUD, OrganizationCRUD, PersonaViewCRUD, TenantCRUD
from database import close_db, get_db, init_db
from models import CloudProvider

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


# ============================================================================
# Pydantic Models
# ============================================================================

# Organization Models
class OrganizationCreate(BaseModel):
    """Organization creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = None
    settings: Optional[dict] = None


class OrganizationUpdate(BaseModel):
    """Organization update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = None
    settings: Optional[dict] = None


class OrganizationResponse(BaseModel):
    """Organization response."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    industry: Optional[str] = None
    settings: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Tenant Models
class TenantCreate(BaseModel):
    """Tenant creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[dict] = None


class TenantUpdate(BaseModel):
    """Tenant update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    settings: Optional[dict] = None


class TenantResponse(BaseModel):
    """Tenant response."""
    id: str
    org_id: str
    name: str
    slug: str
    description: Optional[str] = None
    settings: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Cloud Account Models
class CloudAccountCreate(BaseModel):
    """Cloud account creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    provider: CloudProvider
    account_id: str = Field(..., min_length=1, max_length=255)
    tenant_id: Optional[str] = None
    account_name: Optional[str] = None
    credentials: Optional[dict] = None
    settings: Optional[dict] = None


class CloudAccountUpdate(BaseModel):
    """Cloud account update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    tenant_id: Optional[str] = None
    account_name: Optional[str] = None
    credentials: Optional[dict] = None
    settings: Optional[dict] = None
    is_connected: Optional[bool] = None


class CloudAccountResponse(BaseModel):
    """Cloud account response."""
    id: str
    org_id: str
    tenant_id: Optional[str] = None
    name: str
    provider: CloudProvider
    account_id: str
    account_name: Optional[str] = None
    settings: dict
    is_active: bool
    is_connected: bool
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Persona View Models
class PersonaViewCreate(BaseModel):
    """Persona view creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    persona: str = Field(..., min_length=1, max_length=50)
    config: dict
    description: Optional[str] = None
    is_default: bool = False
    is_shared: bool = False


class PersonaViewUpdate(BaseModel):
    """Persona view update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[dict] = None
    is_default: Optional[bool] = None
    is_shared: Optional[bool] = None


class PersonaViewResponse(BaseModel):
    """Persona view response."""
    id: str
    org_id: str
    name: str
    slug: str
    description: Optional[str] = None
    persona: str
    config: dict
    is_default: bool
    is_shared: bool
    owner_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Organization Endpoints
# ============================================================================

@router.post("/orgs", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
@require_permission(Permission.TENANTS_WRITE)
async def create_organization(
    org_data: OrganizationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Create a new organization."""
    logger.info(f"Creating organization: {org_data.name}")
    
    try:
        org = await OrganizationCRUD.create(
            db=db,
            name=org_data.name,
            description=org_data.description,
            industry=org_data.industry,
            settings=org_data.settings,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        await db.commit()
        return org
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create organization",
        )


@router.get("/orgs", response_model=List[OrganizationResponse])
@require_permission(Permission.TENANTS_READ)
async def list_organizations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all organizations."""
    logger.info("Listing organizations")
    
    orgs = await OrganizationCRUD.list(db=db, skip=skip, limit=limit, is_active=True)
    return orgs


@router.get("/orgs/{org_id}", response_model=OrganizationResponse)
@require_permission(Permission.TENANTS_READ)
async def get_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get organization by ID."""
    logger.info(f"Getting organization: {org_id}")
    
    org = await OrganizationCRUD.get_by_id(db=db, org_id=org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found",
        )
    return org


@router.put("/orgs/{org_id}", response_model=OrganizationResponse)
@require_permission(Permission.TENANTS_WRITE)
async def update_organization(
    org_id: str,
    org_data: OrganizationUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update organization."""
    logger.info(f"Updating organization: {org_id}")
    
    try:
        org = await OrganizationCRUD.update(
            db=db,
            org_id=org_id,
            name=org_data.name,
            description=org_data.description,
            industry=org_data.industry,
            settings=org_data.settings,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization {org_id} not found",
            )
        
        await db.commit()
        return org
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update organization",
        )


@router.delete("/orgs/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission(Permission.TENANTS_WRITE)
async def delete_organization(
    org_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Delete organization (soft delete)."""
    logger.info(f"Deleting organization: {org_id}")
    
    try:
        success = await OrganizationCRUD.delete(
            db=db,
            org_id=org_id,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization {org_id} not found",
            )
        
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete organization",
        )


# ============================================================================
# Tenant Endpoints
# ============================================================================

@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
@require_permission(Permission.TENANTS_WRITE)
async def create_tenant(
    tenant_data: TenantCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Create a new tenant."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Creating tenant: {tenant_data.name} for org: {org_id}")
    
    try:
        tenant = await TenantCRUD.create(
            db=db,
            org_id=org_id,
            name=tenant_data.name,
            description=tenant_data.description,
            settings=tenant_data.settings,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        await db.commit()
        return tenant
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tenant",
        )


@router.get("/tenants", response_model=List[TenantResponse])
@require_permission(Permission.TENANTS_READ)
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List tenants for the organization."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Listing tenants for org: {org_id}")
    
    tenants = await TenantCRUD.list(db=db, org_id=org_id, skip=skip, limit=limit, is_active=True)
    return tenants


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
@require_permission(Permission.TENANTS_READ)
async def get_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get tenant by ID."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Getting tenant: {tenant_id}")
    
    tenant = await TenantCRUD.get_by_id(db=db, tenant_id=tenant_id, org_id=org_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found",
        )
    return tenant


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
@require_permission(Permission.TENANTS_WRITE)
async def update_tenant(
    tenant_id: str,
    tenant_data: TenantUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update tenant."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Updating tenant: {tenant_id}")
    
    try:
        tenant = await TenantCRUD.update(
            db=db,
            tenant_id=tenant_id,
            org_id=org_id,
            name=tenant_data.name,
            description=tenant_data.description,
            settings=tenant_data.settings,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant {tenant_id} not found",
            )
        
        await db.commit()
        return tenant
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tenant",
        )


@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission(Permission.TENANTS_WRITE)
async def delete_tenant(
    tenant_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Delete tenant (soft delete)."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Deleting tenant: {tenant_id}")
    
    try:
        success = await TenantCRUD.delete(
            db=db,
            tenant_id=tenant_id,
            org_id=org_id,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant {tenant_id} not found",
            )
        
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete tenant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tenant",
        )


# ============================================================================
# Cloud Account Endpoints
# ============================================================================

@router.post("/cloud-accounts", response_model=CloudAccountResponse, status_code=status.HTTP_201_CREATED)
@require_permission(Permission.TENANTS_WRITE)
async def create_cloud_account(
    account_data: CloudAccountCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Create a new cloud account."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Creating cloud account: {account_data.name} for org: {org_id}")
    
    try:
        account = await CloudAccountCRUD.create(
            db=db,
            org_id=org_id,
            name=account_data.name,
            provider=account_data.provider,
            account_id=account_data.account_id,
            tenant_id=account_data.tenant_id,
            account_name=account_data.account_name,
            credentials=account_data.credentials,
            settings=account_data.settings,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        await db.commit()
        return account
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create cloud account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create cloud account",
        )


@router.get("/cloud-accounts", response_model=List[CloudAccountResponse])
@require_permission(Permission.TENANTS_READ)
async def list_cloud_accounts(
    tenant_id: Optional[str] = None,
    provider: Optional[CloudProvider] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List cloud accounts for the organization."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Listing cloud accounts for org: {org_id}")
    
    accounts = await CloudAccountCRUD.list(
        db=db,
        org_id=org_id,
        tenant_id=tenant_id,
        provider=provider,
        skip=skip,
        limit=limit,
        is_active=True,
    )
    return accounts


@router.get("/cloud-accounts/{account_id}", response_model=CloudAccountResponse)
@require_permission(Permission.TENANTS_READ)
async def get_cloud_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get cloud account by ID."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Getting cloud account: {account_id}")
    
    account = await CloudAccountCRUD.get_by_id(db=db, cloud_account_id=account_id, org_id=org_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cloud account {account_id} not found",
        )
    return account


@router.put("/cloud-accounts/{account_id}", response_model=CloudAccountResponse)
@require_permission(Permission.TENANTS_WRITE)
async def update_cloud_account(
    account_id: str,
    account_data: CloudAccountUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update cloud account."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Updating cloud account: {account_id}")
    
    try:
        account = await CloudAccountCRUD.update(
            db=db,
            cloud_account_id=account_id,
            org_id=org_id,
            name=account_data.name,
            tenant_id=account_data.tenant_id,
            account_name=account_data.account_name,
            credentials=account_data.credentials,
            settings=account_data.settings,
            is_connected=account_data.is_connected,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cloud account {account_id} not found",
            )
        
        await db.commit()
        return account
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update cloud account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cloud account",
        )


@router.delete("/cloud-accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission(Permission.TENANTS_WRITE)
async def delete_cloud_account(
    account_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Delete cloud account (soft delete)."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Deleting cloud account: {account_id}")
    
    try:
        success = await CloudAccountCRUD.delete(
            db=db,
            cloud_account_id=account_id,
            org_id=org_id,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cloud account {account_id} not found",
            )
        
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete cloud account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete cloud account",
        )


# ============================================================================
# Persona View Endpoints
# ============================================================================

@router.post("/views", response_model=PersonaViewResponse, status_code=status.HTTP_201_CREATED)
@require_permission(Permission.TENANTS_WRITE)
async def create_persona_view(
    view_data: PersonaViewCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Create a new persona view."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Creating persona view: {view_data.name} for org: {org_id}")
    
    try:
        view = await PersonaViewCRUD.create(
            db=db,
            org_id=org_id,
            name=view_data.name,
            persona=view_data.persona,
            config=view_data.config,
            description=view_data.description,
            is_default=view_data.is_default,
            is_shared=view_data.is_shared,
            owner_id=get_user_id(),
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        await db.commit()
        return view
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create persona view: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create persona view",
        )


@router.get("/views", response_model=List[PersonaViewResponse])
@require_permission(Permission.TENANTS_READ)
async def list_persona_views(
    persona: Optional[str] = None,
    is_default: Optional[bool] = None,
    is_shared: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List persona views for the organization."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Listing persona views for org: {org_id}")
    
    views = await PersonaViewCRUD.list(
        db=db,
        org_id=org_id,
        persona=persona,
        is_default=is_default,
        is_shared=is_shared,
        skip=skip,
        limit=limit,
        is_active=True,
    )
    return views


@router.get("/views/{view_id}", response_model=PersonaViewResponse)
@require_permission(Permission.TENANTS_READ)
async def get_persona_view(
    view_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get persona view by ID."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Getting persona view: {view_id}")
    
    view = await PersonaViewCRUD.get_by_id(db=db, view_id=view_id, org_id=org_id)
    if not view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona view {view_id} not found",
        )
    return view


@router.put("/views/{view_id}", response_model=PersonaViewResponse)
@require_permission(Permission.TENANTS_WRITE)
async def update_persona_view(
    view_id: str,
    view_data: PersonaViewUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Update persona view."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Updating persona view: {view_id}")
    
    try:
        view = await PersonaViewCRUD.update(
            db=db,
            view_id=view_id,
            org_id=org_id,
            name=view_data.name,
            description=view_data.description,
            config=view_data.config,
            is_default=view_data.is_default,
            is_shared=view_data.is_shared,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        if not view:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Persona view {view_id} not found",
            )
        
        await db.commit()
        return view
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update persona view: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update persona view",
        )


@router.delete("/views/{view_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission(Permission.TENANTS_WRITE)
async def delete_persona_view(
    view_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Delete persona view (soft delete)."""
    org_id = get_org_id()
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID required in headers",
        )
    
    logger.info(f"Deleting persona view: {view_id}")
    
    try:
        success = await PersonaViewCRUD.delete(
            db=db,
            view_id=view_id,
            org_id=org_id,
            user_id=get_user_id(),
            request_id=get_request_id(),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Persona view {view_id} not found",
            )
        
        await db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete persona view: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete persona view",
        )


app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Tenant service starting up")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Tenant service shutting down")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
