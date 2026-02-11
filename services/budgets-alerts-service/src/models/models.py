"""
SQLAlchemy models for budgets and alerts.
"""

import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, Enum as SQLEnum, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class BudgetPeriod(str, enum.Enum):
    """Budget period types."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class BudgetStatus(str, enum.Enum):
    """Budget status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Budget(Base):
    """Budget model."""
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True)
    org_id = Column(String(36), nullable=False, index=True)
    tenant_id = Column(String(36), nullable=True, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    amount = Column(Float, nullable=False)
    period = Column(SQLEnum(BudgetPeriod), nullable=False, default=BudgetPeriod.MONTHLY)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Filters for which costs apply to this budget
    filters = Column(JSON, nullable=True)  # e.g., {"cloud_provider": "aws", "tags": {"env": "prod"}}
    
    # Alert thresholds (percentage of budget)
    thresholds = Column(JSON, nullable=False, default=lambda: [50, 80, 90, 100])
    
    # Current spend tracking
    current_spend = Column(Float, nullable=False, default=0.0)
    last_checked_at = Column(DateTime, nullable=True)
    
    # Alert state (which thresholds have been triggered)
    alert_state = Column(JSON, nullable=False, default=lambda: {})
    
    status = Column(SQLEnum(BudgetStatus), nullable=False, default=BudgetStatus.ACTIVE)
    is_active = Column(Boolean, nullable=False, default=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    
    # Relationships
    alerts = relationship("BudgetAlert", back_populates="budget", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Budget(id={self.id}, name={self.name}, amount={self.amount}, period={self.period})>"


class BudgetAlert(Base):
    """Budget alert history model."""
    __tablename__ = "budget_alerts"

    id = Column(String(36), primary_key=True)
    budget_id = Column(String(36), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(String(36), nullable=False, index=True)
    
    alert_type = Column(String(50), nullable=False)  # threshold, forecast, anomaly
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    
    # Detection details
    threshold_percentage = Column(Float, nullable=True)  # For threshold alerts
    actual_spend = Column(Float, nullable=False)
    budget_amount = Column(Float, nullable=False)
    forecast_amount = Column(Float, nullable=True)  # For forecast alerts
    
    # Anomaly detection details
    baseline_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # Event tracking
    event_id = Column(String(36), nullable=True)  # Kafka event ID
    event_sent = Column(Boolean, nullable=False, default=False)
    event_sent_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    budget = relationship("Budget", back_populates="alerts")

    def __repr__(self):
        return f"<BudgetAlert(id={self.id}, budget_id={self.budget_id}, type={self.alert_type}, severity={self.severity})>"
