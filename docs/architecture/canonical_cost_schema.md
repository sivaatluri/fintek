# Canonical Cost Schema & Data Contracts

## Overview

The FinOps SaaS platform uses a canonical cost schema to normalize billing data from multiple cloud providers into a unified format. This document describes the data contracts that govern how cost data flows through the system.

## Architecture Principles

### 1. Provider Agnostic
All data is transformed into a provider-neutral schema, enabling:
- Cross-cloud cost analysis
- Unified reporting and dashboards
- Consistent APIs regardless of cloud provider
- Easy addition of new cloud providers

### 2. Immutable Data Pipeline
```
Raw Data → Normalized Data → Allocated Data → Analytics
   ↓            ↓               ↓
Preserved   Transformed    Enhanced
```

Each stage preserves the previous stage's data for audit trails and reconciliation.

### 3. Schema-First Design
- All data structures defined as JSON Schema (Draft-07)
- Automated validation at service boundaries
- Contract tests ensure schema compliance
- Type generation for TypeScript, Go, Python

## Data Contract Layers

### Layer 1: Raw Cost Data

**Schema**: `raw_cost.schema.json`

Raw billing data ingested from cloud providers before any transformation. This layer preserves the original provider format for:
- Reconciliation with provider bills
- Audit trails
- Data quality validation
- Regulatory compliance

**Key Fields**:
```json
{
  "record_id": "uuid",
  "tenant_id": "uuid",
  "provider": "aws|azure|gcp|oracle|akamai|datacenter",
  "raw_data": {
    // Provider-specific fields as key-value pairs
  },
  "checksum": "hash for deduplication"
}
```

**Connectors**:
- AWS: CUR (Cost and Usage Report), Cost Explorer API
- Azure: Cost Management API, Usage Details API
- GCP: BigQuery Billing Export
- Oracle: Usage2 API
- Akamai: Billing API
- Datacenter: CSV/CMDB exports

### Layer 2: Normalized Cost Data

**Schema**: `normalized_cost.schema.json`

Canonical schema after transformation. All provider-specific concepts mapped to common categories.

**Normalization Includes**:

1. **Service Categories** (standardized):
   - compute, storage, database, networking, analytics, ml_ai, security, management, other

2. **Region Normalization**:
   - AWS: `us-east-1` → `us-east-1`
   - Azure: `eastus` → `us-east-1`
   - GCP: `us-east1` → `us-east-1`

3. **Usage Types** (standardized):
   - `compute-hours`, `data-transfer-gb`, `storage-gb-month`, `api-requests`

4. **Pricing Models**:
   - on_demand, reserved, spot, savings_plan, committed_use, custom

5. **Tagging**:
   - Native tags preserved
   - Virtual tags added by platform
   - Tag key normalization (CamelCase → lowercase)

**Key Fields**:
```json
{
  "cost_id": "uuid",
  "tenant_id": "uuid",
  "provider": "aws",
  "service_category": "compute",
  "service_name": "Virtual Machines",
  "usage_type": "compute-hours",
  "usage_amount": 1.0,
  "cost": 0.0416,
  "currency": "USD",
  "tags": {},
  "virtual_tags": {},
  "data_quality": {
    "completeness_score": 0.98
  }
}
```

### Layer 3: Allocated Cost Data

**Schema**: `allocated_cost.schema.json`

Cost allocation with unit economics and chargeback/showback.

**Allocation Methods**:
1. **Direct**: 100% to one entity
2. **Proportional Usage**: Based on resource usage metrics
3. **Proportional Cost**: Based on existing cost ratios
4. **Even Split**: Divided equally
5. **Weighted**: Custom weighting factors
6. **Custom**: User-defined allocation logic

**Unit Economics**:
- Cost per user
- Cost per transaction
- Cost per API call
- Cost per customer
- Custom unit definitions

