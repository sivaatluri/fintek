"""Delivery manager with retry logic and persistence."""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finops_common import get_logger

from ..models import DeliveryStatus, Integration, IntegrationDelivery, IntegrationType
from ..providers import get_provider
from .integrations import IntegrationCRUD

logger = get_logger(__name__)


class DeliveryManager:
    """Manages integration deliveries with retry logic."""

    @staticmethod
    async def create_delivery(
        db: AsyncSession,
        integration_id: str,
        org_id: str,
        payload: dict,
        workflow_execution_id: Optional[str] = None,
        workflow_step_id: Optional[str] = None,
        max_attempts: int = 3
    ) -> IntegrationDelivery:
        """Create a new delivery record."""
        delivery = IntegrationDelivery(
            id=str(uuid.uuid4()),
            integration_id=integration_id,
            org_id=org_id,
            workflow_execution_id=workflow_execution_id,
            workflow_step_id=workflow_step_id,
            status=DeliveryStatus.PENDING,
            payload=payload,
            max_attempts=max_attempts,
            attempts=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(delivery)
        await db.flush()
        await db.refresh(delivery)
        
        logger.info(f"Created delivery {delivery.id} for integration {integration_id}")
        
        return delivery

    @staticmethod
    async def send(
        db: AsyncSession,
        integration_id: str,
        org_id: str,
        payload: dict,
        workflow_execution_id: Optional[str] = None,
        workflow_step_id: Optional[str] = None
    ) -> IntegrationDelivery:
        """
        Send payload via integration and persist delivery.
        
        This creates a delivery record and attempts to send immediately.
        If it fails, it will be retried by the retry worker.
        """
        # Get integration
        integration = await IntegrationCRUD.get(db, integration_id, org_id)
        
        if not integration:
            raise ValueError(f"Integration {integration_id} not found")
        
        if not integration.is_active:
            raise ValueError(f"Integration {integration_id} is not active")
        
        # Create delivery record
        delivery = await DeliveryManager.create_delivery(
            db=db,
            integration_id=integration_id,
            org_id=org_id,
            payload=payload,
            workflow_execution_id=workflow_execution_id,
            workflow_step_id=workflow_step_id
        )
        
        # Attempt delivery
        await DeliveryManager.attempt_delivery(db, delivery.id, org_id)
        
        # Refresh to get updated status
        await db.refresh(delivery)
        
        return delivery

    @staticmethod
    async def attempt_delivery(
        db: AsyncSession,
        delivery_id: str,
        org_id: str
    ) -> bool:
        """
        Attempt to deliver a message.
        
        Returns:
            True if delivery succeeded, False otherwise
        """
        # Get delivery
        result = await db.execute(
            select(IntegrationDelivery).where(
                IntegrationDelivery.id == delivery_id,
                IntegrationDelivery.org_id == org_id
            )
        )
        delivery = result.scalar_one_or_none()
        
        if not delivery:
            logger.error(f"Delivery {delivery_id} not found")
            return False
        
        # Get integration
        integration = await IntegrationCRUD.get(db, delivery.integration_id, org_id)
        
        if not integration:
            logger.error(f"Integration {delivery.integration_id} not found")
            delivery.status = DeliveryStatus.FAILED
            delivery.error_message = "Integration not found"
            await db.flush()
            return False
        
        # Increment attempt counter
        delivery.attempts += 1
        delivery.status = DeliveryStatus.SENT
        delivery.sent_at = datetime.utcnow()
        delivery.updated_at = datetime.utcnow()
        
        start_time = datetime.utcnow()
        
        try:
            # Get provider and send
            provider = get_provider(
                integration_type=integration.integration_type,
                config=integration.config,
                credentials=integration.credentials
            )
            
            response = await provider.send(delivery.payload)
            
            # Update delivery with response
            delivery.response = response.response_data
            delivery.http_status = response.http_status
            delivery.external_id = response.external_id
            delivery.external_url = response.external_url
            delivery.duration_ms = response.duration_ms or (
                int((datetime.utcnow() - start_time).total_seconds() * 1000)
            )
            
            if response.success:
                delivery.status = DeliveryStatus.DELIVERED
                delivery.delivered_at = datetime.utcnow()
                delivery.error_message = None
                
                # Update integration stats
                await IntegrationCRUD.update_last_used(db, integration.id, org_id)
                await IntegrationCRUD.reset_failure_count(db, integration.id, org_id)
                
                logger.info(f"Delivery {delivery_id} succeeded after {delivery.attempts} attempts")
                
                await db.flush()
                return True
            else:
                delivery.error_message = response.error_message
                
                # Determine if we should retry
                if delivery.attempts < delivery.max_attempts:
                    delivery.status = DeliveryStatus.RETRYING
                    # Exponential backoff: 2^attempts minutes
                    retry_delay = min(2 ** delivery.attempts, 60)  # Max 60 minutes
                    delivery.next_retry_at = datetime.utcnow() + timedelta(minutes=retry_delay)
                    logger.warning(f"Delivery {delivery_id} failed, will retry in {retry_delay} minutes")
                else:
                    delivery.status = DeliveryStatus.FAILED
                    logger.error(f"Delivery {delivery_id} failed after {delivery.attempts} attempts")
                
                # Update integration failure count
                await IntegrationCRUD.increment_failure_count(db, integration.id, org_id)
                
                await db.flush()
                return False
                
        except Exception as e:
            logger.error(f"Delivery {delivery_id} error: {e}")
            
            delivery.error_message = str(e)
            delivery.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Determine if we should retry
            if delivery.attempts < delivery.max_attempts:
                delivery.status = DeliveryStatus.RETRYING
                retry_delay = min(2 ** delivery.attempts, 60)
                delivery.next_retry_at = datetime.utcnow() + timedelta(minutes=retry_delay)
            else:
                delivery.status = DeliveryStatus.FAILED
            
            await IntegrationCRUD.increment_failure_count(db, integration.id, org_id)
            
            await db.flush()
            return False

    @staticmethod
    async def get_delivery(
        db: AsyncSession,
        delivery_id: str,
        org_id: str
    ) -> Optional[IntegrationDelivery]:
        """Get delivery by ID with org enforcement."""
        result = await db.execute(
            select(IntegrationDelivery).where(
                IntegrationDelivery.id == delivery_id,
                IntegrationDelivery.org_id == org_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_deliveries(
        db: AsyncSession,
        org_id: str,
        integration_id: Optional[str] = None,
        status: Optional[DeliveryStatus] = None,
        workflow_execution_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[IntegrationDelivery]:
        """List deliveries with filters and pagination."""
        query = select(IntegrationDelivery).where(IntegrationDelivery.org_id == org_id)
        
        if integration_id:
            query = query.where(IntegrationDelivery.integration_id == integration_id)
        
        if status:
            query = query.where(IntegrationDelivery.status == status)
        
        if workflow_execution_id:
            query = query.where(IntegrationDelivery.workflow_execution_id == workflow_execution_id)
        
        query = query.order_by(IntegrationDelivery.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_pending_retries(
        db: AsyncSession,
        limit: int = 100
    ) -> List[IntegrationDelivery]:
        """Get deliveries that need to be retried."""
        now = datetime.utcnow()
        
        query = select(IntegrationDelivery).where(
            IntegrationDelivery.status == DeliveryStatus.RETRYING,
            IntegrationDelivery.next_retry_at <= now
        ).order_by(IntegrationDelivery.next_retry_at).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def retry_failed_deliveries(db: AsyncSession) -> int:
        """
        Retry deliveries that are due for retry.
        
        This should be called periodically by a background worker.
        
        Returns:
            Number of deliveries retried
        """
        deliveries = await DeliveryManager.get_pending_retries(db)
        
        retried = 0
        for delivery in deliveries:
            success = await DeliveryManager.attempt_delivery(db, delivery.id, delivery.org_id)
            if success or delivery.status == DeliveryStatus.FAILED:
                retried += 1
        
        if retried > 0:
            logger.info(f"Retried {retried} deliveries")
        
        return retried
