"""Audit logging helper."""
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models import AuditLog


async def create_audit_log(
    db: AsyncSession,
    entity_type: str,
    entity_id: str,
    action: str,
    org_id: str,
    user_id: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
) -> AuditLog:
    """Create an audit log entry.
    
    Args:
        db: Database session
        entity_type: Type of entity (e.g., 'organization', 'tenant')
        entity_id: ID of the entity
        action: Action performed ('create', 'update', 'delete')
        org_id: Organization ID
        user_id: User who performed the action
        changes: Dictionary of changes (old/new values)
        ip_address: IP address of the request
        user_agent: User agent string
        request_id: Request ID for tracking
    
    Returns:
        Created audit log entry
    """
    audit_log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        org_id=org_id,
        user_id=user_id,
        changes=changes or {},
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        created_at=datetime.utcnow(),
    )
    
    db.add(audit_log)
    await db.flush()
    
    return audit_log


def get_changes_dict(old_obj: Any, new_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get dictionary of changes between old object and new data.
    
    Args:
        old_obj: SQLAlchemy model instance
        new_data: Dictionary of new values
    
    Returns:
        Dictionary with 'old' and 'new' keys containing changed fields
    """
    changes = {"old": {}, "new": {}}
    
    for key, new_value in new_data.items():
        if hasattr(old_obj, key):
            old_value = getattr(old_obj, key)
            if old_value != new_value:
                changes["old"][key] = old_value
                changes["new"][key] = new_value
    
    return changes if changes["old"] else {}
