# Database Migrations Guide

## Overview

The FinOps SaaS platform uses Alembic for database migrations. This guide covers everything you need to know about managing database schema changes.

## Quick Start

```bash
# 1. Start PostgreSQL
make dev-up

# 2. Run all migrations
make db-migrate

# 3. Verify
./scripts/run_migrations.sh current

# 4. Seed demo data
make seed-db
```

## Migration Files

All migrations are located in `data/db/alembic/versions/`:

| Migration | Tables Created | Description |
|-----------|----------------|-------------|
| **001** | 8 tables | Core identity & auth (users, roles, permissions, sessions) |
| **002** | 2 tables | Tenant management (tenants, cloud_accounts) |
| **003** | 2 tables | Configuration (persona_views, audit_logs) |
| **004** | 2 tables | Cost management (budgets, anomalies) |
| **005** | 4 tables | Workflow automation (definitions, executions, steps, external refs) |
| **006** | 2 tables | Integrations (integrations, deliveries) |

**Total: 22 tables created**

## Database Schema

### Core Tables

#### Identity & Authentication
- `organizations` - Top-level organizational entities
- `users` - User accounts with OIDC/SAML support
- `user_organizations` - User-organization associations
- `roles` - RBAC roles (system and custom)
- `permissions` - Fine-grained permissions (resource:action)
- `user_roles` - User-role assignments (with org context)
- `role_permissions` - Role-permission mappings
- `sessions` - Active user sessions with tokens

#### Tenant Management
- `tenants` - Logical groupings within organizations
- `cloud_accounts` - Cloud provider accounts (AWS, Azure, GCP, Oracle, Akamai, Datacenter)

#### Configuration
- `persona_views` - Saved dashboards for different personas
- `audit_logs` - Comprehensive audit trail for all changes

#### Cost Management
- `budgets` - Budget definitions with alert thresholds
- `anomalies` - Cost anomaly detection and tracking

#### Workflow Automation
- `workflow_definitions` - Workflow templates and configurations
- `workflow_executions` - Execution history and status
- `workflow_steps` - Individual step execution details
- `workflow_external_refs` - Links to external systems (Jira, ServiceNow, etc.)

#### Integrations
- `integrations` - External system configurations
- `integration_deliveries` - Delivery attempts with retry logic

### Key Features

1. **Multi-Tenancy**: All tables properly scoped with `org_id`
2. **RBAC**: Comprehensive role-based access control
3. **Audit Trail**: All mutations tracked in `audit_logs`
4. **Soft Deletes**: `is_active` flags prevent data loss
5. **Timestamps**: `created_at` and `updated_at` on all tables
6. **Indexes**: Comprehensive indexing for query performance

## Commands

### Using Makefile

```bash
# Run all migrations (recommended)
make db-migrate

# Initialize database (alias for db-migrate)
make init-db

# Full bootstrap (start services + migrate + seed)
make bootstrap
make db-migrate
make seed-db
```

### Using Migration Script

```bash
# Upgrade to latest
./scripts/run_migrations.sh upgrade

# Upgrade to specific revision
./scripts/run_migrations.sh upgrade 003

# Downgrade one revision
./scripts/run_migrations.sh downgrade -1

# Show current revision
./scripts/run_migrations.sh current

# Show migration history
./scripts/run_migrations.sh history

# Show available heads
./scripts/run_migrations.sh heads

# Create new migration
./scripts/run_migrations.sh revision "add new feature"

# Stamp database (mark as migrated without running)
./scripts/run_migrations.sh stamp head

# Show help
./scripts/run_migrations.sh help
```

### Using Alembic Directly

```bash
cd data/db/alembic

# Upgrade
alembic upgrade head

# Downgrade
alembic downgrade -1

# Show current
alembic current

# Show history
alembic history --verbose

# Create new migration
alembic revision --autogenerate -m "description"
```

## Environment Configuration

### Setting Database URL

