# API Guide

## Overview

All services expose REST APIs with OpenAPI (Swagger) documentation available at `/docs` endpoint.

## Common Patterns

### Authentication
All API requests (except health checks) should include an authentication token:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/endpoint
```

### Tenant Context
Multi-tenant APIs require tenant_id in the request:

```json
{
  "tenant_id": "tenant-123",
  "other_field": "value"
}
```

### Pagination
List endpoints support pagination:

```bash
GET /api/resource?skip=0&limit=100
```

### Error Responses
Standard error response format:

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "details": {}
}
```

## Service APIs

### Gateway (Port 8000)

#### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "gateway",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Service Proxy
```bash
GET /{service}/{path}
```

Routes to backend services.

### Auth Service (Port 8001)

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Get Current User
```bash
GET /auth/me
Authorization: Bearer <token>
```

### Tenant Service (Port 8002)

#### List Tenants
```bash
GET /tenants?skip=0&limit=100
```

#### Create Tenant
```bash
POST /tenants
Content-Type: application/json

{
  "name": "Acme Corp",
  "slug": "acme-corp",
  "primary_contact_email": "admin@acme.com",
  "primary_contact_name": "John Doe"
}
```

#### Get Tenant
```bash
GET /tenants/{tenant_id}
```

#### Update Tenant
```bash
PUT /tenants/{tenant_id}
```

#### Delete Tenant
```bash
DELETE /tenants/{tenant_id}
```

### Ingestion Service (Port 8003)

#### Ingest Cost Records
```bash
POST /ingest/costs
Content-Type: application/json

[
  {
    "tenant_id": "tenant-123",
    "resource_id": "i-1234567890",
    "resource_type": "vm",
    "cloud_provider": "aws",
    "region": "us-east-1",
    "service_name": "EC2",
    "cost": "15.50",
    "currency": "USD",
    "billing_period_start": "2024-01-01T00:00:00Z",
    "billing_period_end": "2024-01-01T23:59:59Z",
    "tags": {"env": "production"}
  }
]
```

#### Get Job Status
```bash
GET /ingest/jobs/{job_id}
```

#### Trigger Provider Sync
```bash
POST /ingest/sync/{provider}?tenant_id=tenant-123
```

### Budgets Service (Port 8005)

#### List Budgets
```bash
GET /budgets?tenant_id=tenant-123
```

#### Create Budget
```bash
POST /budgets
Content-Type: application/json

{
  "tenant_id": "tenant-123",
  "name": "Monthly AWS Budget",
  "amount": "10000.00",
  "currency": "USD",
  "period": "monthly",
  "alert_threshold": 80
}
```

#### Get Budget
```bash
GET /budgets/{budget_id}
```

#### Update Budget
```bash
PUT /budgets/{budget_id}
```

#### Delete Budget
```bash
DELETE /budgets/{budget_id}
```

#### Get Budget Alerts
```bash
GET /budgets/{budget_id}/alerts
```

### Query Service (Port 8006)

#### Execute Query
```bash
POST /query/execute
Content-Type: application/json

{
  "tenant_id": "tenant-123",
  "sql": "SELECT resource_type, SUM(cost) as total FROM costs WHERE tenant_id = 'tenant-123' GROUP BY resource_type"
}
```

#### Get Query Status
```bash
GET /query/{query_id}
```

#### Cancel Query
```bash
POST /query/cancel/{query_id}
```

### Workflows Service (Port 8004)

#### List Workflows
```bash
GET /workflows?tenant_id=tenant-123
```

#### Create Workflow
```bash
POST /workflows
Content-Type: application/json

{
  "tenant_id": "tenant-123",
  "name": "Daily Cost Report",
  "description": "Generate daily cost report",
  "schedule": "0 9 * * *",
  "tasks": [
    {"type": "query", "query": "SELECT ..."},
    {"type": "export", "format": "csv"}
  ]
}
```

#### Run Workflow
```bash
POST /workflows/{workflow_id}/run
```

#### Cancel Workflow
```bash
POST /workflows/{workflow_id}/cancel
```

### Integrations Service (Port 8007)

#### List Integrations
```bash
GET /integrations?tenant_id=tenant-123
```

#### Create Integration
```bash
POST /integrations
Content-Type: application/json

{
  "tenant_id": "tenant-123",
  "provider": "aws",
  "name": "AWS Production",
  "credentials": {
    "access_key_id": "AKIA...",
    "secret_access_key": "..."
  }
}
```

#### Sync Integration
```bash
POST /integrations/{integration_id}/sync
```

#### Test Integration
```bash
POST /integrations/{integration_id}/test
```

## Testing APIs

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# With authentication
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/endpoint

# POST with JSON
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"key": "value"}' \
     http://localhost:8000/api/endpoint
```

### Using httpie

```bash
# Install httpie
pip install httpie

# Make requests
http GET http://localhost:8000/health
http POST http://localhost:8001/auth/login email=user@example.com password=password
```

### Using Swagger UI

Visit http://localhost:{port}/docs for interactive API documentation.

## Rate Limiting (Future)

Rate limits will be applied per tenant:
- 1000 requests per minute per tenant
- 100,000 requests per day per tenant

Response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1234567890
```

## Versioning (Future)

API versioning via URL path:
```
/v1/tenants
/v2/tenants
```
