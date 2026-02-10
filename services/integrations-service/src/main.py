"""Integrations Service - Main application."""
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

from crud import DeliveryManager, IntegrationCRUD
from database import close_db, get_db, init_db
from models import DeliveryStatus, Integration, IntegrationDelivery, IntegrationType
from providers import get_provider

logger = get_logger(__name__)

settings = Settings(
    service_name="integrations-service",
    service_version="1.0.0",
    port=8011,
)

app = create_app(
    title="FinOps Integrations Service",
    version="1.0.0",
    description="Integration and Delivery Management Service",
    settings=settings,
)

router = APIRouter(prefix="/api/v1", tags=["Integrations"])


# ============================================================================
# Pydantic Models
# ============================================================================

# Integration Models
class IntegrationCreate(BaseModel):
    """Integration creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    integration_type: IntegrationType
    config: dict = Field(default_factory=dict)
    credentials: Optional[dict] = None


class IntegrationUpdate(BaseModel):
    """Integration update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    config: Optional[dict] = None
    credentials: Optional[dict] = None
    is_active: Optional[bool] = None


class IntegrationResponse(BaseModel):
    """Integration response."""
    id: str
    org_id: str
    name: str
    integration_type: IntegrationType
    config: dict
    is_active: bool
    is_verified: bool
    last_verified_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    failure_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Delivery Models
class DeliveryCreate(BaseModel):
    """Delivery creation request."""
    integration_id: str
    payload: dict
    workflow_execution_id: Optional[str] = None
    workflow_step_id: Optional[str] = None


class DeliveryResponse(BaseModel):
    """Delivery response."""
    id: str
    integration_id: str
    org_id: str
    workflow_execution_id: Optional[str] = None
    workflow_step_id: Optional[str] = None
    status: DeliveryStatus
    payload: dict
    response: Optional[dict] = None
    error_message: Optional[str] = None
    http_status: Optional[int] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    attempts: int
    max_attempts: int
    next_retry_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestIntegrationRequest(BaseModel):
    """Test integration request."""
    payload: Optional[dict] = None


