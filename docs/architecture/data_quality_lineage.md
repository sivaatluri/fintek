# Data Quality & Lineage

## Overview

The FinOps SaaS platform implements comprehensive data quality monitoring and lineage tracking to ensure accurate cost data and enable trust in financial reporting.

## Data Quality Framework

### Quality Dimensions

1. **Completeness**: Are all expected fields present?
2. **Accuracy**: Does the data match the source?
3. **Consistency**: Is data consistent across systems?
4. **Timeliness**: Is data fresh and up-to-date?
5. **Validity**: Does data conform to schemas?
6. **Uniqueness**: Are there duplicates?

### Completeness Scoring

Each normalized cost record includes a completeness score (0.0 - 1.0):

```json
{
  "data_quality": {
    "completeness_score": 0.98,
    "quality_flags": []
  }
}
```

**Calculation**:
```
completeness_score = (fields_present / fields_expected)
```

**Thresholds**:
- **Excellent** (≥0.95): All critical fields present
- **Good** (0.85-0.94): Minor fields missing
- **Fair** (0.70-0.84): Some important fields missing
- **Poor** (<0.70): Significant quality issues

### Quality Flags

Records automatically flagged for common issues:

**Critical Flags**:
- `missing_resource_id`: No resource identifier
- `missing_account_id`: No account/subscription ID
- `invalid_currency`: Currency code invalid
- `negative_cost_unexpected`: Unexpected negative cost
- `future_timestamp`: Timestamp in the future

**Warning Flags**:
- `missing_tags`: No tags present
- `missing_region`: Region not specified
- `zero_usage_with_cost`: Cost without usage
- `usage_without_cost`: Usage without cost
- `duplicate_suspected`: Potential duplicate record
- `outlier_detected`: Value outside normal range

### Quality Checks

**Ingestion-Time Checks**:
1. Schema validation (JSON Schema)
2. Required field presence
3. Data type validation
4. Format validation (dates, UUIDs, etc.)
5. Enum value validation
6. Numeric range validation

**Post-Processing Checks**:
1. Cross-field validation
2. Business rule validation
3. Duplicate detection
4. Outlier detection
5. Consistency checks
6. Reconciliation with source

## Data Lineage

### Lineage Tracking

Every piece of data maintains lineage through the pipeline:

```
Raw Cost Record
    ↓ (raw_record_id)
Normalized Cost Record
    ↓ (cost_id)
Allocated Cost Record
    ↓ (allocation_id)
Analytics/Reports
```

**Lineage Fields**:
```json
{
  "normalized_cost": {
    "cost_id": "uuid",
    "raw_record_id": "uuid",  // Link to raw data
    "normalized_at": "timestamp"
  },
  "allocated_cost": {
    "allocation_id": "uuid",
    "cost_id": "uuid",  // Link to normalized data
    "allocated_at": "timestamp"
  }
}
```

### Transformation Tracking

Each transformation stage records:
- Source record ID
- Transformation timestamp
- Transformation rules applied
- Service version that performed transformation
- Quality scores before and after

### Audit Trail

Complete audit trail for compliance:
```json
{
  "audit_metadata": {
    "ingested_at": "2024-02-01T08:30:00Z",
    "ingested_by": "cost-ingestion-service:v1.2.3",
    "normalized_at": "2024-02-01T08:35:00Z",
    "normalized_by": "cost-normalization-service:v2.1.0",
    "allocated_at": "2024-02-01T09:00:00Z",
    "allocated_by": "allocation-service:v1.5.0"
  }
}
```

## Reconciliation

### Provider Reconciliation

Periodic reconciliation with cloud provider bills:

1. **Daily Reconciliation**: Compare ingested data with source
2. **Monthly Reconciliation**: Match with provider invoices
3. **Variance Analysis**: Identify and explain differences

**Reconciliation Metrics**:
- Total cost variance (%)
- Record count variance
- Missing records
- Duplicate records
- Late-arriving data

### Internal Reconciliation

Consistency checks within the platform:

1. **Pipeline Reconciliation**: Raw → Normalized → Allocated
2. **Aggregation Reconciliation**: Detail ↔ Summary
3. **Report Reconciliation**: Reports ↔ Source data

## Data Quality Monitoring

### Real-Time Monitoring

Dashboard showing:
- Ingestion rate (records/minute)
- Quality score distribution
- Error rates by check type
- Data freshness (lag time)
- Completeness by provider

### Alerting

Alerts triggered for:
- Quality score drops below threshold
- Error rate exceeds threshold
- Data lag exceeds SLA
- Reconciliation variance > tolerance
- Critical quality flags

### Quality Reports

**Daily Reports**:
- Records ingested
- Average quality score
- Top quality issues
- Provider-specific issues

**Monthly Reports**:
- Quality trends
- Reconciliation summary
- Improvement recommendations
- SLA compliance

## Contract Testing

### Schema Validation Tests

All data validated against JSON schemas:

```bash
cd tests/contract-tests
npm install
npm test
```

**Test Coverage**:
- 7 core schemas
- 10+ sample payloads
- Automated validation
- CI/CD integration

### Contract Test Results

```
✓ raw_cost_aws.json validates against raw_cost.schema.json
✓ normalized_cost_aws.json validates against normalized_cost.schema.json
✓ allocated_cost_example.json validates against allocated_cost.schema.json
✓ recommendation_rightsizing.json validates against recommendation.schema.json
✓ event_budget_exceeded.json validates against event.schema.json
✓ event_anomaly_spike.json validates against event.schema.json
✓ event_waste_detected.json validates against event.schema.json
✓ event_commitment_low_utilization.json validates against event.schema.json
✓ workflow_execution_completed.json validates against workflow_execution.schema.json
✓ integration_delivery_slack.json validates against integration_delivery.schema.json

All contract tests passed! ✓
```

## Data Retention

### Retention Policies

**Raw Cost Data**: 13 months (1 year + 1 month overlap)
- Required for reconciliation
- Archived to cold storage after 3 months

**Normalized Cost Data**: 7 years
- Financial reporting requirements
- Partitioned by month
- Compressed after 1 year

**Allocated Cost Data**: 7 years
- Chargeback/showback history
- Audit requirements

**Events**: 1 year
- Operational history
- Debugging and analysis

**Workflow Executions**: 90 days
- Audit trail
- Troubleshooting

## Performance & Scale

### Optimization Strategies

1. **Partitioning**: Partition tables by date (monthly)
2. **Indexing**: Strategic indexes on query patterns
3. **Compression**: Compress old data
4. **Archival**: Move old data to cold storage
5. **Caching**: Cache aggregated results

### Expected Scale

- **Ingestion**: 100M+ records/day
- **Storage**: PB-scale cost data
- **Query**: Sub-second for common queries
- **Retention**: 7 years of normalized data

## Related Documentation

- [Canonical Cost Schema](./canonical_cost_schema.md) - Schema details
- [Data Contracts README](../../data/contracts/README.md) - Schema reference
- [Contract Tests](../../tests/contract-tests/README.md) - Testing guide
