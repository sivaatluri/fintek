"""
Data Lake Writer for MinIO.
"""

import json
import os
from datetime import date
from typing import List, Dict, Any
from io import BytesIO
from minio import Minio
from minio.error import S3Error
from finops_common import get_logger

logger = get_logger(__name__)


class DataLakeWriter:
    """Writes cost data to MinIO data lake"""
    
    def __init__(self):
        """Initialize MinIO client"""
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        self.bucket_name = os.getenv("MINIO_BUCKET", "cost-data-lake")
        
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        # Ensure bucket exists
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def generate_path(
        self,
        org_id: str,
        cloud_provider: str,
        usage_date: date
    ) -> str:
        """
        Generate data lake path.
        
        Format: lake/{org_id}/{cloud}/{yyyy}/{mm}/{dd}/raw.jsonl
        
        Args:
            org_id: Organization ID
            cloud_provider: Cloud provider name
            usage_date: Date of usage
            
        Returns:
            Object path in data lake
        """
        return (
            f"lake/{org_id}/{cloud_provider}/"
            f"{usage_date.year:04d}/{usage_date.month:02d}/{usage_date.day:02d}/"
            f"raw.jsonl"
        )
    
    async def write_records(
        self,
        org_id: str,
        cloud_provider: str,
        records: List[Dict[str, Any]]
    ) -> str:
        """
        Write records to MinIO.
        
        Args:
            org_id: Organization ID
            cloud_provider: Cloud provider
            records: List of cost records
            
        Returns:
            Path where data was written
        """
        if not records:
            logger.warning("No records to write")
            return ""
        
        # Group records by date
        records_by_date: Dict[date, List[Dict[str, Any]]] = {}
        for record in records:
            usage_date = date.fromisoformat(record["usage_date"])
            if usage_date not in records_by_date:
                records_by_date[usage_date] = []
            records_by_date[usage_date].append(record)
        
        # Write each date's records
        paths = []
        for usage_date, date_records in records_by_date.items():
            path = self.generate_path(org_id, cloud_provider, usage_date)
            
            # Convert records to JSONL format
            jsonl_data = "\n".join(json.dumps(record) for record in date_records)
            data_bytes = jsonl_data.encode("utf-8")
            
            # Upload to MinIO
            try:
                self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=path,
                    data=BytesIO(data_bytes),
                    length=len(data_bytes),
                    content_type="application/jsonl"
                )
                logger.info(f"Wrote {len(date_records)} records to {path}")
                paths.append(path)
            except S3Error as e:
                logger.error(f"Error writing to MinIO: {e}")
                raise
        
        # Return first path (or combine all paths)
        return paths[0] if paths else ""
