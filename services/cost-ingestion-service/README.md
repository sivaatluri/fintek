# Cost Ingestion Service

Production-ready cost data ingestion orchestrator with pluggable connectors, MinIO data lake integration, and Kafka event emission.

## Features

- **Pluggable Connector System** - Base interface for multiple cloud providers
- **Mock Connector** - Generates synthetic cost data for 6 cloud providers
- **MinIO Data Lake** - Standard layout: `lake/{org_id}/{cloud}/{yyyy}/{mm}/{dd}/raw.jsonl`
- **Job Orchestration** - Async job scheduling and execution
- **Kafka Events** - Emits `cost.ingestion_completed` events
- **RESTful API** - Full CRUD for ingestion jobs

## Cloud Providers Supported

### Mock Connector (Implemented)
1. **AWS** - EC2, S3, RDS, Lambda
2. **Azure** - Virtual Machines, Storage, SQL Database
3. **GCP** - Compute Engine, Cloud Storage, BigQuery
4. **Oracle** - Compute, Block Storage, Autonomous Database
5. **Akamai** - CDN, WAF, DNS
6. **Datacenter** - Compute, Storage, Network

### Real Connectors (Future)
- AWS CUR (Cost and Usage Reports)
- Azure Cost Management API
- GCP BigQuery Billing Export
- Oracle Cloud Cost API

## API Endpoints

### Jobs
- `POST /api/v1/ingestion/jobs` - Create ingestion job
- `GET /api/v1/ingestion/jobs` - List jobs
- `GET /api/v1/ingestion/jobs/{id}` - Get job details
- `POST /api/v1/ingestion/jobs/{id}/cancel` - Cancel job
- `POST /api/v1/ingestion/jobs/{id}/retry` - Retry failed job

### Connectors
- `GET /api/v1/connectors` - List available connectors
- `POST /api/v1/connectors/test` - Test connector

## Data Lake Layout

```
lake/
├── org-abc123/
│   ├── aws/
│   │   ├── 2024/01/15/raw.jsonl
│   │   └── 2024/01/16/raw.jsonl
│   ├── azure/
│   │   └── 2024/01/15/raw.jsonl
│   └── gcp/
│       └── 2024/01/15/raw.jsonl
```

## Usage

### Create Ingestion Job

```bash
curl -X POST http://localhost:8004/api/v1/ingestion/jobs \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-abc123" \
  -d '{
    "connector_type": "mock",
    "cloud_provider": "aws",
    "config": {
      "records_per_day": 1000,
      "start_date": "2024-01-15",
      "end_date": "2024-01-15"
    }
  }'
```

### List Jobs

```bash
curl http://localhost:8004/api/v1/ingestion/jobs \
  -H "X-Org-ID: org-abc123"
```

### Test Connector

```bash
curl -X POST http://localhost:8004/api/v1/connectors/test \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-abc123" \
  -d '{
    "connector_type": "mock",
    "cloud_provider": "aws",
    "config": {
      "records_per_day": 10,
      "start_date": "2024-01-15",
      "end_date": "2024-01-15"
    }
  }'
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/finops_cost_ingestion

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=cost-data-lake

# Service
SERVICE_NAME=cost-ingestion-service
PORT=8004
```

## Connector Interface

### Creating a New Connector

```python
from connectors.base import BaseConnector
from typing import List, Dict, Any
from datetime import date

class MyConnector(BaseConnector):
    async def fetch_data(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        # Implement data fetching
        return records
    
    async def validate_config(self) -> bool:
        # Validate configuration
        return True

# Register connector
from connectors.registry import connector_registry
connector_registry.register("my_connector", MyConnector)
```

## Event Schema

### cost.ingestion_completed Event

```json
{
  "event_id": "evt-job-123",
  "event_type": "cost.ingestion_completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "cost-ingestion-service",
  "org_id": "org-abc123",
  "payload": {
    "job_id": "job-456",
    "org_id": "org-abc123",
    "cloud_provider": "aws",
    "start_date": "2024-01-15",
    "end_date": "2024-01-15",
    "records_ingested": 1000,
    "status": "completed",
    "duration_seconds": 12.5,
    "data_lake_path": "lake/org-abc123/aws/2024/01/15/raw.jsonl"
  },
  "routing": {
    "priority": "normal",
    "channels": ["workflow", "notification"]
  }
}
```

## Development

### Run Tests

```bash
pytest tests/
```

### Run Service

```bash
python -m src.main
```

## Production Deployment

1. Set up PostgreSQL database
2. Run Alembic migrations
3. Configure MinIO/S3 bucket
4. Set environment variables
5. Deploy service (Docker/K8s)
6. Configure Kafka for event emission

## Future Enhancements

- Implement real AWS CUR connector
- Implement real Azure Cost connector
- Implement real GCP Billing connector
- Add Parquet format support
- Add data compression
- Add data validation service
- Add retry logic with exponential backoff
- Add job scheduling with cron expressions
