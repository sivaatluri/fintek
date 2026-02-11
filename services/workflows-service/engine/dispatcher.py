"""Event dispatcher and workflow matcher."""
import json
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from finops_common import get_logger
from models import (
    TriggerType,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionStatus,
)
from .evaluator import ConditionEvaluator
from .idempotency import IdempotencyChecker
from .state_machine import WorkflowStateMachine

logger = get_logger(__name__)


class WorkflowDispatcher:
    """Dispatches events to matching workflows."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.evaluator = ConditionEvaluator()
        self.idempotency = IdempotencyChecker(db)
        self.state_machine = WorkflowStateMachine(db)
    
    async def find_matching_workflows(
        self,
        org_id: str,
        event: Dict,
    ) -> List[WorkflowDefinition]:
        """Find workflow definitions matching this event."""
        event_type = event.get("event_type")
        
        # Query active event-triggered workflows for this org
        result = await self.db.execute(
            select(WorkflowDefinition)
            .where(
                WorkflowDefinition.org_id == org_id,
                WorkflowDefinition.is_active == True,
                WorkflowDefinition.trigger_type == TriggerType.EVENT,
            )
        )
        definitions = result.scalars().all()
        
        # Filter by event type and conditions
        matching = []
        for definition in definitions:
            trigger_config = definition.trigger_config or {}
            event_types = trigger_config.get("event_types", [])
            
            # Check if event type matches
            if event_type not in event_types:
                continue
            
            # Check if conditions match
            if definition.conditions:
                if not self.evaluator.evaluate(definition.conditions, event):
                    continue
            
            matching.append(definition)
        
        logger.info(f"Found {len(matching)} matching workflows for event {event_type}")
        return matching
    
    async def dispatch_event(
        self,
        org_id: str,
        event: Dict,
        dry_run: bool = False,
    ) -> List[WorkflowExecution]:
        """Dispatch event to matching workflows."""
        executions = []
        
        # Find matching workflows
        workflows = await self.find_matching_workflows(org_id, event)
        
        for workflow in workflows:
            # Check deduplication
            should_run, dedupe_key = await self.idempotency.should_execute(
                org_id, event, workflow
            )
            
            # Create execution record
            execution_id = str(uuid4())
            execution = WorkflowExecution(
                id=execution_id,
                workflow_definition_id=workflow.id,
                org_id=org_id,
                status=WorkflowExecutionStatus.MATCHED if should_run else WorkflowExecutionStatus.DEDUPED,
                trigger_event=event,
                dedupe_key=dedupe_key,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            
            if not dry_run:
                self.db.add(execution)
                await self.db.commit()
                await self.db.refresh(execution)
            
            executions.append(execution)
            
            logger.info(
                f"Created execution {execution_id} for workflow {workflow.id} "
                f"(status: {execution.status})"
            )
        
        return executions
