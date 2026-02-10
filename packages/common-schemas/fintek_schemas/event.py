"""Canonical event schemas for fintek platform."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event types in the fintek platform."""
    
    # Cost events
    COST_INGESTED = "cost.ingested"
    COST_UPDATED = "cost.updated"
    COST_ANOMALY_DETECTED = "cost.anomaly_detected"
    
    # Budget events
    BUDGET_CREATED = "budget.created"
    BUDGET_UPDATED = "budget.updated"
    BUDGET_THRESHOLD_EXCEEDED = "budget.threshold_exceeded"
    BUDGET_ALERT = "budget.alert"
    
    # Tenant events
    TENANT_CREATED = "tenant.created"
    TENANT_UPDATED = "tenant.updated"
    TENANT_DELETED = "tenant.deleted"
    
    # Integration events
    INTEGRATION_CONNECTED = "integration.connected"
    INTEGRATION_DISCONNECTED = "integration.disconnected"
    INTEGRATION_SYNC_STARTED = "integration.sync_started"
    INTEGRATION_SYNC_COMPLETED = "integration.sync_completed"
    INTEGRATION_SYNC_FAILED = "integration.sync_failed"
    
    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"


class Event(BaseModel):
    """Canonical event schema for the fintek platform."""
    
    id: Optional[str] = None
    event_type: EventType = Field(..., description="Type of event")
    tenant_id: str = Field(..., description="Tenant identifier")
    
    # Event source
    source_service: str = Field(..., description="Service that generated the event")
    source_id: Optional[str] = Field(None, description="Source entity ID")
    
    # Event payload
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    
    # Metadata
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    user_id: Optional[str] = Field(None, description="User who triggered the event")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "cost.ingested",
                "tenant_id": "tenant-123",
                "source_service": "ingestion",
                "source_id": "ingest-job-456",
                "payload": {
                    "records_count": 1000,
                    "total_cost": "1500.00",
                    "provider": "aws",
                },
                "correlation_id": "corr-789",
            }
        }
