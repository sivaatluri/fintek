"""CRUD operations for integrations."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finops_common import get_logger

from ..models import Integration, IntegrationType

logger = get_logger(__name__)


class IntegrationCRUD:
    """CRUD operations for integrations."""

    @staticmethod
    async def create(
        db: AsyncSession,
        org_id: str,
        name: str,
        integration_type: IntegrationType,
        config: dict,
        credentials: Optional[dict] = None,
        created_by: Optional[str] = None
    ) -> Integration:
        """Create a new integration."""
        integration = Integration(
            id=str(uuid.uuid4()),
            org_id=org_id,
            name=name,
            integration_type=integration_type,
            config=config,
            credentials=credentials,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(integration)
        await db.flush()
        await db.refresh(integration)
        
        logger.info(f"Created integration {integration.id} ({name}) for org {org_id}")
        
        return integration

    @staticmethod
    async def get(db: AsyncSession, integration_id: str, org_id: str) -> Optional[Integration]:
        """Get integration by ID with org enforcement."""
        result = await db.execute(
            select(Integration).where(
                Integration.id == integration_id,
                Integration.org_id == org_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        org_id: str,
        integration_type: Optional[IntegrationType] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Integration]:
        """List integrations with filters and pagination."""
        query = select(Integration).where(Integration.org_id == org_id)
        
        if integration_type is not None:
            query = query.where(Integration.integration_type == integration_type)
        
        if is_active is not None:
            query = query.where(Integration.is_active == is_active)
        
        query = query.order_by(Integration.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession,
        integration_id: str,
        org_id: str,
        name: Optional[str] = None,
        config: Optional[dict] = None,
        credentials: Optional[dict] = None,
        is_active: Optional[bool] = None,
        updated_by: Optional[str] = None
    ) -> Optional[Integration]:
        """Update integration."""
        integration = await IntegrationCRUD.get(db, integration_id, org_id)
        
        if not integration:
            return None
        
        if name is not None:
            integration.name = name
        if config is not None:
            integration.config = config
        if credentials is not None:
            integration.credentials = credentials
        if is_active is not None:
            integration.is_active = is_active
        if updated_by is not None:
            integration.updated_by = updated_by
        
        integration.updated_at = datetime.utcnow()
        
        await db.flush()
        await db.refresh(integration)
        
        logger.info(f"Updated integration {integration_id}")
        
        return integration

    @staticmethod
    async def delete(db: AsyncSession, integration_id: str, org_id: str) -> bool:
        """Soft delete integration."""
        integration = await IntegrationCRUD.get(db, integration_id, org_id)
        
        if not integration:
            return False
        
        integration.is_active = False
        integration.updated_at = datetime.utcnow()
        
        await db.flush()
        
        logger.info(f"Soft deleted integration {integration_id}")
        
        return True

    @staticmethod
    async def update_verification(
        db: AsyncSession,
        integration_id: str,
        org_id: str,
        is_verified: bool
    ) -> Optional[Integration]:
        """Update verification status."""
        integration = await IntegrationCRUD.get(db, integration_id, org_id)
        
        if not integration:
            return None
        
        integration.is_verified = is_verified
        integration.last_verified_at = datetime.utcnow()
        integration.updated_at = datetime.utcnow()
        
        await db.flush()
        await db.refresh(integration)
        
        return integration

    @staticmethod
    async def update_last_used(
        db: AsyncSession,
        integration_id: str,
        org_id: str
    ) -> None:
        """Update last used timestamp."""
        integration = await IntegrationCRUD.get(db, integration_id, org_id)
        
        if integration:
            integration.last_used_at = datetime.utcnow()
            await db.flush()

    @staticmethod
    async def increment_failure_count(
        db: AsyncSession,
        integration_id: str,
        org_id: str
    ) -> None:
        """Increment failure count."""
        integration = await IntegrationCRUD.get(db, integration_id, org_id)
        
        if integration:
            integration.failure_count += 1
            await db.flush()

    @staticmethod
    async def reset_failure_count(
        db: AsyncSession,
        integration_id: str,
        org_id: str
    ) -> None:
        """Reset failure count after successful delivery."""
        integration = await IntegrationCRUD.get(db, integration_id, org_id)
        
        if integration:
            integration.failure_count = 0
            await db.flush()
