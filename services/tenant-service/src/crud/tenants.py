"""CRUD operations for tenants."""
import re
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Tenant

from .audit import create_audit_log


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


class TenantCRUD:
    """CRUD operations for tenants."""

    @staticmethod
    async def create(
        db: AsyncSession,
        org_id: str,
        name: str,
        description: Optional[str] = None,
        settings: Optional[dict] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tenant:
        """Create a new tenant."""
        tenant_id = str(uuid4())
        slug = slugify(name)
        
        # Ensure slug is unique within org
        counter = 1
        original_slug = slug
        while True:
            result = await db.execute(
                select(Tenant).where(
                    Tenant.org_id == org_id,
                    Tenant.slug == slug
                )
            )
            if result.scalar_one_or_none() is None:
                break
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        tenant = Tenant(
            id=tenant_id,
            org_id=org_id,
            name=name,
            slug=slug,
            description=description,
            settings=settings or {},
            is_active=True,
            created_by=user_id,
            updated_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(tenant)
        await db.flush()
        
        # Create audit log
        await create_audit_log(
            db=db,
            entity_type="tenant",
            entity_id=tenant_id,
            action="create",
            org_id=org_id,
            user_id=user_id,
            changes={"new": {"name": name, "slug": slug, "org_id": org_id}},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )
        
        return tenant

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        tenant_id: str,
        org_id: str,
    ) -> Optional[Tenant]:
        """Get tenant by ID with org_id enforcement."""
        result = await db.execute(
            select(Tenant).where(
                Tenant.id == tenant_id,
                Tenant.org_id == org_id,
                Tenant.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(
        db: AsyncSession,
        slug: str,
        org_id: str,
    ) -> Optional[Tenant]:
        """Get tenant by slug with org_id enforcement."""
        result = await db.execute(
            select(Tenant).where(
                Tenant.slug == slug,
                Tenant.org_id == org_id,
                Tenant.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        org_id: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[Tenant]:
        """List tenants for an organization with pagination."""
        query = select(Tenant).where(Tenant.org_id == org_id)
        
        if is_active is not None:
            query = query.where(Tenant.is_active == is_active)
        
        query = query.order_by(Tenant.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count(
        db: AsyncSession,
        org_id: str,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count tenants for an organization."""
        query = select(func.count(Tenant.id)).where(Tenant.org_id == org_id)
        
        if is_active is not None:
            query = query.where(Tenant.is_active == is_active)
        
        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def update(
        db: AsyncSession,
        tenant_id: str,
        org_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        settings: Optional[dict] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[Tenant]:
        """Update tenant with org_id enforcement."""
        result = await db.execute(
            select(Tenant).where(
                Tenant.id == tenant_id,
                Tenant.org_id == org_id,
                Tenant.is_active == True,
            )
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return None
        
        changes = {"old": {}, "new": {}}
        
        if name is not None and name != tenant.name:
            changes["old"]["name"] = tenant.name
            changes["new"]["name"] = name
            tenant.name = name
            
            # Update slug if name changed
            new_slug = slugify(name)
            if new_slug != tenant.slug:
                changes["old"]["slug"] = tenant.slug
                changes["new"]["slug"] = new_slug
                tenant.slug = new_slug
        
        if description is not None and description != tenant.description:
            changes["old"]["description"] = tenant.description
            changes["new"]["description"] = description
            tenant.description = description
        
        if settings is not None and settings != tenant.settings:
            changes["old"]["settings"] = tenant.settings
            changes["new"]["settings"] = settings
            tenant.settings = settings
        
        tenant.updated_by = user_id
        tenant.updated_at = datetime.utcnow()
        
        await db.flush()
        
        # Create audit log if there were changes
        if changes["old"]:
            await create_audit_log(
                db=db,
                entity_type="tenant",
                entity_id=tenant_id,
                action="update",
                org_id=org_id,
                user_id=user_id,
                changes=changes,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
            )
        
        return tenant

    @staticmethod
    async def delete(
        db: AsyncSession,
        tenant_id: str,
        org_id: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Soft delete tenant with org_id enforcement."""
        result = await db.execute(
            select(Tenant).where(
                Tenant.id == tenant_id,
                Tenant.org_id == org_id,
                Tenant.is_active == True,
            )
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return False
        
        tenant.is_active = False
        tenant.updated_by = user_id
        tenant.updated_at = datetime.utcnow()
        
        await db.flush()
        
        # Create audit log
        await create_audit_log(
            db=db,
            entity_type="tenant",
            entity_id=tenant_id,
            action="delete",
            org_id=org_id,
            user_id=user_id,
            changes={"old": {"is_active": True}, "new": {"is_active": False}},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )
        
        return True
