# FastAPI Service Template Guide

## Overview

This repository uses a standardized FastAPI service template based on `finops-common` package. All services follow consistent patterns for:

- Health and readiness checks
- Request ID tracking
- Organization/tenant context
- Structured JSON logging
- RBAC authorization
- OpenTelemetry instrumentation
- Docker containerization

## Service Structure

Each service follows this structure:

```
services/<service-name>/
├── Dockerfile              # Multi-stage Docker build
├── requirements.txt        # Python dependencies
├── README.md              # Service-specific documentation
├── src/
│   ├── main.py            # Application entry point
│   ├── routes/            # API route handlers
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   └── db/                # Database models (if needed)
└── tests/
    └── test_main.py       # Unit tests
```

## Creating a New Service

### 1. Create Service Structure

```bash
mkdir -p services/my-service/src services/my-service/tests
```

### 2. Create requirements.txt

```txt
# My Service Requirements
-e ../../packages/common-py

fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-multipart>=0.0.6

# Add service-specific dependencies here
```

### 3. Create main.py

```python
from fastapi import APIRouter
from finops_common import Settings, create_app, get_logger

logger = get_logger(__name__)

settings = Settings(
    service_name="my-service",
    service_version="1.0.0",
    port=8000,
)

app = create_app(
    title="My Service",
    version="1.0.0",
    description="Service description",
    settings=settings,
)

router = APIRouter(prefix="/api/v1", tags=["MyService"])

@router.get("/example")
async def example():
    logger.info("Example endpoint called")
    return {"message": "Hello World"}

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
```

### 4. Create Dockerfile

Use the template in `services/Dockerfile.template` or generate with:

```bash
# Update the script with your service
bash scripts/generate_service_dockerfiles.sh
```

## Features Provided by finops-common

### Automatic Endpoints

All services automatically get:

- `GET /health` - Basic health check
- `GET /ready` - Readiness check with dependency checks
- `GET /docs` - OpenAPI documentation (if enabled)

### Request Context

Access request context anywhere in your code:

```python
from finops_common.context import get_request_id, get_org_id, get_tenant_id, get_user_id

@router.get("/example")
async def example():
    request_id = get_request_id()  # Auto-generated or from X-Request-ID header
    org_id = get_org_id()          # From X-Org-ID header
    tenant_id = get_tenant_id()    # From X-Tenant-ID header
    user_id = get_user_id()        # From X-User-ID header
    
    return {"request_id": request_id}
```

### Structured Logging

```python
from finops_common import get_logger

logger = get_logger(__name__)

@router.post("/items")
async def create_item(item: Item):
    logger.info("Creating item", extra={"item_id": item.id, "user_id": "123"})
    # Logs include: timestamp, level, logger, message, request_id, org_id, trace_id, span_id
    return {"status": "created"}
```

### RBAC Authorization

```python
from finops_common import require_permission, Permission

@router.get("/admin")
@require_permission(Permission.ADMIN)
async def admin_endpoint():
    return {"message": "Admin only"}

@router.get("/costs")
@require_permission(Permission.COSTS_READ)
async def read_costs():
    return {"costs": []}
```

### Configuration

Use environment variables or .env file:

```python
from finops_common import Settings

settings = Settings(
    service_name="my-service",
    port=8000,
    log_level="INFO",
    database_url="postgresql://...",
    redis_url="redis://...",
    otel_enabled=True,
)
```

### Health Checks

Register custom readiness checks:

```python
@app.on_event("startup")
async def startup_event():
    # Register database check
    async def check_database():
        try:
            # Test database connection
            return {"status": "ready", "latency_ms": 5}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    app.state.health_checker.register_ready_check("database", check_database)
```

## Service Port Allocation

| Service | Port | Status |
|---------|------|--------|
| gateway-api | 8000 | ✅ Implemented |
| auth-service | 8001 | ✅ Implemented |
| tenant-service | 8002 | ✅ Implemented |
| billing-service | 8003 | ✅ Template |
| cost-ingestion-service | 8004 | ✅ Template |
| cost-normalization-service | 8005 | ✅ Template |
| virtual-tagging-service | 8006 | ✅ Template |
| allocation-service | 8007 | ✅ Template |
| recommendations-service | 8008 | ✅ Template |
| budgets-alerts-service | 8009 | ✅ Template |
| workflows-service | 8010 | ✅ Template |
| integrations-service | 8011 | ✅ Template |
| reporting-service | 8012 | ✅ Template |
| query-service | 8013 | ✅ Template |
| data-quality-service | 8014 | ✅ Template |
| metering-service | 8015 | ✅ Template |
| audit-service | 8016 | ✅ Template |
| admin-ops-service | 8017 | ✅ Template |

## Development Workflow

### Local Development

```bash
# Install dependencies
cd services/my-service
pip install -r requirements.txt

# Run with auto-reload
python src/main.py

# Or with uvicorn directly
uvicorn src.main:app --reload --port 8000
```

### Docker Development

```bash
# Build image
docker build -t my-service:latest -f services/my-service/Dockerfile .

# Run container
docker run -p 8000:8000 \
    -e LOG_LEVEL=DEBUG \
    -e OTEL_ENABLED=true \
    my-service:latest
```

### Testing

```bash
# Run tests
cd services/my-service
pytest tests/

# With coverage
pytest --cov=src --cov-report=html tests/
```

## Docker Best Practices

Our Dockerfiles follow these best practices:

1. **Multi-stage builds** - Smaller final images
2. **Non-root user** - Security best practice
3. **Health checks** - Container orchestration ready
4. **Layer caching** - Faster builds
5. **Minimal base image** - python:3.11-slim
6. **Security scanning** - Ready for Snyk/Trivy

## Environment Variables

Common environment variables (from finops-common):

```bash
# Service Identity
SERVICE_NAME=my-service
SERVICE_VERSION=1.0.0
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Logging
LOG_LEVEL=INFO
LOG_JSON=true

# OpenTelemetry
OTEL_ENABLED=true
OTEL_ENDPOINT=http://otel-collector:4317

# Database
DATABASE_URL=postgresql://user:pass@localhost/db
DATABASE_POOL_SIZE=5

# Redis
REDIS_URL=redis://redis:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# CORS
CORS_ENABLED=true
CORS_ORIGINS=["*"]
```

## Deployment

### Kubernetes

Each service has a Helm chart in `infra/helm/charts/<service-name>/`.

```bash
# Deploy service
helm install my-service infra/helm/charts/my-service/ \
    --set image.tag=v1.0.0 \
    --set env.LOG_LEVEL=INFO
```

### Docker Compose

Services can be run with docker-compose:

```yaml
version: '3.8'
services:
  my-service:
    build:
      context: .
      dockerfile: services/my-service/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=DEBUG
      - OTEL_ENABLED=true
    depends_on:
      - postgres
      - redis
```

## Troubleshooting

### Service won't start

1. Check health endpoint: `curl http://localhost:8000/health`
2. Check logs: `docker logs <container-id>`
3. Verify environment variables
4. Check dependencies in readiness endpoint

### Missing request context

Ensure middleware is running:
```python
# This is automatic with create_app()
app.add_middleware(RequestContextMiddleware)
```

### RBAC not working

1. Ensure user context is set (X-User-ID header)
2. Implement `RBACGuard.get_user_permissions()` method
3. Check permission enum values

## Next Steps

1. Implement database models and migrations
2. Add API route handlers
3. Write unit and integration tests
4. Configure CI/CD pipeline
5. Create Helm chart for Kubernetes
6. Add monitoring and alerting

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
