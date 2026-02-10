"""Tenant schemas for fintek platform."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class TenantStatus(str, Enum):
    """Tenant status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"


class TenantSettings(BaseModel):
    """Tenant-specific settings."""
    
    currency: str = Field(default="USD", description="Default currency")
    timezone: str = Field(default="UTC", description="Default timezone")
    
    # Feature flags
    enable_anomaly_detection: bool = Field(default=True)
    enable_budget_alerts: bool = Field(default=True)
    enable_custom_dashboards: bool = Field(default=False)
    
    # Limits
    max_users: int = Field(default=10, description="Maximum number of users")
    max_integrations: int = Field(default=5, description="Maximum number of cloud integrations")
    data_retention_days: int = Field(default=90, description="Data retention period in days")
    
    # Custom settings
    custom: Dict[str, Any] = Field(default_factory=dict)


class Tenant(BaseModel):
    """Tenant schema."""
    
    id: Optional[str] = None
    name: str = Field(..., description="Tenant name")
    slug: str = Field(..., description="URL-friendly tenant identifier")
    
    status: TenantStatus = Field(default=TenantStatus.TRIAL)
    
    # Contact info
    primary_contact_email: EmailStr
    primary_contact_name: str
    
    # Settings
    settings: TenantSettings = Field(default_factory=TenantSettings)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    trial_ends_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Acme Corporation",
                "slug": "acme-corp",
                "status": "active",
                "primary_contact_email": "admin@acme.com",
                "primary_contact_name": "John Doe",
            }
        }
