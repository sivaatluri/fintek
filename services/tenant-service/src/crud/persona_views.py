"""CRUD operations for persona views."""
import re
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import PersonaView

from .audit import create_audit_log


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


class PersonaViewCRUD:
    """CRUD operations for persona views."""

    @staticmethod
    async def create(
        db: AsyncSession,
        org_id: str,
        name: str,
        persona: str,
        config: dict,
        description: Optional[str] = None,
        is_default: bool = False,
        is_shared: bool = False,
        owner_id: Optional[str] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> PersonaView:
        """Create a new persona view."""
        view_id = str(uuid4())
        slug = slugify(name)
        
        # Ensure slug is unique within org
        counter = 1
        original_slug = slug
        while True:
            result = await db.execute(
                select(PersonaView).where(
                    PersonaView.org_id == org_id,
                    PersonaView.slug == slug
                )
            )
            if result.scalar_one_or_none() is None:
                break
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        view = PersonaView(
            id=view_id,
            org_id=org_id,
            name=name,
            slug=slug,
            description=description,
            persona=persona,
            config=config,
            is_default=is_default,
            is_shared=is_shared,
            owner_id=owner_id or user_id,
            is_active=True,
            created_by=user_id,
            updated_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(view)
        await db.flush()
        
        # Create audit log
        await create_audit_log(
            db=db,
            entity_type="persona_view",
            entity_id=view_id,
            action="create",
            org_id=org_id,
            user_id=user_id,
            changes={"new": {
                "name": name,
                "slug": slug,
                "persona": persona,
                "is_default": is_default,
            }},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )
        
        return view

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        view_id: str,
        org_id: str,
    ) -> Optional[PersonaView]:
        """Get persona view by ID with org_id enforcement."""
        result = await db.execute(
            select(PersonaView).where(
                PersonaView.id == view_id,
                PersonaView.org_id == org_id,
                PersonaView.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(
        db: AsyncSession,
        slug: str,
        org_id: str,
    ) -> Optional[PersonaView]:
        """Get persona view by slug with org_id enforcement."""
        result = await db.execute(
            select(PersonaView).where(
                PersonaView.slug == slug,
                PersonaView.org_id == org_id,
                PersonaView.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        org_id: str,
        persona: Optional[str] = None,
        owner_id: Optional[str] = None,
        is_default: Optional[bool] = None,
        is_shared: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[PersonaView]:
        """List persona views for an organization with pagination."""
        query = select(PersonaView).where(PersonaView.org_id == org_id)
        
        if persona is not None:
            query = query.where(PersonaView.persona == persona)
        
        if owner_id is not None:
            query = query.where(PersonaView.owner_id == owner_id)
        
        if is_default is not None:
            query = query.where(PersonaView.is_default == is_default)
        
        if is_shared is not None:
            query = query.where(PersonaView.is_shared == is_shared)
        
        if is_active is not None:
            query = query.where(PersonaView.is_active == is_active)
        
        query = query.order_by(PersonaView.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count(
        db: AsyncSession,
        org_id: str,
        persona: Optional[str] = None,
        owner_id: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count persona views for an organization."""
        query = select(func.count(PersonaView.id)).where(PersonaView.org_id == org_id)
        
        if persona is not None:
            query = query.where(PersonaView.persona == persona)
        
        if owner_id is not None:
            query = query.where(PersonaView.owner_id == owner_id)
        
        if is_active is not None:
            query = query.where(PersonaView.is_active == is_active)
        
        result = await db.execute(query)
        return result.scalar_one()

    @staticmethod
    async def update(
        db: AsyncSession,
        view_id: str,
        org_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[dict] = None,
        is_default: Optional[bool] = None,
        is_shared: Optional[bool] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[PersonaView]:
        """Update persona view with org_id enforcement."""
        result = await db.execute(
            select(PersonaView).where(
                PersonaView.id == view_id,
                PersonaView.org_id == org_id,
                PersonaView.is_active == True,
            )
        )
        view = result.scalar_one_or_none()
        
        if not view:
            return None
        
        changes = {"old": {}, "new": {}}
        
        if name is not None and name != view.name:
            changes["old"]["name"] = view.name
            changes["new"]["name"] = name
            view.name = name
            
            # Update slug if name changed
            new_slug = slugify(name)
            if new_slug != view.slug:
                changes["old"]["slug"] = view.slug
                changes["new"]["slug"] = new_slug
                view.slug = new_slug
        
        if description is not None and description != view.description:
            changes["old"]["description"] = view.description
            changes["new"]["description"] = description
            view.description = description
        
        if config is not None and config != view.config:
            changes["old"]["config"] = view.config
            changes["new"]["config"] = config
            view.config = config
        
        if is_default is not None and is_default != view.is_default:
            changes["old"]["is_default"] = view.is_default
            changes["new"]["is_default"] = is_default
            view.is_default = is_default
        
        if is_shared is not None and is_shared != view.is_shared:
            changes["old"]["is_shared"] = view.is_shared
            changes["new"]["is_shared"] = is_shared
            view.is_shared = is_shared
        
        view.updated_by = user_id
        view.updated_at = datetime.utcnow()
        
        await db.flush()
        
        # Create audit log if there were changes
        if changes["old"]:
            await create_audit_log(
                db=db,
                entity_type="persona_view",
                entity_id=view_id,
                action="update",
                org_id=org_id,
                user_id=user_id,
                changes=changes,
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
            )
        
        return view

    @staticmethod
    async def delete(
        db: AsyncSession,
        view_id: str,
        org_id: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Soft delete persona view with org_id enforcement."""
        result = await db.execute(
            select(PersonaView).where(
                PersonaView.id == view_id,
                PersonaView.org_id == org_id,
                PersonaView.is_active == True,
            )
        )
        view = result.scalar_one_or_none()
        
        if not view:
            return False
        
        view.is_active = False
        view.updated_by = user_id
        view.updated_at = datetime.utcnow()
        
        await db.flush()
        
        # Create audit log
        await create_audit_log(
            db=db,
            entity_type="persona_view",
            entity_id=view_id,
            action="delete",
            org_id=org_id,
            user_id=user_id,
            changes={"old": {"is_active": True}, "new": {"is_active": False}},
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )
        
        return True
