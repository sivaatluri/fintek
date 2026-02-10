# Multi-Tenancy Architecture

## Overview

The FinOps SaaS platform implements a hierarchical multi-tenant architecture that provides secure data isolation while enabling efficient resource sharing.

## Tenant Hierarchy

```
Organization
  └── Tenant (Customer)
      └── Workspace (Environment/Team)
          └── Cloud Account (AWS Account, Azure Subscription, etc.)
```

### Levels

1. **Organization**: Top-level entity, typically a company
2. **Tenant**: A customer instance with dedicated configuration
3. **Workspace**: Logical grouping within a tenant (e.g., prod, dev, team-specific)
4. **Cloud Account**: Individual cloud provider accounts/subscriptions

## Data Isolation

### Database-Level Isolation

All data tables include `tenant_id` as a mandatory field:

```sql
CREATE TABLE costs (
  id UUID PRIMARY KEY,
  tenant_id VARCHAR(255) NOT NULL,
  provider VARCHAR(50) NOT NULL,
  account_id VARCHAR(255) NOT NULL,
  cost DECIMAL(18, 6) NOT NULL,
  usage_date DATE NOT NULL,
  -- ... other fields
  CONSTRAINT fk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- Row-level security
CREATE POLICY tenant_isolation ON costs
  FOR ALL
  USING (tenant_id = current_setting('app.current_tenant_id'));
```

### Query-Time Filtering

All queries automatically include tenant filtering:

```typescript
// Automatic tenant context injection
class CostRepository {
  async findByDate(date: Date): Promise<Cost[]> {
    const tenantId = this.context.getTenantId();
    return this.db.costs.findMany({
      where: {
        tenant_id: tenantId,  // Always included
        usage_date: date
      }
    });
  }
}
```

### Object Storage Isolation

Data lake uses tenant-prefixed paths:

```
s3://finops-data/
  tenant_id=abc123/
    provider=aws/
      year=2026/month=02/
        costs.parquet
  tenant_id=xyz789/
    provider=azure/
      year=2026/month=02/
        costs.parquet
```

## Authentication & Authorization

### Per-Tenant SSO Configuration

Each tenant can configure their own identity provider:

```typescript
interface TenantAuthConfig {
  tenant_id: string;
  sso_enabled: boolean;
  oidc_config?: {
    issuer: string;
    client_id: string;
    client_secret: string;
  };
  saml_config?: {
    entry_point: string;
    issuer: string;
    cert: string;
  };
}
```

### Role-Based Access Control (RBAC)

Roles are defined per tenant:

```typescript
interface Role {
  id: string;
  tenant_id: string;
  name: string;  // e.g., 'admin', 'finops-analyst', 'viewer'
  permissions: Permission[];
}

interface Permission {
  resource: string;  // e.g., 'budgets', 'costs', 'users'
  actions: string[];  // e.g., ['read', 'write', 'delete']
}
```

## Resource Limits & Quotas

### Per-Tenant Quotas

```typescript
interface TenantQuota {
  tenant_id: string;
  max_users: number;
  max_cloud_accounts: number;
  max_budgets: number;
  max_workflows: number;
  max_storage_gb: number;
  retention_days: number;
}
```

### Rate Limiting

Rate limits are applied per tenant:

```typescript
// Redis-based rate limiting
const rateLimiter = new RateLimiter({
  keyPrefix: 'ratelimit',
  points: 100,        // Number of requests
  duration: 60,       // Per 60 seconds
  blockDuration: 60   // Block for 60 seconds if exceeded
});

// Per tenant, per endpoint
const key = `${tenantId}:${endpoint}`;
await rateLimiter.consume(key);
```

## Configuration Isolation

### Per-Tenant Settings

Each tenant has isolated configuration:

```typescript
interface TenantSettings {
  tenant_id: string;
  currency: string;
  timezone: string;
  cost_allocation_enabled: boolean;
  virtual_tagging_rules: VirtualTagRule[];
  notification_preferences: NotificationPreferences;
  branding: {
    logo_url?: string;
    primary_color?: string;
  };
}
```

### Feature Flags

Features can be enabled/disabled per tenant:

