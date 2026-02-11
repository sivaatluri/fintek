"""Workflows Service - Main application."""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from finops_common import (
    Settings,
    create_app,
    get_logger,
    get_org_id,
    get_request_id,
)

from database import close_db, get_db, init_db
from models import (
    TriggerType,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionStatus,
)
from engine import WorkflowDispatcher, ContextBuilder, EscalationEngine
from executor import WorkflowExecutor

logger = get_logger(__name__)

settings = Settings(
    service_name="workflows-service",
    service_version="1.0.0",
    port=8010,
)

app = create_app(
    title="FinOps Workflows Service",
    version="1.0.0",
    description="Workflow Automation Service for FinOps Platform",
    settings=settings,
)

router = APIRouter(prefix="/api/v1", tags=["Workflows"])


# ============================================================================
# Pydantic Models
# ============================================================================

class WorkflowDefinitionCreate(BaseModel):
    """Workflow definition creation request."""
    name: str
    description: Optional[str] = None
    trigger_type: TriggerType
    trigger_config: dict
    conditions: Optional[dict] = None
    actions: list
    escalation_rules: Optional[dict] = None
    dedupe_config: Optional[dict] = None
    cooldown_minutes: Optional[int] = 60


class DryRunRequest(BaseModel):
    """Dry run request."""
    event: dict
    workflow_definition: Optional[dict] = None


