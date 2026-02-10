# Tenant Service

Tenant, Organization, and Workspace Management Service for the FinOps SaaS Platform.

## Overview

The Tenant Service is responsible for managing the organizational hierarchy and multi-tenant structure of the platform:

- **Organizations** - Top-level entities representing companies or business units
- **Tenants** - Logical groupings within organizations (e.g., environments, regions, teams)
- **Cloud Accounts** - Cloud provider accounts (AWS, Azure, GCP, etc.) linked to tenants
- **Persona Views** - Customizable dashboards and views for different user personas

## Features

- ✅ Full CRUD operations for all entities
- ✅ **org_id enforcement** - All tenant/account/view operations scoped to organization
- ✅ **Audit logging** - Complete audit trail for all create/update/delete operations
- ✅ **Soft deletes** - Entities are deactivated rather than deleted
- ✅ **Pagination support** - Efficient listing of large datasets
- ✅ **Multi-cloud support** - AWS, Azure, GCP, Oracle, Akamai, Datacenter
- ✅ **Persona customization** - Views for Executive, FinOps, Engineering, Product Ops, etc.

## Database Models

### Organization
- **id** - Unique identifier (UUID)
- **name** - Organization name
- **slug** - URL-friendly identifier (auto-generated)
- **description** - Optional description
- **industry** - Industry category
- **settings** - JSON configuration
- **is_active** - Soft delete flag
- **created_at**, **updated_at** - Timestamps
- **created_by**, **updated_by** - User tracking

### Tenant
- **id** - Unique identifier (UUID)
- **org_id** - Organization reference (enforced)
- **name** - Tenant name
- **slug** - URL-friendly identifier (unique within org)
- **description** - Optional description
- **settings** - JSON configuration
- **is_active** - Soft delete flag
- **created_at**, **updated_at** - Timestamps
- **created_by**, **updated_by** - User tracking

### CloudAccount
- **id** - Unique identifier (UUID)
- **org_id** - Organization reference (enforced)
- **tenant_id** - Optional tenant reference
- **name** - Account name
- **provider** - Cloud provider (aws, azure, gcp, oracle, akamai, datacenter)
- **account_id** - Provider-specific account ID
- **account_name** - Provider account name
- **credentials** - Encrypted credentials/references
- **settings** - JSON configuration
- **is_active** - Soft delete flag
- **is_connected** - Connection status
- **last_sync_at** - Last synchronization timestamp
- **created_at**, **updated_at** - Timestamps
- **created_by**, **updated_by** - User tracking

### PersonaView
- **id** - Unique identifier (UUID)
- **org_id** - Organization reference (enforced)
- **name** - View name
- **slug** - URL-friendly identifier (unique within org)
- **persona** - Persona type (executive, finops, engineering, product_ops, etc.)
- **config** - JSON view configuration (widgets, filters, etc.)
- **description** - Optional description
- **is_default** - Default view for persona
- **is_shared** - Shared across organization
- **owner_id** - View owner
- **is_active** - Soft delete flag
- **created_at**, **updated_at** - Timestamps
- **created_by**, **updated_by** - User tracking

### AuditLog
- **id** - Auto-incrementing ID
- **entity_type** - Type of entity (organization, tenant, cloud_account, persona_view)
- **entity_id** - Entity identifier
- **action** - Action performed (create, update, delete)
- **org_id** - Organization context
- **user_id** - User who performed action
- **changes** - JSON of old/new values
- **created_at** - Timestamp
- **ip_address**, **user_agent** - Request context
- **request_id** - Request tracking

## API Endpoints

### Organizations

```
POST   /api/v1/orgs              - Create organization
GET    /api/v1/orgs              - List organizations
GET    /api/v1/orgs/{org_id}     - Get organization
PUT    /api/v1/orgs/{org_id}     - Update organization
DELETE /api/v1/orgs/{org_id}     - Delete organization (soft)
```

### Tenants

All tenant endpoints require `X-Org-ID` header.

```
POST   /api/v1/tenants              - Create tenant
GET    /api/v1/tenants              - List tenants
GET    /api/v1/tenants/{tenant_id}  - Get tenant
PUT    /api/v1/tenants/{tenant_id}  - Update tenant
DELETE /api/v1/tenants/{tenant_id}  - Delete tenant (soft)
```

### Cloud Accounts

All cloud account endpoints require `X-Org-ID` header.

```
POST   /api/v1/cloud-accounts              - Create cloud account
GET    /api/v1/cloud-accounts              - List cloud accounts
       ?tenant_id=xxx                        - Filter by tenant
       ?provider=aws                         - Filter by provider
GET    /api/v1/cloud-accounts/{account_id}  - Get cloud account
PUT    /api/v1/cloud-accounts/{account_id}  - Update cloud account
DELETE /api/v1/cloud-accounts/{account_id}  - Delete cloud account (soft)
```

