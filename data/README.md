# Data Schemas and Migrations

This directory contains database schemas and migration scripts.

## Structure

- `schemas/` - SQL schema definitions
- `migrations/` - Database migration scripts
- `seeds/` - Sample data for development

## Database Schema

### Core Tables

- `tenants` - Tenant information
- `users` - User accounts
- `cost_records` - Cost data records
- `budgets` - Budget definitions
- `alerts` - Alert configurations
- `integrations` - Cloud provider integrations
- `workflows` - Workflow definitions

## Migrations

We use Alembic for database migrations:

```bash
# Create a new migration
alembic revision -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Sample Data

Sample data for local development:

```sql
-- Insert sample tenant
INSERT INTO tenants (id, name, slug, status) 
VALUES ('tenant-1', 'Demo Tenant', 'demo', 'active');

-- Insert sample user
INSERT INTO users (id, tenant_id, email, name) 
VALUES ('user-1', 'tenant-1', 'admin@demo.com', 'Admin User');
```

## Future Work

- Alembic migration setup
- Complete schema definitions
- Seed data scripts
- Data archival strategy