class DryRunResponse(BaseModel):
    """Dry run response."""
    matched_workflows: int
    executions: List[dict]
    would_execute: bool
    deduplicated: bool
    dedup_reasons: List[str]


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/workflows/dry-run", response_model=DryRunResponse)
async def dry_run_workflow(
    request: DryRunRequest,
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    """Test workflow execution without actually executing."""
    logger.info(f"Dry run for org {org_id}, event type: {request.event.get('event_type')}")
    
    dispatcher = WorkflowDispatcher(db)
    
    # If workflow definition provided, test it specifically
    if request.workflow_definition:
        # Create temporary workflow definition
        temp_workflow = WorkflowDefinition(
            id=str(uuid4()),
            org_id=org_id,
            **request.workflow_definition,
        )
        
        # Check if it would match
        evaluator = dispatcher.evaluator
        trigger_config = temp_workflow.trigger_config or {}
        event_types = trigger_config.get("event_types", [])
        
        would_match = request.event.get("event_type") in event_types
        
        if temp_workflow.conditions:
            would_match = would_match and evaluator.evaluate(
                temp_workflow.conditions,
                request.event,
            )
        
        # Check deduplication
        should_run, dedupe_key = await dispatcher.idempotency.should_execute(
            org_id, request.event, temp_workflow
        )
        
        return DryRunResponse(
            matched_workflows=1 if would_match else 0,
            executions=[{
                "workflow_name": temp_workflow.name,
                "would_match": would_match,
                "would_execute": would_match and should_run,
                "dedupe_key": dedupe_key,
            }],
            would_execute=would_match and should_run,
            deduplicated=not should_run,
            dedup_reasons=["Duplicate found in cooldown period"] if not should_run else [],
        )
    
    # Otherwise, test against existing workflows
    executions = await dispatcher.dispatch_event(org_id, request.event, dry_run=True)
    
    deduped_count = sum(1 for e in executions if e.status == WorkflowExecutionStatus.DEDUPED)
    
    return DryRunResponse(
        matched_workflows=len(executions),
        executions=[{
            "id": e.id,
            "workflow_definition_id": e.workflow_definition_id,
            "status": e.status,
            "dedupe_key": e.dedupe_key,
        } for e in executions],
        would_execute=len(executions) > deduped_count,
        deduplicated=deduped_count > 0,
        dedup_reasons=[f"{deduped_count} workflows deduplicated"] if deduped_count > 0 else [],
    )


@router.post("/workflows/definitions")
async def create_workflow_definition(
    definition: WorkflowDefinitionCreate,
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    """Create workflow definition."""
    workflow_id = str(uuid4())
    
    workflow = WorkflowDefinition(
        id=workflow_id,
        org_id=org_id,
        **definition.dict(),
    )
    
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    
    logger.info(f"Created workflow definition {workflow_id} for org {org_id}")
    
    return {
        "id": workflow.id,
        "name": workflow.name,
        "trigger_type": workflow.trigger_type,
        "version": workflow.version,
        "is_active": workflow.is_active,
        "created_at": workflow.created_at,
    }


@router.get("/workflows/definitions")
async def list_workflow_definitions(
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    """List workflow definitions."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(WorkflowDefinition)
        .where(WorkflowDefinition.org_id == org_id)
        .order_by(WorkflowDefinition.created_at.desc())
    )
    
    workflows = result.scalars().all()
    
    return {
        "workflows": [{
            "id": w.id,
            "name": w.name,
            "trigger_type": w.trigger_type,
            "version": w.version,
            "is_active": w.is_active,
            "created_at": w.created_at,
        } for w in workflows]
    }


@router.get("/workflows/executions")
async def list_workflow_executions(
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    """List workflow executions."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(WorkflowExecution)
        .where(WorkflowExecution.org_id == org_id)
        .order_by(WorkflowExecution.created_at.desc())
        .limit(limit)
    )
    
    executions = result.scalars().all()
    
    return {
        "executions": [{
            "id": e.id,
            "workflow_definition_id": e.workflow_definition_id,
            "status": e.status,
            "started_at": e.started_at,
            "completed_at": e.completed_at,
            "duration_ms": e.duration_ms,
            "created_at": e.created_at,
        } for e in executions]
    }


@router.get("/workflows/executions/{execution_id}")
async def get_workflow_execution(
    execution_id: str,
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    """Get workflow execution details."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(WorkflowExecution)
        .where(
            WorkflowExecution.id == execution_id,
            WorkflowExecution.org_id == org_id,
        )
    )
    
    execution = result.scalar_one_or_none()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {
        "id": execution.id,
        "workflow_definition_id": execution.workflow_definition_id,
        "status": execution.status,
        "trigger_event": execution.trigger_event,
        "context": execution.context,
        "result": execution.result,
        "error_message": execution.error_message,
        "dedupe_key": execution.dedupe_key,
        "retry_count": execution.retry_count,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at,
        "duration_ms": execution.duration_ms,
        "created_at": execution.created_at,
    }


app.include_router(router)


# ============================================================================
# Background Tasks
# ============================================================================

async def process_kafka_events():
    """Background task to consume Kafka events."""
    logger.info("Kafka event consumer started")
    
    # In production, this would use aiokafka
    # For now, it's a placeholder that would be integrated with the Kafka infrastructure
    
    while True:
        try:
            # This is where you'd consume from Kafka
            # consumer = AIOKafkaConsumer('finops-events', ...)
            # async for message in consumer:
            #     event = json.loads(message.value)
            #     await handle_event(event)
            
            await asyncio.sleep(5)  # Poll interval
            
        except Exception as e:
            logger.error(f"Error in Kafka consumer: {e}")
            await asyncio.sleep(10)


async def handle_event(event: Dict):
    """Handle incoming event from Kafka."""
    logger.info(f"Handling event: {event.get('event_type')} ({event.get('event_id')})")
    
    org_id = event.get("tenant_id")  # In our schema, tenant_id maps to org
    
    async with get_db() as db:
        # Dispatch to matching workflows
        dispatcher = WorkflowDispatcher(db)
        executions = await dispatcher.dispatch_event(org_id, event)
        
        # Execute matched workflows
        executor = WorkflowExecutor(db)
        context_builder = ContextBuilder()
        
        for execution in executions:
            if execution.status == WorkflowExecutionStatus.MATCHED:
                # Build context
                context = context_builder.build_context(event, {})
                execution.context = context
                
                # Get workflow definition
                from sqlalchemy import select
                result = await db.execute(
                    select(WorkflowDefinition)
                    .where(WorkflowDefinition.id == execution.workflow_definition_id)
                )
                workflow = result.scalar_one()
                
                # Execute actions
                success = await executor.execute_actions(
                    execution.id,
                    workflow.actions,
                    context,
                )
                
                # Update execution status
                from engine import WorkflowStateMachine
                state_machine = WorkflowStateMachine(db)
                await state_machine.transition(
                    execution.id,
                    WorkflowExecutionStatus.SUCCEEDED if success else WorkflowExecutionStatus.FAILED,
                )


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Workflows Service starting up")
    
    # Initialize database
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/finops")
    init_db(database_url)
    
    # Start Kafka consumer in background
    # asyncio.create_task(process_kafka_events())
    
    logger.info("Workflows Service ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Workflows Service shutting down")
    await close_db()


if __name__ == "__main__":
    import os
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
