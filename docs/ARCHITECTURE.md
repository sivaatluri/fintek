# FinOps SaaS - Service Architecture Overview

## Overview

This repository implements a cloud-agnostic FinOps (Financial Operations) SaaS platform using a microservices architecture. All services are built with FastAPI and follow standardized patterns for observability, security, and deployment.

## Architecture Principles

### 1. **Cloud Agnostic**
- Portable across AWS, Azure, GCP, Oracle, Akamai, and on-premises
- Provider-specific connectors with unified interfaces
- Abstracted data models and query layers

### 2. **Multi-Tenant**
- Organization → Tenant → Workspace hierarchy
- Data isolation at all layers
- Per-tenant customization and policies

### 3. **Event-Driven**
- Kafka-based event bus
- Asynchronous workflow execution
- Real-time alerting and notifications

### 4. **Observability-First**
- OpenTelemetry distributed tracing
- Structured JSON logging
- Prometheus metrics
- Request ID propagation

### 5. **Security & Compliance**
- RBAC/ABAC authorization
- SSO (OIDC/SAML) integration
- Audit trail for all operations
- Encryption at rest and in transit

## Service Catalog

### Core Services

#### 1. Gateway API (Port 8000)
**Purpose:** API Gateway and Backend-for-Frontend  
**Features:**
- Routes requests to microservices
- JWT token validation
- Rate limiting
- Response aggregation
- API documentation

#### 2. Auth Service (Port 8001)
**Purpose:** Authentication and Authorization  
**Features:**
- OIDC/SAML SSO integration
- JWT token generation
- SCIM user provisioning
- Session management
- RBAC policy enforcement

#### 3. Tenant Service (Port 8002)
**Purpose:** Multi-tenancy management  
**Features:**
- Organization management
- Tenant/workspace CRUD
- Cloud account mapping
- User-tenant associations

### Financial Operations Services

#### 4. Billing Service (Port 8003)
**Purpose:** SaaS billing and invoicing  
**Features:**
- Subscription management
- Usage-based billing
- Invoice generation
- Payment processing integration

#### 5. Cost Ingestion Service (Port 8004)
**Purpose:** Orchestrate cloud cost data ingestion  
**Features:**
- Scheduled ingestion jobs
- Connector orchestration
- Incremental updates
- Data validation

#### 6. Cost Normalization Service (Port 8005)
**Purpose:** Transform raw costs to canonical schema  
**Features:**
- Multi-cloud normalization
- Virtual tagging application
- Data quality scoring
- Schema versioning

#### 7. Virtual Tagging Service (Port 8006)
**Purpose:** Rule-based tag enrichment  
**Features:**
- Tag inference rules
- Pattern matching
- ML-based suggestions
- Tag propagation

#### 8. Allocation Service (Port 8007)
**Purpose:** Cost allocation and unit economics  
**Features:**
- Custom allocation rules
- Chargeback/showback
- Unit economics calculations
- Metric-based allocation

### Optimization Services

#### 9. Recommendations Service (Port 8008)
**Purpose:** Cost optimization recommendations  
**Features:**
- Rightsizing analysis
- Reserved instance recommendations
- Idle resource detection
- Savings calculations
- Workflow integration

#### 10. Budgets & Alerts Service (Port 8009)
**Purpose:** Budget tracking and anomaly detection  
**Features:**
- Budget management
- Threshold monitoring
- Anomaly detection (ML-based)
- Forecast generation
- Event emission

#### 11. Workflows Service (Port 8010)
**Purpose:** Automated workflows and actions  
**Features:**
- Event-driven workflows
- Condition evaluation
- Action execution
- Idempotency and retry
- Escalation policies

### Integration Services

#### 12. Integrations Service (Port 8011)
**Purpose:** External system integrations  
**Features:**
- Jira/ServiceNow ticketing
- Slack/Teams notifications
- Email delivery
- Webhook dispatch
- PagerDuty alerts

#### 13. Reporting Service (Port 8012)
**Purpose:** Report generation and scheduling  
**Features:**
- Scheduled reports
- Custom dashboards
- Export to PDF/CSV
- Email delivery
- Template management

### Data Services

#### 14. Query Service (Port 8013)
**Purpose:** Unified query layer  
**Features:**
- Portable query engine (Trino)
- Cloud-specific adapters (Athena, BigQuery, Synapse)
- Query optimization
- Result caching
- Access control

#### 15. Data Quality Service (Port 8014)
**Purpose:** Data quality and lineage  
**Features:**
- Completeness checks
- Reconciliation
- Data lineage tracking
- Quality scoring
- Alerting

### Support Services

#### 16. Metering Service (Port 8015)
**Purpose:** Application metrics for unit economics  
**Features:**
- API usage tracking
- Feature usage metrics
- User activity logging
- Cost attribution

#### 17. Audit Service (Port 8016)
**Purpose:** Audit trail and compliance  
**Features:**
- All operations logging
- Change tracking
- Compliance reporting
- Retention policies

#### 18. Admin Ops Service (Port 8017)
**Purpose:** Support and operations tooling  
**Features:**
- Tenant operations automation
- Support diagnostics
- Data migrations
- Health monitoring

## Common Patterns

### Service Template

All services implement:

```python
from finops_common import create_app, Settings

settings = Settings(
    service_name="my-service",
    port=8000,
)

app = create_app(
    title="My Service",
    version="1.0.0",
    settings=settings,
)
```