**Key Fields**:
```json
{
  "allocation_id": "uuid",
  "cost_id": "uuid (reference to normalized cost)",
  "allocation_method": "proportional_usage",
  "allocation_targets": [
    {
      "target_type": "team|project|product|customer",
      "target_id": "uuid",
      "allocation_percentage": 60.0,
      "allocated_amount": 100.00
    }
  ],
  "unit_economics": {
    "unit_type": "api_request",
    "unit_count": 1000000,
    "cost_per_unit": 0.0001
  },
  "chargeback_info": {
    "mode": "chargeback|showback",
    "status": "approved"
  }
}
```

## Event-Driven Architecture

### Event Schema

**Schema**: `event.schema.json`

All platform events follow a consistent envelope with typed payloads.

**Event Types**:

**Budget Events**:
- `budget.threshold_exceeded` - Budget limit reached
- `budget.threshold_warning` - Approaching limit (e.g., 80%)
- `budget.forecast_exceeded` - Forecast exceeds budget

**Anomaly Events**:
- `anomaly.cost_spike` - Unusual cost increase detected
- `anomaly.usage_spike` - Unusual usage increase
- `anomaly.cost_drop` - Unusual cost decrease

**Waste Events**:
- `waste.idle_resource_detected` - Resource with no activity
- `waste.underutilized_resource` - Low utilization (< threshold)
- `waste.zombie_resource` - Orphaned resource

**Commitment Events**:
- `commitment.utilization_low` - Poor RI/SP utilization
- `commitment.expiring_soon` - Commitment ending
- `commitment.renewal_recommended` - Should renew
- `commitment.coverage_gap` - Not enough coverage

**Event Structure**:
```json
{
  "event_id": "uuid",
  "event_type": "budget.threshold_exceeded",
  "event_version": "1.0.0",
  "tenant_id": "uuid",
  "timestamp": "ISO-8601",
  "source": {
    "service": "budgets-alerts-service",
    "instance": "pod-123"
  },
  "payload": {
    // Event-specific payload (validated via oneOf)
  }
}
```

## Workflow & Integration Tracking

### Workflow Execution Schema

**Schema**: `workflow_execution.schema.json`

Tracks workflow execution from trigger to completion.

**Workflow States**:
- pending → running → completed
- pending → running → failed
- pending → running → paused → running → completed
- pending → cancelled

**Key Features**:
- Step-by-step execution history
- Retry tracking
- Idempotency keys
- Cooldown periods
- Parent-child workflow relationships

### Integration Delivery Schema

**Schema**: `integration_delivery.schema.json`

Tracks delivery of notifications and data to external systems.

**Supported Integrations**:
- Email (SMTP)
- Slack
- Microsoft Teams
- Jira
- ServiceNow
- Zendesk
- PagerDuty
- Generic Webhooks
- Custom APIs

**Delivery States**:
- pending → queued → sending → delivered
- pending → failed → retrying → delivered
- pending → cancelled

## Recommendation Schema

**Schema**: `recommendation.schema.json`

Cost optimization recommendations with actionable insights.

**Recommendation Types**:
1. **Rightsizing**: Adjust resource sizes (up or down)
2. **Idle Resources**: Terminate unused resources
3. **Reserved Instances**: Purchase commitments
4. **Savings Plans**: Flexible commitments
5. **Spot Instances**: Use preemptible instances
6. **Storage Optimization**: Lifecycle policies, tiering
7. **Data Transfer**: Optimize cross-region transfer
8. **Commitment Utilization**: Improve RI/SP usage
9. **Architecture**: Structural improvements
10. **License Optimization**: Right-size licenses

**Assessment Metrics**:
- Estimated monthly/annual savings
- Confidence level (very_high, high, medium, low)
- Implementation effort (very_low → very_high)
- Implementation risk (very_low → very_high)
- Priority (critical, high, medium, low)

## Data Validation

### Schema Validation

All data validated at service boundaries using JSON Schema validators:

