# Data Contracts

This directory contains the canonical data schemas (contracts) for the FinOps SaaS platform. These schemas define the structure and validation rules for all data exchanged between services, stored in databases, and transmitted via events.

## Overview

Data contracts ensure:
- **Consistency**: All services use the same data structures
- **Validation**: Data is validated against schemas before processing
- **Evolution**: Schemas can evolve with proper versioning
- **Documentation**: Schemas serve as living documentation
- **Interoperability**: Easy integration between services and external systems

## Schema Files

### 1. Raw Cost Schema (`raw_cost.schema.json`)

**Purpose**: Defines the structure of raw cloud billing data as ingested from various cloud providers before any normalization.

**Use Cases**:
- Ingestion from AWS CUR, Azure Cost Management, GCP Billing Export
- Data quality validation at ingestion time
- Audit trail of original billing data
- Reconciliation with provider bills

**Key Fields**:
- `record_id`: Unique identifier for deduplication
- `tenant_id`: Multi-tenant isolation
- `provider`: Cloud provider (aws, azure, gcp, oracle, akamai, datacenter)
- `raw_data`: Provider-specific billing data as key-value pairs
- `checksum`: For detecting duplicates

### 2. Normalized Cost Schema (`normalized_cost.schema.json`)

**Purpose**: Canonical cost schema after transformation to a provider-agnostic format.

**Use Cases**:
- Cross-cloud cost analysis and reporting
- Cost allocation and chargeback
- Trend analysis and forecasting
- Integration with BI tools

**Key Fields**:
- `cost_id`: Unique identifier for the normalized record
- `service_category`: Normalized categories (compute, storage, database, etc.)
- `usage_type` & `usage_amount`: Standardized usage metrics
- `tags` & `virtual_tags`: Native and platform-applied tags
- `data_quality`: Completeness scoring and quality flags

**Normalization Includes**:
- Region name standardization
- Service name mapping to common categories
- Usage unit conversion
- Currency standardization
- Tag key normalization

### 3. Allocated Cost Schema (`allocated_cost.schema.json`)

**Purpose**: Cost allocation with unit economics and chargeback/showback.

**Use Cases**:
- Departmental chargeback
- Project-level cost tracking
- Unit economics (cost per user, transaction, API call)
- Budget accountability

**Key Fields**:
- `allocation_method`: How costs are divided (direct, proportional, weighted, etc.)
- `allocation_targets`: Entities receiving cost allocations (business units, teams, projects)
- `unit_economics`: Cost per unit calculations
- `chargeback_info`: Billing cycle and invoice information

**Allocation Methods**:
- **Direct**: Costs directly attributed to a single entity
- **Proportional Usage**: Split based on resource usage
- **Proportional Cost**: Split based on existing cost ratios
- **Even Split**: Divided equally
- **Weighted**: Custom weighting factors
- **Custom**: User-defined allocation logic

### 4. Recommendation Schema (`recommendation.schema.json`)

**Purpose**: Cost optimization and savings recommendations.

**Use Cases**:
- Rightsizing compute resources
- Identifying idle resources
- Reserved instance/savings plan recommendations
- Storage optimization suggestions

**Key Fields**:
- `recommendation_type`: Type of optimization (rightsizing, idle_resource, etc.)
- `priority`: Based on savings potential and effort
- `estimated_monthly_savings`: Expected savings
- `confidence_level`: Confidence in the estimate
- `implementation_effort` & `implementation_risk`: Assessment metrics

**Recommendation Types**:
- Rightsizing: Adjust resource sizes
- Idle Resource: Terminate unused resources
- Reserved Instance: Purchase commitments
- Spot Instance: Use spot/preemptible instances
- Storage Optimization: Lifecycle policies, compression
- Architecture Optimization: Structural improvements

### 5. Event Schema (`event.schema.json`)

**Purpose**: Event envelope with typed payloads for budgets, anomalies, waste, and commitments.

**Use Cases**:
- Event-driven workflows and automation
- Real-time alerting
- Audit logging
- Event sourcing

**Structure**:
```json
{
  "event_id": "uuid",
  "event_type": "budget.threshold_exceeded",
  "tenant_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "source": {
    "service": "budgets-alerts-service",
    "instance": "pod-123"
  },
  "payload": {
    // Event-specific payload
  }
}
```

**Event Types**:

**Budget Events**:
- `budget.threshold_exceeded`: Budget limit reached
- `budget.threshold_warning`: Approaching budget limit
- `budget.forecast_exceeded`: Forecast exceeds budget

**Anomaly Events**:
- `anomaly.cost_spike`: Unusual cost increase
- `anomaly.usage_spike`: Unusual usage increase
- `anomaly.cost_drop`: Unusual cost decrease

