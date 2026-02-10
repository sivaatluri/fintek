"""CRUD operations for cloud accounts."""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CloudAccount, CloudProvider

from .audit import create_audit_log


class CloudAccountCRUD:
    """CRUD operations for cloud accounts."""

    @staticmethod
    async def create(
        db: AsyncSession,
        org_id: str,
        name: str,
        provider: CloudProvider,
        account_id: str,
        tenant_id: Optional[str] = None,
        account_name: Optional[str] = None,
        credentials: Optional[dict] = None,
        settings: Optional[dict] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> CloudAccount:
        """Create a new cloud account."""
        cloud_account_id = str(uuid4())
        
        cloud_account = CloudAccount(
            id=cloud_account_id,
            org_id=org_id,
            tenant_id=tenant_id,
            name=name,
            provider=provider,
            account_id=account_id,
            account_name=account_name,
            credentials=credentials or {},
            settings=settings or {},
            is_active=True,
            is_connected=False,
            created_by=user_id,
            updated_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(cloud_account)
        await db.flush()
        
        # Create audit log
        await create_audit_log(
            db=db,
            entity_type="cloud_account",
            entity_id=cloud_account_id,
            action="create",
            org_id=org_id,
            user_id=user_id,
            changes={"new": {
                "name": name,
                "provider": provider.value,
                "account_id": account_id,
                "tenant_id": tenant_id,
            }},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )
        
        return cloud_account

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        cloud_account_id: str,
        org_id: str,
    ) -> Optional[CloudAccount]:
        """Get cloud account by ID with org_id enforcement."""
        result = await db.execute(
            select(CloudAccount).where(
                CloudAccount.id == cloud_account_id,
                CloudAccount.org_id == org_id,
                CloudAccount.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        org_id: str,
        tenant_id: Optional[str] = None,
        provider: Optional[CloudProvider] = None,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[CloudAccount]:
        """List cloud accounts for an organization with pagination."""
        query = select(CloudAccount).where(CloudAccount.org_id == org_id)
        
        if tenant_id is not None:
            query = query.where(CloudAccount.tenant_id == tenant_id)
        
        if provider is not None:
            query = query.where(CloudAccount.provider == provider)
        
        if is_active is not None:
            query = query.where(CloudAccount.is_active == is_active)
        
        query = query.order_by(CloudAccount.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count(
        db: AsyncSession,
        org_id: str,
        tenant_id: Optional[str] = None,
        provider: Optional[CloudProvider] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count cloud accounts for an organization."""
        query = select(func.count(CloudAccount.id)).where(CloudAccount.org_id == org_id)
        
        if tenant_id is not None:
            query = query.where(CloudAccount.tenant_id == tenant_id)
        
        if provider is not None:
            query = query.where(CloudAccount.provider == provider)
        
        if is_active is not None:
            query = query.where(CloudAccount.is_active == is_active)
        
        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def update(
        db: AsyncSession,
        cloud_account_id: str,
        org_id: str,
        name: Optional[str] = None,
        tenant_id: Optional[str] = None,
        account_name: Optional[str] = None,
        credentials: Optional[dict] = None,
        settings: Optional[dict] = None,
        is_connected: Optional[bool] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[CloudAccount]:
        """Update cloud account with org_id enforcement."""
        result = await db.execute(
            select(CloudAccount).where(
                CloudAccount.id == cloud_account_id,
                CloudAccount.org_id == org_id,
                CloudAccount.is_active == True,
            )
        )
        cloud_account = result.scalar_one_or_none()
        
        if not cloud_account:
            return None
        
        changes = {"old": {}, "new": {}}
        
        if name is not None and name != cloud_account.name:
            changes["old"]["name"] = cloud_account.name
            changes["new"]["name"] = name
            cloud_account.name = name
        
        if tenant_id is not None and tenant_id != cloud_account.tenant_id:
            changes["old"]["tenant_id"] = cloud_account.tenant_id
            changes["new"]["tenant_id"] = tenant_id
            cloud_account.tenant_id = tenant_id
        
        if account_name is not None and account_name != cloud_account.account_name:
            changes["old"]["account_name"] = cloud_account.account_name
            changes["new"]["account_name"] = account_name
            cloud_account.account_name = account_name
        
        if credentials is not None and credentials != cloud_account.credentials:
            changes["old"]["credentials"] = "***"  # Don't log credentials
            changes["new"]["credentials"] = "***"
            cloud_account.credentials = credentials
        
        if settings is not None and settings != cloud_account.settings:
            changes["old"]["settings"] = cloud_account.settings
            changes["new"]["settings"] = settings
            cloud_account.settings = settings
        
        if is_connected is not None and is_connected != cloud_account.is_connected:
            changes["old"]["is_connected"] = cloud_account.is_connected
            changes["new"]["is_connected"] = is_connected
            cloud_account.is_connected = is_connected
        
        cloud_account.updated_by = user_id
        cloud_account.updated_at = datetime.utcnow()
        
        await db.flush()
        
        # Create audit log if there were changes
        if changes["old"]:
            await create_audit_log(
                db=db,
                entity_type="cloud_account",
                entity_id=cloud_account_id,
                action="update",
                org_id=org_id,
                user_id=user_id,
                changes=changes,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
            )
        
        return cloud_account

    @staticmethod
    async def delete(
        db: AsyncSession,
        cloud_account_id: str,
        org_id: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Soft delete cloud account with org_id enforcement."""
        result = await db.execute(
            select(CloudAccount).where(
                CloudAccount.id == cloud_account_id,
                CloudAccount.org_id == org_id,
                CloudAccount.is_active == True,
            )
        )
        cloud_account = result.scalar_one_or_none()
        
        if not cloud_account:
            return False
        
        cloud_account.is_active = False
        cloud_account.updated_by = user_id
        cloud_account.updated_at = datetime.utcnow()
        
        await db.flush()
        
        # Create audit log
        await create_audit_log(
            db=db,
            entity_type="cloud_account",
            entity_id=cloud_account_id,
            action="delete",
            org_id=org_id,
            user_id=user_id,
            changes={"old": {"is_active": True}, "new": {"is_active": False}},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )
        
        return True
