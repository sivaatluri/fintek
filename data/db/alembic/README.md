# Database Migrations

This directory contains Alembic database migrations for the FinOps SaaS platform.

## Overview

The database schema is managed using [Alembic](https://alembic.sqlalchemy.org/), a lightweight database migration tool for SQLAlchemy. All schema changes are version-controlled through migration scripts.

## Directory Structure

```
data/db/alembic/
├── alembic.ini          # Alembic configuration
├── env.py               # Migration environment setup
├── script.py.mako       # Template for new migrations
├── README               # This file
└── versions/            # Migration scripts
    ├── 001_initial_schema.py
    ├── 002_tenant_cloud_accounts.py
    ├── 003_persona_views_audit.py
    ├── 004_budgets_anomalies.py
    ├── 005_workflows.py
    └── 006_integrations.py
```

## Migrations

### 001: Initial Schema (Core Auth & Tenant)
Creates the foundational tables:
- **organizations** - Top-level organizational entities
- **users** - User accounts with OIDC/SAML support
- **user_organizations** - User-org associations
- **roles** - RBAC roles
- **permissions** - Fine-grained permissions
- **user_roles** - User-role assignments (with org context)
- **role_permissions** - Role-permission mappings
- **sessions** - User sessions with token management

### 002: Tenant & Cloud Accounts
Creates tenant management tables:
- **tenants** - Logical groupings within organizations
- **cloud_accounts** - Cloud provider account connections (AWS, Azure, GCP, Oracle, Akamai, Datacenter)

### 003: Persona Views & Audit
Creates configuration and audit tables:
- **persona_views** - Saved dashboards for different personas (Executive, FinOps, Engineering, etc.)
- **audit_logs** - Comprehensive audit trail for all entity changes

### 004: Budgets & Anomalies
Creates cost management tables:
- **budgets** - Budget definitions with alerts
- **anomalies** - Cost anomaly detection and tracking

### 005: Workflows
Creates workflow automation tables:
- **workflow_definitions** - Workflow templates and configurations
- **workflow_executions** - Workflow execution history
- **workflow_steps** - Individual step execution details
- **workflow_external_refs** - Links to external systems (Jira, ServiceNow, etc.)

### 006: Integrations
Creates integration tables:
- **integrations** - External system configurations (Slack, Teams, Jira, ServiceNow, etc.)
- **integration_deliveries** - Delivery tracking with retry logic

## Usage

### Running Migrations

Use the provided script or Makefile target:

```bash
# Using Makefile (recommended)
make db-migrate

# Using script directly
./scripts/run_migrations.sh

# Using alembic directly
cd data/db/alembic
alembic upgrade head
```

### Common Commands

```bash
# Upgrade to latest
make db-migrate
# or
./scripts/run_migrations.sh upgrade

# Show current revision
./scripts/run_migrations.sh current

# Show migration history
./scripts/run_migrations.sh history

# Downgrade one revision
./scripts/run_migrations.sh downgrade -1

# Upgrade to specific revision
./scripts/run_migrations.sh upgrade 003

# Create new migration (auto-generate from model changes)
./scripts/run_migrations.sh revision "description of changes"

# Show help
./scripts/run_migrations.sh help
```

### Environment Variables

Set `DATABASE_URL` to override the default database connection:

```bash
export DATABASE_URL="postgresql://user:pass@host:port/dbname"
make db-migrate
```

Or add to `.env` file:
```
DATABASE_URL=postgresql://finops:finops_dev@localhost:5432/finops
```

## Database Schema Overview

### Entity Relationships

```
organizations (1) ─── (N) tenants
                 └─── (N) cloud_accounts
                 └─── (N) persona_views
                 └─── (N) user_organizations ─── (1) users
                 └─── (N) budgets
                 └─── (N) anomalies
                 └─── (N) workflow_definitions
                 └─── (N) integrations
                 └─── (N) audit_logs

users (1) ─── (N) user_roles ─── (1) roles (1) ─── (N) role_permissions ─── (1) permissions
      └─── (N) sessions

workflow_definitions (1) ─── (N) workflow_executions (1) ─── (N) workflow_steps
                                                             └─── (N) workflow_external_refs

integrations (1) ─── (N) integration_deliveries
```

### Key Features

1. **Multi-tenancy**: All data is scoped to organizations with proper foreign keys
2. **RBAC**: Comprehensive role-based access control with permissions
3. **Audit Trail**: All changes tracked in audit_logs table
4. **Soft Deletes**: Most tables use `is_active` flag instead of hard deletes
5. **Timestamps**: All tables have `created_at` and `updated_at` timestamps
6. **Indexes**: Comprehensive indexing for query performance

## Creating New Migrations

### Manual Migration

1. Create a new migration file:
```bash
./scripts/run_migrations.sh revision "add new feature"
```

2. Edit the generated file in `versions/` directory

3. Implement `upgrade()` and `downgrade()` functions

4. Test the migration:
```bash
./scripts/run_migrations.sh upgrade
./scripts/run_migrations.sh downgrade -1
./scripts/run_migrations.sh upgrade
```

### Auto-generate from Models

1. Update your SQLAlchemy models
2. Generate migration:
```bash
cd data/db/alembic
alembic revision --autogenerate -m "description"
```
3. Review and edit the generated migration
4. Test thoroughly

## Best Practices

1. **Always review auto-generated migrations** - They may not be perfect
2. **Test both upgrade and downgrade** - Ensure reversibility
3. **Use transactions** - Migrations run in transactions by default
4. **Add indexes for performance** - Consider query patterns
5. **Document complex migrations** - Add comments explaining the logic
6. **Never edit applied migrations** - Create new migrations instead
7. **Back up before production migrations** - Always have a recovery plan

## Troubleshooting

### Migration fails with "relation already exists"

The database may already have tables. Options:
1. Drop all tables and re-run migrations (dev only)
2. Stamp the database at current state: `./scripts/run_migrations.sh stamp head`

### Can't import models

Ensure Python path is set correctly. The `env.py` adds project root to sys.path.

### Database connection refused

Check:
1. PostgreSQL is running: `make ps`
2. DATABASE_URL is correct
3. Database exists: `psql -U finops -d finops`

### Alembic not found

Install dependencies:
```bash
pip install alembic psycopg2-binary
```

## Production Deployment

### Pre-deployment Checklist

- [ ] Backup production database
- [ ] Test migrations on staging environment
- [ ] Review all SQL that will be executed
- [ ] Plan rollback strategy
- [ ] Schedule maintenance window if needed
- [ ] Notify stakeholders

### Running in Production

```bash
# 1. Backup database
pg_dump -U finops finops > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Run migrations
DATABASE_URL="postgresql://user:pass@prod-host/finops" make db-migrate

# 3. Verify
DATABASE_URL="postgresql://user:pass@prod-host/finops" ./scripts/run_migrations.sh current

# 4. If issues, rollback
DATABASE_URL="postgresql://user:pass@prod-host/finops" ./scripts/run_migrations.sh downgrade -1
```

### Rolling Back

If a migration causes issues:

```bash
# Downgrade by one revision
./scripts/run_migrations.sh downgrade -1

# Or downgrade to specific revision
./scripts/run_migrations.sh downgrade 004

# Restore from backup if needed
psql -U finops finops < backup_file.sql
```

## Integration with Docker

Migrations can be run automatically on container startup:

```dockerfile
# In Dockerfile
CMD ["sh", "-c", "./scripts/run_migrations.sh && uvicorn main:app --host 0.0.0.0"]
```

Or in docker-compose:

```yaml
services:
  app:
    command: sh -c "./scripts/run_migrations.sh && uvicorn main:app"
    depends_on:
      postgres:
        condition: service_healthy
```

## Support

For issues or questions:
1. Check this README
2. Review Alembic documentation: https://alembic.sqlalchemy.org/
3. Check migration logs in `data/db/alembic/`
4. Contact the platform team

## License

Copyright © 2026 FinOps SaaS Platform