**Option 1: Environment Variable**
```bash
export DATABASE_URL="postgresql://user:pass@host:port/dbname"
make db-migrate
```

**Option 2: .env File**
```bash
# Add to .env file
DATABASE_URL=postgresql://finops:finops_dev_password@postgres:5432/finops

# Run migrations
make db-migrate
```

**Option 3: Alembic Config**
Edit `data/db/alembic/alembic.ini`:
```ini
sqlalchemy.url = postgresql://user:pass@host:port/dbname
```

### Default Values

If `DATABASE_URL` is not set:
- **Development**: `postgresql://finops:finops_dev@localhost:5432/finops`
- **Production**: Must be explicitly set

## Creating New Migrations

### Method 1: Auto-generate from Models

1. Update SQLAlchemy models in your service
2. Generate migration:
```bash
cd data/db/alembic
alembic revision --autogenerate -m "add user profile fields"
```
3. Review generated file in `versions/`
4. Edit if needed
5. Test migration

### Method 2: Manual Migration

1. Create migration file:
```bash
./scripts/run_migrations.sh revision "add new table"
```

2. Edit the generated file:
```python
def upgrade() -> None:
    op.create_table(
        'my_table',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        # ... more columns
    )
    op.create_index('idx_my_table_name', 'my_table', ['name'])

def downgrade() -> None:
    op.drop_table('my_table')
```

3. Test:
```bash
./scripts/run_migrations.sh upgrade
./scripts/run_migrations.sh downgrade -1
./scripts/run_migrations.sh upgrade
```

## Testing Migrations

### Local Testing

```bash
# 1. Start clean database
make clean-volumes
make dev-up

# 2. Run migrations
make db-migrate

# 3. Verify schema
psql -U finops -h localhost -d finops -c "\dt"

# 4. Verify current revision
./scripts/run_migrations.sh current

# 5. Test downgrade
./scripts/run_migrations.sh downgrade -1

# 6. Re-upgrade
./scripts/run_migrations.sh upgrade

# 7. Seed data
make seed-db
```

### Staging Testing

```bash
# 1. Backup staging database
pg_dump -U finops -h staging-db finops > staging_backup.sql

# 2. Run migrations
DATABASE_URL="postgresql://user:pass@staging-db/finops" make db-migrate

# 3. Verify
DATABASE_URL="postgresql://user:pass@staging-db/finops" ./scripts/run_migrations.sh current

# 4. Test application
# ... run tests ...

# 5. If issues, rollback
DATABASE_URL="postgresql://user:pass@staging-db/finops" ./scripts/run_migrations.sh downgrade -1
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] Backup production database
- [ ] Test migrations on staging with production-like data
- [ ] Review all SQL that will be executed
- [ ] Verify rollback strategy
- [ ] Schedule maintenance window if needed
- [ ] Notify stakeholders
- [ ] Prepare rollback scripts

### Deployment Steps

```bash
# 1. Backup production database
pg_dump -U finops -h prod-db finops > prod_backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Verify backup
pg_restore --list prod_backup_*.sql | head -20

# 3. Stop application (if needed)
# ... stop services ...

# 4. Run migrations
DATABASE_URL="postgresql://user:pass@prod-db/finops" make db-migrate

# 5. Verify migration
DATABASE_URL="postgresql://user:pass@prod-db/finops" ./scripts/run_migrations.sh current

# 6. Verify schema
psql -U finops -h prod-db -d finops -c "\d+ users"

# 7. Start application
# ... start services ...

# 8. Monitor logs
# ... check application logs ...

# 9. Verify functionality
# ... run smoke tests ...
```

### Rollback Procedure

If migration causes issues:

```bash
# Option 1: Rollback migration
DATABASE_URL="postgresql://user:pass@prod-db/finops" \
  ./scripts/run_migrations.sh downgrade -1

# Option 2: Restore from backup
psql -U finops -h prod-db -d finops < prod_backup_file.sql