# ============================================================================
# Event Handlers
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    await init_db()
    logger.info("Integrations service started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await close_db()
    logger.info("Integrations service shutdown")


# ============================================================================
# Integration Endpoints
# ============================================================================

@router.post("/integrations", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    data: IntegrationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
    user_id: Optional[str] = Depends(get_user_id),
):
    """Create a new integration."""
    try:
        integration = await IntegrationCRUD.create(
            db=db,
            org_id=org_id,
            name=data.name,
            integration_type=data.integration_type,
            config=data.config,
            credentials=data.credentials,
            created_by=user_id
        )
        await db.commit()
        
        logger.info(f"Created integration {integration.id} for org {org_id}")
        
        return integration
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/integrations", response_model=List[IntegrationResponse])
async def list_integrations(
    integration_type: Optional[IntegrationType] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
):
    """List integrations for organization."""
    integrations = await IntegrationCRUD.list(
        db=db,
        org_id=org_id,
        integration_type=integration_type,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    return integrations


@router.get("/integrations/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    integration_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
):
    """Get integration by ID."""
    integration = await IntegrationCRUD.get(db, integration_id, org_id)
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration {integration_id} not found"
        )
    
    return integration


@router.put("/integrations/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: str,
    data: IntegrationUpdate,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
    user_id: Optional[str] = Depends(get_user_id),
):
    """Update integration."""
    try:
        integration = await IntegrationCRUD.update(
            db=db,
            integration_id=integration_id,
            org_id=org_id,
            name=data.name,
            config=data.config,
            credentials=data.credentials,
            is_active=data.is_active,
            updated_by=user_id
        )
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration {integration_id} not found"
            )
        
        await db.commit()
        
        return integration
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/integrations/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
):
    """Delete (deactivate) integration."""
    try:
        success = await IntegrationCRUD.delete(db, integration_id, org_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration {integration_id} not found"
            )
        
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/integrations/{integration_id}/verify")
async def verify_integration(
    integration_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
):
    """Verify integration configuration."""
    try:
        integration = await IntegrationCRUD.get(db, integration_id, org_id)
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration {integration_id} not found"
            )
        
        # Get provider and verify
        provider = get_provider(
            integration_type=integration.integration_type,
            config=integration.config,
            credentials=integration.credentials
        )
        
        response = await provider.verify()
        
        # Update verification status
        await IntegrationCRUD.update_verification(
            db=db,
            integration_id=integration_id,
            org_id=org_id,
            is_verified=response.success
        )
        await db.commit()
        
        return {
            "success": response.success,
            "error_message": response.error_message,
            "response": response.response_data
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error verifying integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/integrations/{integration_id}/test")
async def test_integration(
    integration_id: str,
    request_data: TestIntegrationRequest,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
):
    """Test integration with sample payload."""
    try:
        integration = await IntegrationCRUD.get(db, integration_id, org_id)
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration {integration_id} not found"
            )
        
        # Get provider and test
        provider = get_provider(
            integration_type=integration.integration_type,
            config=integration.config,
            credentials=integration.credentials
        )
        
        response = await provider.test(payload=request_data.payload)
        
        return {
            "success": response.success,
            "error_message": response.error_message,
            "response": response.response_data,
            "duration_ms": response.duration_ms
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# Delivery Endpoints
# ============================================================================

@router.post("/deliveries", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    data: DeliveryCreate,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
):
    """Send via integration and create delivery record."""
    try:
        delivery = await DeliveryManager.send(
            db=db,
            integration_id=data.integration_id,
            org_id=org_id,
            payload=data.payload,
            workflow_execution_id=data.workflow_execution_id,
            workflow_step_id=data.workflow_step_id
        )
        await db.commit()
        
        return delivery
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating delivery: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/deliveries", response_model=List[DeliveryResponse])
async def list_deliveries(
    integration_id: Optional[str] = None,
    status: Optional[DeliveryStatus] = None,
    workflow_execution_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
):
    """List delivery attempts."""
    deliveries = await DeliveryManager.list_deliveries(
        db=db,
        org_id=org_id,
        integration_id=integration_id,
        status=status,
        workflow_execution_id=workflow_execution_id,
        skip=skip,
        limit=limit
    )
    return deliveries


@router.get("/deliveries/{delivery_id}", response_model=DeliveryResponse)
async def get_delivery(
    delivery_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
):
    """Get delivery by ID."""
    delivery = await DeliveryManager.get_delivery(db, delivery_id, org_id)
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Delivery {delivery_id} not found"
        )
    
    return delivery


@router.post("/deliveries/{delivery_id}/retry")
async def retry_delivery(
    delivery_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id),
):
    """Manually retry a failed delivery."""
    try:
        delivery = await DeliveryManager.get_delivery(db, delivery_id, org_id)
        
        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Delivery {delivery_id} not found"
            )
        
        if delivery.status not in [DeliveryStatus.FAILED, DeliveryStatus.RETRYING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Delivery is in {delivery.status} status and cannot be retried"
            )
        
        success = await DeliveryManager.attempt_delivery(db, delivery_id, org_id)
        await db.commit()
        
        # Refresh to get updated status
        await db.refresh(delivery)
        
        return {
            "success": success,
            "delivery": DeliveryResponse.from_orm(delivery)
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error retrying delivery: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# Background Tasks Endpoint (for retry worker)
# ============================================================================

@router.post("/internal/retry-pending")
async def retry_pending_deliveries(
    db: AsyncSession = Depends(get_db),
):
    """
    Retry pending deliveries (internal endpoint for background worker).
    
    This should be called periodically by a cron job or background worker.
    """
    try:
        retried = await DeliveryManager.retry_failed_deliveries(db)
        await db.commit()
        
        return {
            "retried": retried,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error retrying pending deliveries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Register router
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
