# Canonical Cost Schema

## Overview

The canonical cost schema is a normalized, provider-agnostic data model that enables consistent cost analysis across all cloud providers and on-premises infrastructure.

## Design Goals

1. **Consistency**: Same schema for all providers
2. **Completeness**: Captures all relevant cost dimensions
3. **Extensibility**: Easy to add new fields
4. **Query Performance**: Optimized for analytical queries

## Schema Versions

Current version: **v1.0**

Schema evolution follows semantic versioning:
- **Major**: Breaking changes to existing fields
- **Minor**: New optional fields added
- **Patch**: Documentation or metadata updates

## Core Fields

### Identity Fields

```typescript
interface CostIdentity {
  tenant_id: string;        // Multi-tenant isolation
  provider: CloudProvider;  // aws | azure | gcp | oracle | akamai | datacenter
  account_id: string;       // Provider account/subscription ID
  account_name: string;     // Human-readable account name
}
```

### Service Fields

```typescript
interface ServiceFields {
  service: string;          // Normalized service (compute, storage, network, etc.)
  service_native: string;   // Provider's service name (EC2, VirtualMachines, etc.)
  resource_type: string;    // Normalized resource type
  resource_id?: string;     // Unique resource identifier
  resource_name?: string;   // Resource name/description
}
```

### Location Fields

```typescript
interface LocationFields {
  region: string;           // Normalized region (us-east-1, eastus, us-central1)
  region_native: string;    // Provider's region name
  availability_zone?: string;
}
```

### Time Fields

```typescript
interface TimeFields {
  usage_date: Date;         // Date in YYYY-MM-DD format
  usage_start: DateTime;    // Start of usage period (ISO 8601)
  usage_end: DateTime;      // End of usage period (ISO 8601)
}
```

### Cost Fields

```typescript
interface CostFields {
  cost: number;             // Total cost (primary metric)
  cost_unblended: number;   // Before any discounts
  cost_amortized: number;   // Including amortized upfront fees
  currency: string;         // ISO 4217 code (USD, EUR, etc.)
}
```

### Usage Fields

```typescript
interface UsageFields {
  usage_type: string;       // Type of usage (BoxUsage, DataTransfer, etc.)
  usage_amount: number;     // Quantity used
  usage_unit: string;       // Unit (GB, Hours, Requests, etc.)
  pricing_unit: string;     // Pricing unit (per GB-Month, per Hour)
  pricing_rate: number;     // Rate per pricing unit
}
```

### Tag Fields

```typescript
interface TagFields {
  tags: Record<string, string>;           // Native tags from provider
  virtual_tags: Record<string, string>;   // Tags from virtual tagging rules
}
```

### Commitment Fields

```typescript
interface CommitmentFields {
  commitment_id?: string;
  commitment_type: 'reserved_instance' | 'savings_plan' | 
                  'committed_use_discount' | 'none';
}
```

### Charge Type Fields

```typescript
interface ChargeTypeFields {
  charge_type: 'usage' | 'purchase' | 'refund' | 
               'credit' | 'tax' | 'fee';
  invoice_id?: string;
}
```

## Complete Schema

```json
{
  "tenant_id": "abc123",
  "provider": "aws",
  "account_id": "123456789012",
  "account_name": "Production",
  "service": "compute",
  "service_native": "Amazon Elastic Compute Cloud",
  "resource_type": "instance",
  "resource_id": "i-1234567890abcdef0",
  "resource_name": "web-server-01",
  "region": "us-east-1",
  "region_native": "US East (N. Virginia)",
  "availability_zone": "us-east-1a",
  "usage_date": "2026-02-10",
  "usage_start": "2026-02-10T00:00:00Z",
  "usage_end": "2026-02-10T01:00:00Z",
  "usage_type": "BoxUsage:t3.medium",
  "usage_amount": 1.0,
  "usage_unit": "Hours",
  "cost": 0.0416,
  "cost_unblended": 0.0416,
  "cost_amortized": 0.0416,
  "currency": "USD",
  "pricing_unit": "per Hour",
  "pricing_rate": 0.0416,
  "tags": {
    "Environment": "production",
    "Team": "platform",
    "CostCenter": "engineering"
  },
  "virtual_tags": {
    "BusinessUnit": "core-platform",
    "Product": "web-app"
  },
  "commitment_type": "none",
  "charge_type": "usage",
  "invoice_id": "202602-123456",
  "metadata": {
    "ingestion_timestamp": "2026-02-10T02:00:00Z",
    "normalization_version": "v1.0",
    "source_file": "s3://cur-bucket/2026/02/10/cur-manifest.json"
  }
}
```

