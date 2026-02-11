"""Deduplication and idempotency logic."""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from finops_common import get_logger
from models import WorkflowDefinition, WorkflowExecution, WorkflowExecutionStatus

logger = get_logger(__name__)


class IdempotencyChecker:
    """Handles workflow deduplication and cooldown."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def generate_dedupe_key(
        self,
        org_id: str,
        event_type: str,
        scope: Optional[Dict] = None,
        period: Optional[str] = None,
        threshold: Optional[float] = None,
        workflow_version: int = 1,
    ) -> str:
        """Generate SHA256 dedupe key."""
        # Build dedupe data
        dedupe_data = {
            "org_id": org_id,
            "event_type": event_type,
            "scope": scope or {},
            "period": period or "default",
            "threshold": threshold or 0,
            "workflow_version": workflow_version,
        }
        
        # Sort keys for consistency
        canonical = json.dumps(dedupe_data, sort_keys=True)
        
        # Generate SHA256 hash
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    async def check_duplicate(
        self,
        dedupe_key: str,
        cooldown_minutes: int = 60,
    ) -> Optional[WorkflowExecution]:
        """Check if workflow execution is duplicate within cooldown period."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=cooldown_minutes)
        
        result = await self.db.execute(
            select(WorkflowExecution)
            .where(
                WorkflowExecution.dedupe_key == dedupe_key,
                WorkflowExecution.created_at >= cutoff_time,
                WorkflowExecution.status != WorkflowExecutionStatus.FAILED,
            )
            .order_by(WorkflowExecution.created_at.desc())
            .limit(1)
        )
        
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info(
                f"Found duplicate execution {existing.id} with dedupe_key {dedupe_key}"
            )
        
        return existing
    
    async def should_execute(
        self,
        org_id: str,
        event: Dict,
        workflow_definition: WorkflowDefinition,
    ) -> tuple[bool, Optional[str]]:
        """Determine if workflow should execute based on deduplication."""
        if not workflow_definition.dedupe_config:
            return True, None
        
        # Extract dedupe parameters from config
        dedupe_config = workflow_definition.dedupe_config
        event_type = event.get("event_type")
        
        # Build scope from event payload
        scope = {}
        if "scope_fields" in dedupe_config:
            payload = event.get("payload", {})
            for field in dedupe_config["scope_fields"]:
                if field in payload:
                    scope[field] = payload[field]
        
        # Generate dedupe key
        dedupe_key = self.generate_dedupe_key(
            org_id=org_id,
            event_type=event_type,
            scope=scope,
            period=dedupe_config.get("period"),
            threshold=dedupe_config.get("threshold"),
            workflow_version=workflow_definition.version,
        )
        
        # Check for duplicates
        cooldown = dedupe_config.get("cooldown_minutes", workflow_definition.cooldown_minutes or 60)
        duplicate = await self.check_duplicate(dedupe_key, cooldown)
        
        if duplicate:
            logger.info(f"Deduplicating workflow execution for org {org_id}, event {event_type}")
            return False, dedupe_key
        
        return True, dedupe_key