```typescript
const canUseForecast = await featureFlags.isEnabled(
  'forecasting',
  tenantId
);

if (canUseForecast) {
  // Show forecast UI
}
```

## Data Processing

### Tenant-Specific Pipelines

Ingestion jobs are scheduled per tenant:

```typescript
// Cron job per tenant
tenants.forEach(tenant => {
  scheduleJob(`${tenant.id}-ingestion`, tenant.ingestion_schedule, async () => {
    await ingestCostData(tenant.id);
  });
});
```

### Resource Allocation

Processing resources are allocated per tenant tier:

```typescript
interface TenantTier {
  name: string;
  cpu_limit: string;      // e.g., '2000m'
  memory_limit: string;   // e.g., '4Gi'
  priority: number;       // 0-100
}

// Kubernetes pod with tenant-specific resources
const pod = {
  resources: {
    limits: {
      cpu: tenant.tier.cpu_limit,
      memory: tenant.tier.memory_limit
    }
  }
};
```

## Observability

### Tenant-Specific Metrics

All metrics are tagged with tenant_id:

```typescript
metrics.increment('api.requests', 1, {
  tenant_id: tenantId,
  endpoint: '/api/costs'
});

// Query in Prometheus
sum(rate(api_requests{tenant_id="abc123"}[5m]))
```

### Tenant-Specific Logs

Logs include tenant context:

```typescript
logger.info('Cost ingestion started', {
  tenant_id: tenantId,
  provider: 'aws',
  account_id: accountId
});
```

## Tenant Provisioning

### Onboarding Flow

```typescript
async function provisionTenant(config: TenantConfig): Promise<Tenant> {
  // 1. Create tenant record
  const tenant = await db.tenants.create({
    id: generateId(),
    organization_id: config.organization_id,
    name: config.name,
    slug: config.slug
  });

  // 2. Set up database schemas
  await db.raw(`
    CREATE SCHEMA IF NOT EXISTS tenant_${tenant.id};
  `);

  // 3. Initialize default settings
  await tenantSettings.create({
    tenant_id: tenant.id,
    currency: config.currency || 'USD',
    timezone: config.timezone || 'UTC'
  });

  // 4. Create default admin user
  await users.create({
    tenant_id: tenant.id,
    email: config.admin_email,
    role: 'admin'
  });

  // 5. Set up object storage paths
  await objectStorage.createBucket(`tenant-${tenant.id}`);

  return tenant;
}
```

## Security Considerations

### Preventing Cross-Tenant Access

1. **Request Context**: Every request carries tenant context
2. **Middleware**: Validates tenant_id in JWT token
3. **Database Policies**: Row-level security enforces isolation
4. **API Gateway**: Routes requests to tenant-specific endpoints
5. **Audit Logging**: All cross-tenant access attempts are logged

### Data Encryption

- **At Rest**: Tenant data encrypted with tenant-specific keys
- **In Transit**: TLS 1.3 for all communications
- **Key Management**: Tenant keys stored in secrets manager

## Tenant Migration

### Export Data

```bash
# Export tenant data
./scripts/export_tenant.sh --tenant-id abc123 --output /tmp/tenant-export/
```

### Import Data

```bash
# Import to new tenant
./scripts/import_tenant.sh --tenant-id xyz789 --input /tmp/tenant-export/
```

## Performance Optimization

### Tenant-Specific Caching

```typescript
// Cache key includes tenant_id
const cacheKey = `costs:${tenantId}:${date}`;
const cached = await redis.get(cacheKey);

if (cached) {
  return JSON.parse(cached);
}

const data = await fetchCosts(tenantId, date);
await redis.setex(cacheKey, 3600, JSON.stringify(data));
return data;
```

### Query Optimization

Indexes include tenant_id:

```sql
CREATE INDEX idx_costs_tenant_date 
  ON costs(tenant_id, usage_date);

CREATE INDEX idx_costs_tenant_provider 
  ON costs(tenant_id, provider, usage_date);
```

## Related Documentation

- [Authentication & Authorization](./auth_sso_rbac_abac.md)
- [Security & Compliance](./security_compliance.md)
