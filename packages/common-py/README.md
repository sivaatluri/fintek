# FinOps Common Python Package

Common utilities for FinOps SaaS FastAPI services.

## Features

- **Health & Readiness Endpoints**: Standardized `/health` and `/ready` endpoints
- **Request ID Middleware**: Automatic request ID generation and propagation
- **Organization Context**: Extract and track organization/tenant IDs
- **Structured Logging**: JSON logging with trace context
- **RBAC Guards**: Role-based access control decorators
- **OpenTelemetry Integration**: Distributed tracing and metrics
- **FastAPI Application Factory**: Standardized app initialization

## Installation

```bash
pip install -e packages/common-py
```

## Quick Start

```python
from finops_common import create_app
from finops_common.config import Settings

settings = Settings()
app = create_app(
    title="My Service",
    version="1.0.0",
    settings=settings
)

@app.get("/api/v1/example")
async def example():
    return {"message": "Hello World"}
```

## Usage

### Health Endpoints

Automatically available at:
- `GET /health` - Basic health check
- `GET /ready` - Readiness check (includes dependency checks)

### Request Context

```python
from finops_common.context import get_request_id, get_org_id, get_tenant_id

@app.get("/api/v1/data")
async def get_data():
    request_id = get_request_id()
    org_id = get_org_id()
    tenant_id = get_tenant_id()
    return {"request_id": request_id}
```

### RBAC Guards

```python
from finops_common.rbac import require_permission, Permission

@app.get("/api/v1/admin")
@require_permission(Permission.ADMIN)
async def admin_endpoint():
    return {"message": "Admin only"}
```

### Logging

```python
from finops_common.logging import get_logger

logger = get_logger(__name__)

@app.get("/api/v1/example")
async def example():
    logger.info("Processing request", extra={"user_id": 123})
    return {"status": "ok"}
```

## Configuration

All services use Pydantic settings with environment variable support:

```python
from finops_common.config import Settings

settings = Settings(
    service_name="my-service",
    log_level="INFO",
    otel_enabled=True,
    # ... other settings
)
```

## Development

```bash
# Install with dev dependencies
pip install -e "packages/common-py[dev]"

# Run tests
cd packages/common-py
pytest

# Format code
black src tests
ruff check src tests

# Type checking
mypy src
```

## Testing

```python
from fastapi.testclient import TestClient
from finops_common import create_app

def test_health():
    app = create_app("test", "1.0.0")
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
```

## Architecture

```
packages/common-py/
├── src/finops_common/
│   ├── __init__.py           # Main exports
│   ├── app.py                # FastAPI app factory
│   ├── config.py             # Settings configuration
│   ├── context.py            # Request context management
│   ├── health.py             # Health endpoints
│   ├── logging.py            # Structured logging
│   ├── middleware.py         # Custom middleware
│   ├── rbac.py               # RBAC decorators
│   └── telemetry.py          # OpenTelemetry setup
└── tests/
    ├── test_app.py
    ├── test_context.py
    ├── test_health.py
    └── test_middleware.py
```

## License

See LICENSE file in repository root.
