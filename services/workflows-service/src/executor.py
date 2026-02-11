"""Workflow executor - executes workflow actions."""
import httpx
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from finops_common import get_logger
from models import WorkflowStep, StepStatus, WorkflowExternalRef, WorkflowExecutionStatus
from engine import WorkflowStateMachine

logger = get_logger(__name__)


class WorkflowExecutor:
    """Executes workflow actions."""
    
    def __init__(self, db: AsyncSession, integrations_base_url: str = "http://integrations-service:8011"):
        self.db = db
        self.integrations_base_url = integrations_base_url
        self.state_machine = WorkflowStateMachine(db)
        
        # Set up Jinja2 for templates
        self.jinja_env = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=select_autoescape(["html", "xml", "j2"]),
        )
    
    async def execute_actions(
        self,
        execution_id: str,
        actions: List[Dict],
        context: Dict,
    ) -> bool:
        """Execute all actions for a workflow."""
        success = True
        
        for i, action in enumerate(actions):
            step_id = str(uuid4())
            
            # Create step record
            step = WorkflowStep(
                id=step_id,
                workflow_execution_id=execution_id,
                step_name=action.get("name", f"Action {i+1}"),
                step_type=action.get("type", "action"),
                step_order=i,
                status=StepStatus.PENDING,
                input_data=action,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            
            self.db.add(step)
            await self.db.commit()
            await self.db.refresh(step)
            
            # Execute the action
            step_success = await self._execute_action(step, action, context)
            
            if not step_success:
                success = False
                if action.get("required", False):
                    logger.error(f"Required action failed: {action.get('name')}")
                    break
        
        return success
    
    async def _execute_action(
        self,
        step: WorkflowStep,
        action: Dict,
        context: Dict,
    ) -> bool:
        """Execute a single action."""
        # Update step to running
        await self.db.execute(
            update(WorkflowStep)
            .where(WorkflowStep.id == step.id)
            .values(
                status=StepStatus.RUNNING,
                started_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        await self.db.commit()
        
        action_type = action.get("type")
        
        try:
            if action_type in ["jira", "servicenow", "slack", "email", "webhook"]:
                result = await self._execute_integration_action(step, action, context)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                result = {"status": "skipped", "reason": f"Unknown action type: {action_type}"}
            
            # Update step as completed
            await self.db.execute(
                update(WorkflowStep)
                .where(WorkflowStep.id == step.id)
                .values(
                    status=StepStatus.COMPLETED,
                    output_data=result,
                    completed_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )
            await self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing action {action.get('name')}: {e}")
            
            # Update step as failed
            await self.db.execute(
                update(WorkflowStep)
                .where(WorkflowStep.id == step.id)
                .values(
                    status=StepStatus.FAILED,
                    error_message=str(e),
                    completed_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            )
            await self.db.commit()
            
            return False
    
    async def _execute_integration_action(
        self,
        step: WorkflowStep,
        action: Dict,
        context: Dict,
    ) -> Dict:
        """Execute action via integrations service."""
        action_type = action.get("type")
        template_name = action.get("template")
        integration_name = action.get("integration")
        
        # Render template if provided
        payload = {}
        if template_name:
            template_path = f"{action_type}/{template_name}.j2"
            try:
                template = self.jinja_env.get_template(template_path)
                rendered = template.render(**context)
                payload["body"] = rendered
            except Exception as e:
                logger.error(f"Error rendering template {template_path}: {e}")
                payload["body"] = str(context.get("event", {}))
        else:
            payload = action.get("payload", context.get("event", {}))
        
        # Add metadata
        payload.update({
            "subject": action.get("subject", f"FinOps Alert: {context.get('event_type')}"),
            "priority": context.get("routing", {}).get("priority", "P3"),
            "labels": context.get("routing", {}).get("labels", []),
        })
        
        # Call integrations service
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Create delivery via integrations service
                response = await client.post(
                    f"{self.integrations_base_url}/api/v1/deliveries",
                    json={
                        "integration_id": integration_name,  # In real world, would lookup integration ID
                        "payload": payload,
                        "workflow_execution_id": step.workflow_execution_id,
                        "workflow_step_id": step.id,
                    },
                    headers={
                        "X-Org-ID": context.get("event", {}).get("tenant_id"),
                        "X-Request-ID": context.get("event", {}).get("event_id"),
                    },
                )
                
                if response.status_code in [200, 201]:
                    delivery_data = response.json()
                    
                    # Create external reference
                    if delivery_data.get("external_id"):
                        ext_ref = WorkflowExternalRef(
                            id=str(uuid4()),
                            workflow_execution_id=step.workflow_execution_id,
                            workflow_step_id=step.id,
                            external_system=action_type,
                            external_id=delivery_data.get("external_id"),
                            external_url=delivery_data.get("external_url"),
                            metadata=delivery_data,
                            created_at=datetime.utcnow(),
                        )
                        self.db.add(ext_ref)
                        await self.db.commit()
                    
                    return {
                        "status": "success",
                        "delivery_id": delivery_data.get("id"),
                        "external_id": delivery_data.get("external_id"),
                        "external_url": delivery_data.get("external_url"),
                    }
                else:
                    return {
                        "status": "failed",
                        "error": f"HTTP {response.status_code}: {response.text}",
                    }
                    
            except Exception as e:
                logger.error(f"Error calling integrations service: {e}")
                return {
                    "status": "failed",
                    "error": str(e),
                }