# Option 3: Forward fix
# Create new migration to fix the issue
./scripts/run_migrations.sh revision "fix production issue"
# Edit migration, test, deploy
```

## Troubleshooting

### "relation already exists"

**Problem**: Database already has tables.

**Solution 1** (Development only):
```bash
# Drop all tables
psql -U finops -d finops -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run migrations
make db-migrate
```

**Solution 2** (Existing database):
```bash
# Stamp database at current state
./scripts/run_migrations.sh stamp head
```

### "can't import models"

**Problem**: Python can't find service models.

**Solution**:
1. Ensure you're running from project root
2. Check `sys.path` in `env.py`
3. Verify models exist in `services/*/src/models/`

### "database connection refused"

**Problem**: Can't connect to PostgreSQL.

**Solution**:
```bash
# Check if PostgreSQL is running
make ps

# Start PostgreSQL
make dev-up

# Verify connection
psql -U finops -h localhost -d finops -c "SELECT version();"

# Check DATABASE_URL
echo $DATABASE_URL
```

### "alembic command not found"

**Problem**: Alembic not installed.

**Solution**:
```bash
pip install alembic psycopg2-binary
```

## Integration with Docker

### Auto-migrate on Startup

**In Dockerfile:**
```dockerfile
CMD ["sh", "-c", "./scripts/run_migrations.sh && uvicorn main:app"]
```

**In docker-compose:**
```yaml
services:
  app:
    command: sh -c "./scripts/run_migrations.sh && uvicorn main:app"
    environment:
      - DATABASE_URL=postgresql://finops:finops_dev@postgres:5432/finops
    depends_on:
      postgres:
        condition: service_healthy
```

### Init Container (Kubernetes)

```yaml
initContainers:
  - name: migrate
    image: finops-app:latest
    command: ["./scripts/run_migrations.sh"]
    env:
      - name: DATABASE_URL
        valueFrom:
          secretKeyRef:
            name: database-secret
            key: url
```

## Best Practices

1. **Always backup before migrations** - Especially in production
2. **Test both upgrade and downgrade** - Ensure reversibility
3. **Review auto-generated migrations** - They may not be perfect
4. **Never edit applied migrations** - Create new ones instead
5. **Use transactions** - Migrations run in transactions by default
6. **Add comprehensive indexes** - Consider query patterns
7. **Document complex migrations** - Add comments
8. **Version control everything** - Commit migration files
9. **Test with production-like data** - On staging
10. **Have a rollback plan** - Always

## Performance Considerations

### Index Strategy

- Add indexes on foreign keys
- Add indexes on commonly queried columns
- Add composite indexes for common query patterns
- Consider partial indexes for filtered queries
- Monitor index usage and remove unused indexes

### Migration Size

- Keep migrations focused and atomic
- Split large migrations into smaller ones
- Run data migrations separately from schema migrations
- Consider downtime for large table alterations

### Locking

- Be aware of table locks during migrations
- Use `CONCURRENTLY` for index creation (when safe)
- Schedule migrations during low-traffic periods
- Consider online schema change tools for large tables

## Monitoring

### Check Migration Status

```bash
# Current revision
./scripts/run_migrations.sh current

# History
./scripts/run_migrations.sh history

# Pending migrations
alembic current
alembic heads
```

### Query Database Directly

```sql
-- Check alembic version
SELECT version_num FROM alembic_version;

-- Count tables
SELECT count(*) FROM information_schema.tables 
WHERE table_schema = 'public';

-- List all tables
\dt

-- Check specific table
\d+ users
```

## Support

For issues or questions:
1. Check this guide
2. Review migration logs
3. Check [Alembic documentation](https://alembic.sqlalchemy.org/)
4. Contact platform team

## Related Documentation

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Database Schema README](data/db/alembic/README.md)
- [Service Development Guide](docs/SERVICE_TEMPLATE.md)

## License

Copyright © 2026 FinOps SaaS Platform
