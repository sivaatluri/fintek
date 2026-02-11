"""
Job runner for ingestion jobs.
"""

from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from finops_common import get_logger

from ..models.models import JobStatus
from ..crud.ingestion_jobs import IngestionJobCRUD
from ..connectors.registry import connector_registry
from ..storage.data_lake_writer import DataLakeWriter

logger = get_logger(__name__)


class JobRunner:
    """Runs ingestion jobs"""
    
    def __init__(self):
        self.data_lake_writer = DataLakeWriter()
    
    async def run_job(
        self,
        db: AsyncSession,
        job_id: str,
        org_id: str
    ) -> bool:
        """
        Run an ingestion job.
        
        Args:
            db: Database session
            job_id: Job ID
            org_id: Organization ID
            
        Returns:
            True if successful
        """
        # Get job
        job = await IngestionJobCRUD.get_by_id(db, job_id, org_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return False
        
        # Update status to running
        await IngestionJobCRUD.update_status(
            db, job_id, org_id, JobStatus.RUNNING.value
        )
        
        try:
            # Create connector
            connector = connector_registry.create_connector(
                connector_type=job.connector_type,
                org_id=org_id,
                config=job.config
            )
            
            # Get date range from config
            start_date = date.fromisoformat(job.config.get("start_date", date.today().isoformat()))
            end_date = date.fromisoformat(job.config.get("end_date", date.today().isoformat()))
            
            # Fetch data
            logger.info(f"Fetching data for job {job_id} from {start_date} to {end_date}")
            records = await connector.fetch_data(start_date, end_date)
            
            # Write to MinIO
            logger.info(f"Writing {len(records)} records to MinIO")
            data_lake_path = await self.data_lake_writer.write_records(
                org_id=org_id,
                cloud_provider=job.cloud_provider,
                records=records
            )
            
            # Update statistics
            await IngestionJobCRUD.update_statistics(
                db, job_id, org_id,
                records_ingested=len(records),
                data_lake_path=data_lake_path
            )
            
            # Update status to completed
            await IngestionJobCRUD.update_status(
                db, job_id, org_id, JobStatus.COMPLETED.value
            )
            
            # Emit Kafka event
            await self._emit_completion_event(job, len(records), data_lake_path)
            
            logger.info(f"Job {job_id} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {str(e)}")
            await IngestionJobCRUD.update_status(
                db, job_id, org_id,
                JobStatus.FAILED.value,
                error_message=str(e)
            )
            return False
    
    async def _emit_completion_event(
        self,
        job,
        records_count: int,
        data_lake_path: str
    ):
        """Emit ingestion completed event to Kafka"""
        # TODO: Implement with event-bus wrapper
        event = {
            "event_type": "cost.ingestion_completed",
            "event_id": f"evt-{job.id}",
            "timestamp": datetime.utcnow().isoformat(),
            "source": "cost-ingestion-service",
            "org_id": job.org_id,
            "payload": {
                "job_id": job.id,
                "org_id": job.org_id,
                "cloud_provider": job.cloud_provider,
                "start_date": job.config.get("start_date"),
                "end_date": job.config.get("end_date"),
                "records_ingested": records_count,
                "status": "completed",
                "duration_seconds": (
                    (job.completed_at - job.started_at).total_seconds()
                    if job.completed_at and job.started_at else 0
                ),
                "data_lake_path": data_lake_path
            },
            "routing": {
                "priority": "normal",
                "channels": ["workflow", "notification"]
            }
        }
        
        logger.info(f"Event emitted: {event['event_type']} for job {job.id}")
        # In production, this would use the event-bus wrapper to publish to Kafka
