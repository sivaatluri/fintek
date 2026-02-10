"""Database models for integrations service."""
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


class IntegrationType(str, enum.Enum):
    """Integration types."""
    JIRA = "jira"
    SERVICENOW = "servicenow"
    ZENDESK = "zendesk"
    SLACK = "slack"
    TEAMS = "teams"
    PAGERDUTY = "pagerduty"
    EMAIL = "email"
    WEBHOOK = "webhook"
    CUSTOM = "custom"


class DeliveryStatus(str, enum.Enum):
    """Delivery status values."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class Integration(Base):
    """Integration configuration."""
    __tablename__ = "integrations"

    id = Column(String(36), primary_key=True)
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    integration_type = Column(Enum(IntegrationType), nullable=False, index=True)
    config = Column(JSON, nullable=False)
    credentials = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    last_verified_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    failure_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(String(36), nullable=True)

    # Relationships
    deliveries = relationship("IntegrationDelivery", back_populates="integration", cascade="all, delete-orphan")


class IntegrationDelivery(Base):
    """Integration delivery attempt."""
    __tablename__ = "integration_deliveries"

    id = Column(String(36), primary_key=True)
    integration_id = Column(String(36), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_execution_id = Column(String(36), ForeignKey("workflow_executions.id", ondelete="SET NULL"), nullable=True, index=True)
    workflow_step_id = Column(String(36), ForeignKey("workflow_steps.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(Enum(DeliveryStatus), nullable=False, default=DeliveryStatus.PENDING, index=True)
    payload = Column(JSON, nullable=False)
    response = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    http_status = Column(Integer, nullable=True)
    external_id = Column(String(255), nullable=True, index=True)
    external_url = Column(String(1000), nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    next_retry_at = Column(DateTime, nullable=True, index=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    integration = relationship("Integration", back_populates="deliveries")
