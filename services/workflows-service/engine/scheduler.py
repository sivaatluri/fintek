"""Delayed action scheduler."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from finops_common import get_logger
from models import WorkflowStep, StepStatus

logger = get_logger(__name__)


class ActionScheduler:
    """Schedules delayed workflow actions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def schedule_action(
        self,
        execution_id: str,
        action_config: Dict,
        delay_minutes: int = 0,
        step_order: int = 0,
    ) -> WorkflowStep:
        """Schedule an action for future execution."""
        step_id = str(uuid4())
        delay_until = datetime.utcnow() + timedelta(minutes=delay_minutes) if delay_minutes > 0 else None
        
        step = WorkflowStep(
            id=step_id,
            workflow_execution_id=execution_id,
            step_name=action_config.get("name", "Action"),
            step_type=action_config.get("type", "action"),
            step_order=step_order,
            status=StepStatus.WAITING if delay_until else StepStatus.PENDING,
            input_data=action_config,
            delay_until=delay_until,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        self.db.add(step)
        await self.db.commit()
        await self.db.refresh(step)
        
        logger.info(
            f"Scheduled step {step_id} for execution {execution_id} "
            f"(delay: {delay_minutes}m, delay_until: {delay_until})"
        )
        
        return step
    
    async def get_due_actions(self) -> List[WorkflowStep]:
        """Get actions that are due for execution."""
        now = datetime.utcnow()
        
        result = await self.db.execute(
            select(WorkflowStep)
            .where(
                WorkflowStep.status == StepStatus.WAITING,
                WorkflowStep.delay_until != None,
                WorkflowStep.delay_until <= now,
            )
            .order_by(WorkflowStep.delay_until)
        )
        
        steps = result.scalars().all()
        
        if steps:
            logger.info(f"Found {len(steps)} actions due for execution")
        
        return steps
    
    async def mark_step_ready(self, step_id: str):
        """Mark a step as ready for execution."""
        await self.db.execute(
            update(WorkflowStep)
            .where(WorkflowStep.id == step_id)
            .values(status=StepStatus.PENDING, updated_at=datetime.utcnow())
        )
        await self.db.commit()
        
        logger.info(f"Marked step {step_id} as ready for execution")
