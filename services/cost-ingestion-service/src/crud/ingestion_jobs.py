"""
CRUD operations for ingestion jobs.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from ..models.models import IngestionJob, JobStatus


class IngestionJobCRUD:
    """CRUD operations for ingestion jobs"""
    
    @staticmethod
    async def create(
        db: AsyncSession,
        org_id: str,
        connector_type: str,
        cloud_provider: str,
        config: dict,
        created_by: Optional[str] = None
    ) -> IngestionJob:
        """Create a new ingestion job"""
        job = IngestionJob(
            id=f"job-{uuid.uuid4().hex[:12]}",
            org_id=org_id,
            connector_type=connector_type,
            cloud_provider=cloud_provider,
            config=config,
            status=JobStatus.PENDING.value,
            created_by=created_by
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        job_id: str,
        org_id: str
    ) -> Optional[IngestionJob]:
        """Get job by ID with org enforcement"""
        result = await db.execute(
            select(IngestionJob)
            .where(IngestionJob.id == job_id)
            .where(IngestionJob.org_id == org_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_jobs(
        db: AsyncSession,
        org_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[IngestionJob]:
        """List ingestion jobs with filtering"""
        query = select(IngestionJob).where(IngestionJob.org_id == org_id)
        
        if status:
            query = query.where(IngestionJob.status == status)
        
        query = query.order_by(IngestionJob.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_status(
        db: AsyncSession,
        job_id: str,
        org_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[IngestionJob]:
        """Update job status"""
        job = await IngestionJobCRUD.get_by_id(db, job_id, org_id)
        if not job:
            return None
        
        job.status = status
        if error_message:
            job.error_message = error_message
        
        if status == JobStatus.RUNNING.value:
            job.started_at = datetime.utcnow()
        elif status in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]:
            job.completed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(job)
        return job
    
    @staticmethod
    async def update_statistics(
        db: AsyncSession,
        job_id: str,
        org_id: str,
        records_ingested: int,
        data_lake_path: str
    ) -> Optional[IngestionJob]:
        """Update job statistics"""
        job = await IngestionJobCRUD.get_by_id(db, job_id, org_id)
        if not job:
            return None
        
        job.records_ingested = records_ingested
        job.data_lake_path = data_lake_path
        
        await db.commit()
        await db.refresh(job)
        return job