### Standard Endpoints

Every service provides:
- `GET /health` - Health check
- `GET /ready` - Readiness with dependency checks
- `GET /docs` - OpenAPI documentation
- `GET /api/v1/*` - Service-specific APIs

### Request Context

All services track:
- Request ID (auto-generated or from header)
- Organization ID
- Tenant ID
- User ID
- Trace ID / Span ID

### Logging

Structured JSON logs with:
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "logger": "service.module",
  "message": "Operation completed",
  "request_id": "uuid",
  "org_id": "org-123",
  "tenant_id": "tenant-456",
  "user_id": "user-789",
  "trace_id": "hex-trace-id",
  "span_id": "hex-span-id"
}
```

### Authorization

RBAC with predefined permissions:
```python
from finops_common import require_permission, Permission

@router.get("/costs")
@require_permission(Permission.COSTS_READ)
async def get_costs():
    return {"costs": []}
```

## Data Flow

### 1. Cost Ingestion Flow
```
Cloud Provider APIs
  → Connectors (AWS/Azure/GCP/etc)
  → Cost Ingestion Service
  → Raw Cost Storage (S3/Blob/GCS)
  → Cost Normalization Service
  → Normalized Cost Storage
  → Virtual Tagging Service
  → Allocation Service
  → Allocated Cost Storage
```

### 2. Recommendation Flow
```
Cost Data
  → Recommendations Service
  → Recommendation Event
  → Workflows Service
  → Action Execution
  → Integrations Service
  → External Systems (Jira/Slack/etc)
```

### 3. Budget Alert Flow
```
Cost Data
  → Budgets & Alerts Service
  → Budget Threshold Event
  → Workflows Service
  → Notification Action
  → Integrations Service
  → User Notification
```

## Technology Stack

### Core
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Validation:** Pydantic

### Data Storage
- **Relational:** PostgreSQL
- **Cache:** Redis
- **Object Storage:** MinIO/S3/Blob/GCS
- **Query Engine:** Trino (portable)

### Messaging
- **Event Bus:** Kafka
- **Message Format:** JSON with Avro schemas

### Observability
- **Tracing:** OpenTelemetry
- **Logging:** Pino (JSON)
- **Metrics:** Prometheus
- **Visualization:** Grafana

### Security
- **SSO:** OIDC/SAML (Keycloak)
- **Authorization:** Custom RBAC/ABAC
- **Secrets:** Vault/AWS SM/Azure KV

### Deployment
- **Container:** Docker (multi-stage builds)
- **Orchestration:** Kubernetes
- **IaC:** Terraform
- **Packaging:** Helm Charts
- **CI/CD:** GitHub Actions

## Development Workflow

### Local Development

1. **Start infrastructure:**
```bash
make dev-up  # PostgreSQL, Redis, Kafka, etc.
```

2. **Run service:**
```bash
cd services/my-service
pip install -r requirements.txt
python src/main.py
```

3. **Run tests:**
```bash
pytest tests/ --cov
```

### Docker Development

```bash
# Build
docker build -t my-service:latest -f services/my-service/Dockerfile .

# Run
docker run -p 8000:8000 my-service:latest
```

### Testing Strategy

1. **Unit Tests:** Test individual functions/classes
2. **Integration Tests:** Test service-to-service communication
3. **Contract Tests:** Validate data schemas
4. **E2E Tests:** Full workflow validation

## Deployment Architecture

### Kubernetes

```
Namespace: finops-prod
├── Gateway API (3 replicas)
├── Auth Service (2 replicas)
├── Tenant Service (2 replicas)
├── Cost Services (scaled independently)
├── Query Service (10 replicas)
└── Support Services (1-2 replicas)
```

### Scaling Strategy

- **Gateway API:** Auto-scale based on request rate
- **Query Service:** High replica count for read load
- **Cost Ingestion:** Scheduled jobs, not always running
- **Recommendations:** CPU-based auto-scaling
- **Support Services:** Minimal replicas

## Monitoring & Alerting

### Key Metrics

- Request latency (p50, p95, p99)
- Error rates by service
- Queue depth (Kafka)
- Database connection pool usage
- Cache hit rates
- Cost data freshness
- Recommendation coverage

### Alerts

- Service down (health check failure)
- High error rate (>1%)
- High latency (p95 >500ms)
- Database connection exhaustion
- Kafka consumer lag
- Cost data staleness (>24h)

## Security Considerations

### Authentication
- All inter-service communication uses mutual TLS
- External APIs require JWT tokens
- Service accounts for system operations

### Authorization
- RBAC enforced at API gateway
- ABAC for fine-grained control
- Audit log for all operations

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- PII/sensitive data masking in logs
- Regular security scans (Snyk, Trivy)

## Future Enhancements

1. **GraphQL API:** Unified data fetching
2. **gRPC:** High-performance inter-service communication
3. **Service Mesh:** Istio for advanced traffic management
4. **Multi-Region:** Global deployment for low latency
5. **AI/ML:** Advanced anomaly detection and forecasting
6. **Real-time Streaming:** Live cost updates
7. **Mobile SDK:** Native iOS/Android support

## References

- [Service Template Guide](./SERVICE_TEMPLATE.md)
- [Data Contracts](../data/contracts/README.md)
- [API Documentation](./api/openapi.yaml)
- [Architecture Decisions](./architecture/)
- [Runbooks](./runbooks/)
