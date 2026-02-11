"""Workflow execution state machine."""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from finops_common import get_logger
from models import WorkflowExecution, WorkflowExecutionStatus, WorkflowStep, StepStatus

logger = get_logger(__name__)


class WorkflowStateMachine:
    """Manages workflow execution state transitions."""
    
    # Valid state transitions
    TRANSITIONS = {
        WorkflowExecutionStatus.RECEIVED: [WorkflowExecutionStatus.MATCHED, WorkflowExecutionStatus.DEDUPED, WorkflowExecutionStatus.FAILED],
        WorkflowExecutionStatus.MATCHED: [WorkflowExecutionStatus.RUNNING, WorkflowExecutionStatus.DEDUPED, WorkflowExecutionStatus.FAILED],
        WorkflowExecutionStatus.RUNNING: [WorkflowExecutionStatus.WAITING, WorkflowExecutionStatus.SUCCEEDED, WorkflowExecutionStatus.FAILED, WorkflowExecutionStatus.RETRYING],
        WorkflowExecutionStatus.WAITING: [WorkflowExecutionStatus.RUNNING, WorkflowExecutionStatus.FAILED, WorkflowExecutionStatus.RETRYING],
        WorkflowExecutionStatus.RETRYING: [WorkflowExecutionStatus.RUNNING, WorkflowExecutionStatus.FAILED],
        WorkflowExecutionStatus.SUCCEEDED: [],  # Terminal state
        WorkflowExecutionStatus.FAILED: [WorkflowExecutionStatus.RETRYING],  # Can retry from failed
        WorkflowExecutionStatus.DEDUPED: [],  # Terminal state
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def transition(
        self,
        execution_id: str,
        new_status: WorkflowExecutionStatus,
        error_message: Optional[str] = None,
        result: Optional[Dict] = None,
    ) -> bool:
        """Transition execution to new status."""
        # Get current execution
        result_obj = await self.db.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        )
        execution = result_obj.scalar_one_or_none()
        
        if not execution:
            logger.error(f"Execution {execution_id} not found")
            return False
        
        # Check if transition is valid
        if new_status not in self.TRANSITIONS.get(execution.status, []):
            logger.warning(
                f"Invalid transition from {execution.status} to {new_status} "
                f"for execution {execution_id}"
            )
            return False
        
        # Update execution
        update_data = {"status": new_status, "updated_at": datetime.utcnow()}
        
        if new_status == WorkflowExecutionStatus.RUNNING and not execution.started_at:
            update_data["started_at"] = datetime.utcnow()
        
        if new_status in [WorkflowExecutionStatus.SUCCEEDED, WorkflowExecutionStatus.FAILED]:
            update_data["completed_at"] = datetime.utcnow()
            if execution.started_at:
                duration = (datetime.utcnow() - execution.started_at).total_seconds() * 1000
                update_data["duration_ms"] = int(duration)
        
        if error_message:
            update_data["error_message"] = error_message
        
        if result:
            update_data["result"] = result
        
        await self.db.execute(
            update(WorkflowExecution)
            .where(WorkflowExecution.id == execution_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        logger.info(f"Transitioned execution {execution_id} from {execution.status} to {new_status}")
        return True
    
    def can_transition(self, current: WorkflowExecutionStatus, target: WorkflowExecutionStatus) -> bool:
        """Check if transition is valid."""
        return target in self.TRANSITIONS.get(current, [])
