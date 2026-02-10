"""Cost data ingestion service for fintek platform."""

from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel
from decimal import Decimal

from .health import router as health_router

app = FastAPI(
    title="Fintek Ingestion Service",
    description="Cost data ingestion and processing service",
    version="0.1.0",
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])


class CostRecordInput(BaseModel):
    """Cost record input."""
    tenant_id: str
    resource_id: str
    resource_type: str
    cloud_provider: str
    region: str
    service_name: str
    cost: Decimal
    currency: str = "USD"
    billing_period_start: datetime
    billing_period_end: datetime
    tags: Dict[str, str] = {}
    metadata: Dict[str, Any] = {}


class IngestJobResponse(BaseModel):
    """Ingest job response."""
    job_id: str
    status: str
    records_count: int
    created_at: datetime


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "fintek-ingestion",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/ingest/costs", response_model=IngestJobResponse, status_code=202)
async def ingest_costs(records: List[CostRecordInput]):
    """Ingest cost records (placeholder).
    
    In production, this would:
    - Validate records
    - Publish to Kafka
    - Store in database
    - Return job ID for tracking
    """
    return {
        "job_id": "job-123",
        "status": "queued",
        "records_count": len(records),
        "created_at": datetime.utcnow(),
    }


@app.get("/ingest/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get ingestion job status (placeholder)."""
    return {
        "job_id": job_id,
        "status": "completed",
        "records_processed": 1000,
        "records_failed": 0,
        "created_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
    }


@app.post("/ingest/sync/{provider}")
async def sync_provider(provider: str, tenant_id: str):
    """Trigger sync from cloud provider (placeholder).
    
    Supported providers: aws, azure, gcp
    """
    if provider not in ["aws", "azure", "gcp"]:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
    
    return {
        "sync_id": "sync-123",
        "provider": provider,
        "tenant_id": tenant_id,
        "status": "started",
        "timestamp": datetime.utcnow(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