**Waste Events**:
- `waste.idle_resource_detected`: Idle resource found
- `waste.underutilized_resource`: Low utilization detected
- `waste.zombie_resource`: Orphaned resource found

**Commitment Events**:
- `commitment.utilization_low`: Poor utilization of commitments
- `commitment.expiring_soon`: RI/SP expiring
- `commitment.renewal_recommended`: Renewal suggested
- `commitment.coverage_gap`: Gaps in commitment coverage

### 6. Workflow Execution Schema (`workflow_execution.schema.json`)

**Purpose**: Track workflow execution state and history.

**Use Cases**:
- Workflow automation tracking
- Debugging workflow failures
- Audit trail of automated actions
- Performance monitoring

**Key Fields**:
- `execution_id`: Unique execution identifier
- `workflow_id` & `workflow_version`: Which workflow was executed
- `status`: Current state (pending, running, completed, failed)
- `steps`: Execution history of each step
- `actions_taken`: Actions executed (emails, tickets, etc.)
- `idempotency_key`: Prevent duplicate executions

**Workflow Triggers**:
- Event-driven: Triggered by platform events
- Scheduled: Cron-like schedules
- Manual: User-initiated
- Webhook: External system triggers

### 7. Integration Delivery Schema (`integration_delivery.schema.json`)

**Purpose**: Track delivery of notifications and data to external integrations.

**Use Cases**:
- Notification delivery tracking
- Integration debugging
- Delivery retry management
- Audit trail of external communications

**Key Fields**:
- `integration_type`: Type (email, slack, jira, webhook, etc.)
- `status`: Delivery status (pending, delivered, failed)
- `payload`: What was sent (template + data)
- `response`: Response from external system
- `retry_count`: Retry attempts made

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

## Schema Validation

All schemas are JSON Schema Draft 7 compliant and include:
- Required field validation
- Type checking
- Format validation (date-time, email, uuid, etc.)
- Enum constraints
- Numeric ranges (min/max)
- Pattern matching (regex)
- Nested object validation

## Sample Data

Sample payloads demonstrating valid data for each schema are available in the `samples/` directory:
- `samples/raw_cost_*.json`
- `samples/normalized_cost_*.json`
- `samples/allocated_cost_*.json`
- `samples/recommendation_*.json`
- `samples/event_*.json`
- `samples/workflow_execution_*.json`
- `samples/integration_delivery_*.json`

## Contract Testing

Contract tests validate that sample data conforms to schemas. Tests are located in `tests/contract-tests/` and can be run with:

```bash
# Install dependencies
npm install

# Run contract tests
npm run test:contracts

# Or using Python
pip install jsonschema
python tests/contract-tests/validate_contracts.py
```

## Schema Evolution

When evolving schemas:

1. **Backward Compatible Changes** (safe):
   - Adding optional fields
   - Making required fields optional
   - Relaxing validation rules
   - Adding enum values

2. **Breaking Changes** (require version bump):
   - Removing fields
   - Renaming fields
   - Making optional fields required
   - Changing field types
   - Tightening validation rules

3. **Versioning**:
   - Use semantic versioning in `$id` field
   - Maintain old schema versions for transition periods
   - Document migration paths

## Best Practices

1. **Always Validate**: Validate data against schemas at service boundaries
2. **Use Types**: Generate types from schemas for TypeScript, Go, etc.
3. **Document Changes**: Update this README when schemas change
4. **Test Samples**: Ensure samples always validate against schemas
5. **Version Carefully**: Plan breaking changes with deprecation periods

## Tools

### Schema Validation Libraries

**JavaScript/TypeScript**:
```bash
npm install ajv ajv-formats
```

**Python**:
```bash
pip install jsonschema
```

**Go**:
```bash
go get github.com/xeipuuv/gojsonschema
```

### Type Generation

**TypeScript from JSON Schema**:
```bash
npm install -g json-schema-to-typescript
json-schema-to-typescript data/contracts/*.schema.json -o types/
```

**Go from JSON Schema**:
```bash
go install github.com/atombender/go-jsonschema@latest
go-jsonschema --package contracts data/contracts/*.schema.json
```

## Related Documentation

- [Architecture: Canonical Cost Schema](../../docs/architecture/canonical_cost_schema.md)
- [Architecture: Data Quality & Lineage](../../docs/architecture/data_quality_lineage.md)
- [Architecture: Budgets, Alerts & Workflows](../../docs/architecture/budgets_alerts_workflows.md)
- [API Guidelines](../../docs/api/api_guidelines.md)

## Support

For questions or issues with data contracts:
- Open an issue on GitHub
- Contact the platform team
- See [CONTRIBUTING.md](../../CONTRIBUTING.md)