**JavaScript/TypeScript**:
```javascript
import Ajv from 'ajv';
import addFormats from 'ajv-formats';

const ajv = new Ajv({ strict: true });
addFormats(ajv);

const validate = ajv.compile(schema);
const valid = validate(data);
```

**Python**:
```python
import jsonschema

jsonschema.validate(instance=data, schema=schema)
```

**Go**:
```go
import "github.com/xeipuuv/gojsonschema"

schemaLoader := gojsonschema.NewReferenceLoader("file://schema.json")
documentLoader := gojsonschema.NewGoLoader(data)
result, _ := gojsonschema.Validate(schemaLoader, documentLoader)
```

### Contract Testing

Automated tests validate:
1. Schema correctness (valid JSON Schema)
2. Sample data compliance (samples validate against schemas)
3. Schema evolution (backward compatibility checks)

**Running Tests**:
```bash
cd tests/contract-tests
npm install
npm test
```

## Schema Evolution

### Versioning Strategy

Schemas use semantic versioning in the `$id` field:

```json
{
  "$id": "https://finops.example.com/schemas/cost.schema.json#v1.2.3",
  ...
}
```

**Version Bumps**:
- **Patch (1.2.3 → 1.2.4)**: Documentation fixes, clarifications
- **Minor (1.2.0 → 1.3.0)**: Backward-compatible additions
- **Major (1.0.0 → 2.0.0)**: Breaking changes

### Backward Compatible Changes

Safe changes that don't break existing consumers:
- Adding optional fields
- Making required fields optional
- Relaxing validation rules (e.g., removing pattern constraints)
- Adding enum values
- Widening numeric ranges

### Breaking Changes

Changes requiring version bump and migration period:
- Removing fields
- Renaming fields
- Making optional fields required
- Changing field types
- Tightening validation rules
- Removing enum values
- Narrowing numeric ranges

### Migration Process

1. **Announce**: Document breaking changes 30 days in advance
2. **Dual Support**: Support both old and new schemas
3. **Deprecation**: Mark old schema as deprecated
4. **Migration Tools**: Provide data transformation scripts
5. **Sunset**: Remove old schema after transition period

## Data Quality

### Completeness Score

Each normalized cost record includes a completeness score (0.0 - 1.0):

```
completeness = (fields_present / fields_expected)
```

**Scoring**:
- 1.0: All expected fields present
- 0.9-0.99: Minor fields missing
- 0.7-0.89: Some important fields missing
- < 0.7: Significant data quality issues

### Quality Flags

Records flagged for quality issues:
- `missing_resource_id`: No resource identifier
- `missing_tags`: No tags present
- `negative_cost`: Unexpected negative cost
- `zero_usage_with_cost`: Cost without usage
- `usage_without_cost`: Usage without cost
- `future_timestamp`: Timestamp in the future
- `duplicate_suspected`: Potential duplicate

## Performance Considerations

### Schema Size

Keep schemas focused and modular:
- Avoid deeply nested structures (max 5 levels)
- Use `$ref` for shared definitions
- Split large schemas into multiple files

### Validation Performance

**Optimization Strategies**:
1. Compile schemas once, reuse validators
2. Use schema caching
3. Validate at boundaries only (not internal processing)
4. Batch validation for bulk operations
5. Use strict mode to catch errors early

### Storage Optimization

**Normalized Cost Table**:
- Partition by date (monthly or daily)
- Index on: tenant_id, provider, service_category, usage_date
- Compress old partitions
- Archive data older than retention period

## Related Documentation

- [Data Contracts README](../../data/contracts/README.md) - Schema reference
- [Contract Tests](../../tests/contract-tests/README.md) - Testing guide
- [Data Quality & Lineage](./data_quality_lineage.md) - Quality framework
- [Virtual Tagging](./virtual_tagging_normalization.md) - Tag enrichment
- [Cost Allocation](./cost_allocation_unit_economics.md) - Allocation strategies
