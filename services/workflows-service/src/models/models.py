"""SQLAlchemy models for workflows service."""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TriggerType(str, enum.Enum):
    """Workflow trigger types."""
    EVENT = "event"
    SCHEDULE = "schedule"
    MANUAL = "manual"


class WorkflowExecutionStatus(str, enum.Enum):
    """Workflow execution status."""
    RECEIVED = "received"  # Event received, not yet matched
    MATCHED = "matched"  # Matched to workflow definition
    DEDUPED = "deduped"  # Deduplicated (skipped)
    RUNNING = "running"  # Currently executing
    WAITING = "waiting"  # Waiting for external response or delay
    RETRYING = "retrying"  # Retrying after failure
    SUCCEEDED = "succeeded"  # Completed successfully
    FAILED = "failed"  # Failed permanently


class StepStatus(str, enum.Enum):
    """Workflow step status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING = "waiting"
    RETRYING = "retrying"


class WorkflowDefinition(Base):
    """Workflow definition model."""
    __tablename__ = "workflow_definitions"

    id = Column(String(36), primary_key=True)
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    trigger_type = Column(Enum(TriggerType), nullable=False)
    trigger_config = Column(JSON, nullable=False)  # event_types, schedule, conditions
    conditions = Column(JSON, nullable=True)  # Matching conditions
    actions = Column(JSON, nullable=False)  # Actions to execute
    escalation_rules = Column(JSON, nullable=True)  # Escalation configuration
    dedupe_config = Column(JSON, nullable=True)  # Deduplication configuration
    cooldown_minutes = Column(Integer, nullable=True)  # Cooldown period
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)
    is_template = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)

    # Relationships
    executions = relationship("WorkflowExecution", back_populates="definition", cascade="all, delete-orphan")


class WorkflowExecution(Base):
    """Workflow execution model."""
    __tablename__ = "workflow_executions"

    id = Column(String(36), primary_key=True)
    workflow_definition_id = Column(String(36), ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(WorkflowExecutionStatus), nullable=False, default=WorkflowExecutionStatus.RECEIVED)
    trigger_event = Column(JSON, nullable=True)  # The event that triggered this
    trigger_data = Column(JSON, nullable=True)  # Additional trigger data
    context = Column(JSON, nullable=True)  # Execution context
    result = Column(JSON, nullable=True)  # Final result
    error_message = Column(Text, nullable=True)
    dedupe_key = Column(String(64), nullable=True)  # SHA256 hash for deduplication
    cooldown_until = Column(DateTime, nullable=True)  # Cooldown period end
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    triggered_by = Column(String(36), nullable=True)

    # Relationships
    definition = relationship("WorkflowDefinition", back_populates="executions")
    steps = relationship("WorkflowStep", back_populates="execution", cascade="all, delete-orphan")
    external_refs = relationship("WorkflowExternalRef", back_populates="execution", cascade="all, delete-orphan")


class WorkflowStep(Base):
    """Workflow step execution model."""
    __tablename__ = "workflow_steps"

    id = Column(String(36), primary_key=True)
    workflow_execution_id = Column(String(36), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False)
    step_name = Column(String(255), nullable=False)
    step_type = Column(String(50), nullable=False)  # action, condition, delay, escalation
    step_order = Column(Integer, nullable=False)
    status = Column(Enum(StepStatus), nullable=False, default=StepStatus.PENDING)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    delay_until = Column(DateTime, nullable=True)  # For delayed actions
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    execution = relationship("WorkflowExecution", back_populates="steps")
    external_refs = relationship("WorkflowExternalRef", back_populates="step", cascade="all, delete-orphan")


class WorkflowExternalRef(Base):
    """External system references (Jira, ServiceNow, etc.)."""
    __tablename__ = "workflow_external_refs"

    id = Column(String(36), primary_key=True)
    workflow_execution_id = Column(String(36), ForeignKey("workflow_executions.id", ondelete="CASCADE"), nullable=False)
    workflow_step_id = Column(String(36), ForeignKey("workflow_steps.id", ondelete="CASCADE"), nullable=True)
    external_system = Column(String(50), nullable=False)  # jira, servicenow, slack, etc.
    external_id = Column(String(255), nullable=False)  # Issue key, ticket number, etc.
    external_url = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    execution = relationship("WorkflowExecution", back_populates="external_refs")
    step = relationship("WorkflowStep", back_populates="external_refs")