## Normalization Mappings

### Service Normalization

Provider-specific services are mapped to normalized categories:

| Normalized | AWS | Azure | GCP |
|------------|-----|-------|-----|
| compute | EC2, ECS, EKS, Lambda | Virtual Machines, AKS, Functions | Compute Engine, GKE, Cloud Functions |
| storage | S3, EBS, EFS | Blob Storage, Disk Storage | Cloud Storage, Persistent Disk |
| database | RDS, DynamoDB, Aurora | SQL Database, Cosmos DB | Cloud SQL, Firestore |
| network | VPC, CloudFront, Route53 | Virtual Network, CDN, DNS | VPC, Cloud CDN, Cloud DNS |
| analytics | Athena, EMR, Redshift | Synapse, HDInsight | BigQuery, Dataproc |

### Region Normalization

Regions are mapped to a consistent format:

| Normalized | AWS | Azure | GCP |
|------------|-----|-------|-----|
| us-east-1 | us-east-1 | eastus | us-east1 |
| us-west-2 | us-west-2 | westus2 | us-west1 |
| eu-west-1 | eu-west-1 | westeurope | europe-west1 |

## Usage Patterns

### Querying by Service

```sql
SELECT 
  service,
  SUM(cost) as total_cost
FROM costs
WHERE 
  tenant_id = 'abc123' AND
  usage_date >= '2026-02-01' AND
  usage_date < '2026-03-01'
GROUP BY service
ORDER BY total_cost DESC;
```

### Querying by Tags

```sql
SELECT 
  virtual_tags->>'BusinessUnit' as business_unit,
  SUM(cost) as total_cost
FROM costs
WHERE 
  tenant_id = 'abc123' AND
  usage_date >= '2026-02-01'
GROUP BY business_unit;
```

### Cross-Provider Analysis

```sql
SELECT 
  provider,
  service,
  SUM(cost) as total_cost
FROM costs
WHERE 
  tenant_id = 'abc123' AND
  usage_date >= '2026-02-01'
GROUP BY provider, service
ORDER BY total_cost DESC;
```

## Partitioning Strategy

Data is partitioned for optimal query performance:

```
costs/
  tenant_id=abc123/
    provider=aws/
      year=2026/
        month=02/
          day=10/
            part-00000.parquet
```

### Partition Pruning

Queries automatically prune partitions:

```sql
-- Only scans aws/2026/02/ partitions
SELECT * FROM costs 
WHERE 
  tenant_id = 'abc123' AND
  provider = 'aws' AND
  usage_date BETWEEN '2026-02-01' AND '2026-02-28';
```

## Schema Evolution

### Adding New Fields

New optional fields can be added without breaking existing queries:

```typescript
// v1.0 → v1.1: Add sustainability fields
interface SustainabilityFields {
  carbon_emissions_kg?: number;
  renewable_energy_percentage?: number;
}
```

### Deprecating Fields

Fields are deprecated but not removed:

```typescript
// Mark as deprecated
/**
 * @deprecated Use resource_id instead
 */
resource_arn?: string;
```

## Validation Rules

1. **Required Fields**: tenant_id, provider, account_id, service, usage_date, cost, currency
2. **Numeric Validation**: cost >= 0, usage_amount >= 0
3. **Date Validation**: usage_start <= usage_end
4. **Enum Validation**: provider must be valid enum value
5. **Currency Validation**: Must be valid ISO 4217 code

## Data Quality

### Completeness Checks

```sql
-- Check for missing required fields
SELECT COUNT(*) as missing_service
FROM costs
WHERE service IS NULL OR service = '';
```

### Consistency Checks

```sql
-- Check for cost/usage mismatches
SELECT COUNT(*) as inconsistent
FROM costs
WHERE usage_amount > 0 AND cost = 0;
```

## Related Documentation

- [Data Lake & Query](./data_lake_and_query.md)
- [Data Quality & Lineage](./data_quality_lineage.md)
- [Virtual Tagging & Normalization](./virtual_tagging_normalization.md)