### Persona Views

All view endpoints require `X-Org-ID` header.

```
POST   /api/v1/views              - Create persona view
GET    /api/v1/views              - List persona views
       ?persona=executive           - Filter by persona
       ?is_default=true             - Filter by default views
       ?is_shared=true              - Filter by shared views
GET    /api/v1/views/{view_id}    - Get persona view
PUT    /api/v1/views/{view_id}    - Update persona view
DELETE /api/v1/views/{view_id}    - Delete persona view (soft)
```

## Usage Examples

### Create Organization

```bash
curl -X POST http://localhost:8002/api/v1/orgs \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user-123" \
  -d '{
    "name": "Acme Corporation",
    "description": "Leading cloud solutions provider",
    "industry": "Technology",
    "settings": {
      "timezone": "America/New_York",
      "currency": "USD"
    }
  }'
```

### Create Tenant

```bash
curl -X POST http://localhost:8002/api/v1/tenants \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-123" \
  -H "X-User-ID: user-123" \
  -d '{
    "name": "Production",
    "description": "Production environment",
    "settings": {"env": "prod"}
  }'
```

### Create Cloud Account

```bash
curl -X POST http://localhost:8002/api/v1/cloud-accounts \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-123" \
  -H "X-User-ID: user-123" \
  -d '{
    "name": "AWS Production",
    "provider": "aws",
    "account_id": "123456789012",
    "tenant_id": "tenant-456",
    "settings": {"region": "us-east-1"}
  }'
```

### Create Persona View

```bash
curl -X POST http://localhost:8002/api/v1/views \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-123" \
  -H "X-User-ID: user-123" \
  -d '{
    "name": "Executive Dashboard",
    "persona": "executive",
    "config": {
      "widgets": [
        {"type": "total_cost", "period": "monthly"},
        {"type": "cost_trend", "period": "6months"}
      ]
    },
    "is_default": true,
    "is_shared": true
  }'
```

## Configuration

Environment variables:

```bash
# Database
TENANT_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/tenant_db
TENANT_DB_ECHO=false
TENANT_DB_POOL_SIZE=10
TENANT_DB_MAX_OVERFLOW=20

# Service
TENANT_SERVICE_NAME=tenant-service
TENANT_SERVICE_VERSION=1.0.0
TENANT_SERVICE_PORT=8002
TENANT_SERVICE_HOST=0.0.0.0
TENANT_SERVICE_RELOAD=true  # Development only
```

## Development

### Setup

```bash
# Install dependencies
cd services/tenant-service
pip install -r requirements.txt

# Set environment variables
export TENANT_DATABASE_URL=postgresql+asyncpg://finops:finops@localhost:5432/tenant_db

# Run migrations (if using Alembic)
alembic upgrade head

# Start service
python src/main.py
```

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_organizations.py -v
```

### Seed Demo Data

```bash
# Start the service first
python src/main.py

# In another terminal, run seed script
cd ../..
./scripts/seed_demo_data.sh
```

This will create:
- 3 Organizations (Acme Corporation, TechStart Inc, Global Enterprises)
- 6 Tenants (Production, Staging, Dev environments)
- 6 Cloud Accounts (AWS, Azure, GCP)
- 5 Persona Views (Executive, FinOps, Engineering, Product Ops, Tenant Admin)

## Security

- **org_id enforcement**: All operations enforce organization context
- **Audit logging**: Complete audit trail with user/IP/timestamp
- **Soft deletes**: Data is never permanently deleted
- **Credentials**: Cloud credentials stored as JSON (should be encrypted in production)
- **RBAC integration**: Uses finops-common RBAC guards

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
└────────┬────────┘
         │
    ┌────┴────┐
    │  CRUD   │  ← Audit Logging
    └────┬────┘
         │
    ┌────┴────┐
    │Database │  ← PostgreSQL + AsyncPG
    └─────────┘
```

## Monitoring

Health check endpoints:
- `GET /health` - Basic health check
- `GET /ready` - Readiness check with database connection

Metrics (via OpenTelemetry):
- Request latency
- Database query performance
- Audit log creation
- Error rates

## Roadmap

- [ ] Alembic migrations
- [ ] GraphQL API
- [ ] Bulk operations
- [ ] Export/import functionality
- [ ] Advanced search and filtering
- [ ] View templates
- [ ] Tenant quotas and limits
- [ ] Cloud account validation
- [ ] Automated cost sync scheduling

## License

Copyright © 2024 FinOps SaaS Platform
