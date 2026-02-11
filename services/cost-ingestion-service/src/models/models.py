"""
Database models for cost ingestion service.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Integer, JSON, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JobStatus(str, Enum):
    """Ingestion job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ORACLE = "oracle"
    AKAMAI = "akamai"
    DATACENTER = "datacenter"


class IngestionJob(Base):
    """Ingestion job model"""
    __tablename__ = "ingestion_jobs"

    id = Column(String, primary_key=True)
    org_id = Column(String, nullable=False, index=True)
    connector_type = Column(String, nullable=False)
    cloud_provider = Column(String, nullable=False)
    status = Column(String, nullable=False, default=JobStatus.PENDING.value)
    
    # Configuration
    config = Column(JSON, nullable=False, default=dict)
    
    # Execution details
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Statistics
    records_ingested = Column(Integer, default=0)
    data_lake_path = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=True)
