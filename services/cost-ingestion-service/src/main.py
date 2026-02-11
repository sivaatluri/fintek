"""
Cost Ingestion Service - Main API
"""

from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from finops_common import create_app, Settings, get_logger

from .database import get_db
from .models.models import IngestionJob, JobStatus
from .crud.ingestion_jobs import IngestionJobCRUD
from .orchestrator.job_runner import JobRunner
from .connectors.registry import connector_registry

# Import mock connector to register it
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../connectors/mock-connector/src'))
import mock_connector

logger = get_logger(__name__)

# Create FastAPI app
settings = Settings(service_name="cost-ingestion-service", port=8004)
app = create_app("Cost Ingestion Service", "1.0.0", settings=settings)

# Initialize job runner
job_runner = JobRunner()


# Pydantic models
class CreateJobRequest(BaseModel):
    connector_type: str
    cloud_provider: str
    config: dict


class TestConnectorRequest(BaseModel):
    connector_type: str
    cloud_provider: str
    config: dict


# API endpoints
@app.post("/api/v1/ingestion/jobs", response_model=dict)
async def create_job(
    request: CreateJobRequest,
    db: AsyncSession = Depends(get_db),
    x_org_id: str = Header(..., alias="X-Org-ID")
):
    """Create a new ingestion job"""
    try:
        job = await IngestionJobCRUD.create(
            db=db,
            org_id=x_org_id,
            connector_type=request.connector_type,
            cloud_provider=request.cloud_provider,
            config=request.config
        )
        
        # Run job asynchronously (in production, use background task or queue)
        import asyncio
        asyncio.create_task(job_runner.run_job(db, job.id, x_org_id))
        
        return {
            "id": job.id,
            "status": job.status,
            "connector_type": job.connector_type,
            "cloud_provider": job.cloud_provider,
            "created_at": job.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ingestion/jobs", response_model=List[dict])
async def list_jobs(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    x_org_id: str = Header(..., alias="X-Org-ID")
):
    """List ingestion jobs"""
    jobs = await IngestionJobCRUD.list_jobs(
        db=db,
        org_id=x_org_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return [
        {
            "id": job.id,
            "status": job.status,
            "connector_type": job.connector_type,
            "cloud_provider": job.cloud_provider,
            "records_ingested": job.records_ingested,
            "data_lake_path": job.data_lake_path,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message
        }
        for job in jobs
    ]


@app.get("/api/v1/ingestion/jobs/{job_id}", response_model=dict)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    x_org_id: str = Header(..., alias="X-Org-ID")
):
    """Get job details"""
    job = await IngestionJobCRUD.get_by_id(db, job_id, x_org_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job.id,
        "org_id": job.org_id,
        "status": job.status,
        "connector_type": job.connector_type,
        "cloud_provider": job.cloud_provider,
        "config": job.config,
        "records_ingested": job.records_ingested,
        "data_lake_path": job.data_lake_path,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message
    }


@app.post("/api/v1/ingestion/jobs/{job_id}/cancel", response_model=dict)
async def cancel_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    x_org_id: str = Header(..., alias="X-Org-ID")
):
    """Cancel a running job"""
    job = await IngestionJobCRUD.update_status(
        db, job_id, x_org_id, JobStatus.FAILED.value, "Cancelled by user"
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"id": job.id, "status": job.status}


@app.post("/api/v1/ingestion/jobs/{job_id}/retry", response_model=dict)
async def retry_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    x_org_id: str = Header(..., alias="X-Org-ID")
):
    """Retry a failed job"""
    job = await IngestionJobCRUD.get_by_id(db, job_id, x_org_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.FAILED.value:
        raise HTTPException(status_code=400, detail="Only failed jobs can be retried")
    
    # Reset status to pending
    job = await IngestionJobCRUD.update_status(
        db, job_id, x_org_id, JobStatus.PENDING.value
    )
    
    # Run job
    import asyncio
    asyncio.create_task(job_runner.run_job(db, job.id, x_org_id))
    
    return {"id": job.id, "status": job.status}


@app.get("/api/v1/connectors", response_model=dict)
async def list_connectors():
    """List available connectors"""
    connectors = connector_registry.list_connectors()
    return {"connectors": connectors}


@app.post("/api/v1/connectors/test", response_model=dict)
async def test_connector(
    request: TestConnectorRequest,
    x_org_id: str = Header(..., alias="X-Org-ID")
):
    """Test a connector configuration"""
    try:
        connector = connector_registry.create_connector(
            connector_type=request.connector_type,
            org_id=x_org_id,
            config=request.config
        )
        
        # Validate config
        is_valid = await connector.validate_config()
        
        # Fetch small sample
        start_date = date.fromisoformat(request.config.get("start_date", date.today().isoformat()))
        end_date = date.fromisoformat(request.config.get("end_date", date.today().isoformat()))
        
        # Limit to 10 records for testing
        test_config = {**request.config, "records_per_day": 10}
        test_connector = connector_registry.create_connector(
            connector_type=request.connector_type,
            org_id=x_org_id,
            config=test_config
        )
        records = await test_connector.fetch_data(start_date, end_date)
        
        return {
            "valid": is_valid,
            "connector_type": request.connector_type,
            "sample_records_count": len(records),
            "sample_record": records[0] if records else None
        }
    except Exception as e:
        logger.error(f"Error testing connector: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
