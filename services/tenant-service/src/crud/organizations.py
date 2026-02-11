"""CRUD operations for organizations."""
import re
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Organization

from .audit import create_audit_log


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


class OrganizationCRUD:
    """CRUD operations for organizations."""

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        description: Optional[str] = None,
        industry: Optional[str] = None,
        settings: Optional[dict] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Organization:
        """Create a new organization."""
        org_id = str(uuid4())
        slug = slugify(name)
        
        # Ensure slug is unique
        counter = 1
        original_slug = slug
        while True:
            result = await db.execute(
                select(Organization).where(Organization.slug == slug)
            )
            if result.scalar_one_or_none() is None:
                break
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        org = Organization(
            id=org_id,
            name=name,
            slug=slug,
            description=description,
            industry=industry,
            settings=settings or {},
            is_active=True,
            created_by=user_id,
            updated_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(org)
        await db.flush()
        
        # Create audit log
        await create_audit_log(
            db=db,
            entity_type="organization",
            entity_id=org_id,
            action="create",
            org_id=org_id,
            user_id=user_id,
            changes={"new": {"name": name, "slug": slug}},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )
        
        return org

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        org_id: str,
    ) -> Optional[Organization]:
        """Get organization by ID."""
        result = await db.execute(
            select(Organization).where(
                Organization.id == org_id,
                Organization.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(
        db: AsyncSession,
        slug: str,
    ) -> Optional[Organization]:
        """Get organization by slug."""
        result = await db.execute(
            select(Organization).where(
                Organization.slug == slug,
                Organization.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[Organization]:
        """List organizations with pagination."""
        query = select(Organization)
        
        if is_active is not None:
            query = query.where(Organization.is_active == is_active)
        
        query = query.order_by(Organization.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count(
        db: AsyncSession,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count organizations."""
        query = select(func.count(Organization.id))
        
        if is_active is not None:
            query = query.where(Organization.is_active == is_active)
        
        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def update(
        db: AsyncSession,
        org_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        industry: Optional[str] = None,
        settings: Optional[dict] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[Organization]:
        """Update organization."""
        result = await db.execute(
            select(Organization).where(
                Organization.id == org_id,
                Organization.is_active == True,
            )
        )
        org = result.scalar_one_or_none()
        
        if not org:
            return None
        
        changes = {"old": {}, "new": {}}
        
        if name is not None and name != org.name:
            changes["old"]["name"] = org.name
            changes["new"]["name"] = name
            org.name = name
            
            # Update slug if name changed
            new_slug = slugify(name)
            if new_slug != org.slug:
                changes["old"]["slug"] = org.slug
                changes["new"]["slug"] = new_slug
                org.slug = new_slug
        
        if description is not None and description != org.description:
            changes["old"]["description"] = org.description
            changes["new"]["description"] = description
            org.description = description
        
        if industry is not None and industry != org.industry:
            changes["old"]["industry"] = org.industry
            changes["new"]["industry"] = industry
            org.industry = industry
        
        if settings is not None and settings != org.settings:
            changes["old"]["settings"] = org.settings
            changes["new"]["settings"] = settings
            org.settings = settings
        
        org.updated_by = user_id
        org.updated_at = datetime.utcnow()
        
        await db.flush()
        
        # Create audit log if there were changes
        if changes["old"]:
            await create_audit_log(
                db=db,
                entity_type="organization",
                entity_id=org_id,
                action="update",
                org_id=org_id,
                user_id=user_id,
                changes=changes,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
            )
        
        return org

    @staticmethod
    async def delete(
        db: AsyncSession,
        org_id: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Soft delete organization."""
        result = await db.execute(
            select(Organization).where(
                Organization.id == org_id,
                Organization.is_active == True,
            )
        )
        org = result.scalar_one_or_none()
        
        if not org:
            return False
        
        org.is_active = False
        org.updated_by = user_id
        org.updated_at = datetime.utcnow()
        
        await db.flush()
        
        # Create audit log
        await create_audit_log(
            db=db,
            entity_type="organization",
            entity_id=org_id,
            action="delete",
            org_id=org_id,
            user_id=user_id,
            changes={"old": {"is_active": True}, "new": {"is_active": False}},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )
        
        return True
