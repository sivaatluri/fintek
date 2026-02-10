"""Canonical cost schemas for fintek platform."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CostGranularity(str, Enum):
    """Time granularity for cost aggregation."""
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"


class CostRecord(BaseModel):
    """Canonical cost record schema."""
    
    id: Optional[str] = None
    tenant_id: str = Field(..., description="Tenant identifier")
    resource_id: str = Field(..., description="Unique resource identifier")
    resource_type: str = Field(..., description="Type of resource (e.g., vm, storage, network)")
    cloud_provider: str = Field(..., description="Cloud provider (aws, azure, gcp, etc.)")
    region: str = Field(..., description="Cloud region")
    service_name: str = Field(..., description="Cloud service name")
    
    # Cost details
    cost: Decimal = Field(..., description="Cost amount")
    currency: str = Field(default="USD", description="Currency code")
    billing_period_start: datetime = Field(..., description="Start of billing period")
    billing_period_end: datetime = Field(..., description="End of billing period")
    
    # Metadata
    tags: Dict[str, str] = Field(default_factory=dict, description="Resource tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant-123",
                "resource_id": "i-1234567890abcdef0",
                "resource_type": "vm",
                "cloud_provider": "aws",
                "region": "us-east-1",
                "service_name": "EC2",
                "cost": "15.50",
                "currency": "USD",
                "billing_period_start": "2024-01-01T00:00:00Z",
                "billing_period_end": "2024-01-01T23:59:59Z",
                "tags": {"environment": "production", "team": "platform"},
            }
        }


class CostAggregation(BaseModel):
    """Aggregated cost metrics."""
    
    tenant_id: str
    total_cost: Decimal
    currency: str = "USD"
    period_start: datetime
    period_end: datetime
    granularity: CostGranularity
    
    # Breakdown dimensions
    by_service: Dict[str, Decimal] = Field(default_factory=dict)
    by_region: Dict[str, Decimal] = Field(default_factory=dict)
    by_resource_type: Dict[str, Decimal] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
