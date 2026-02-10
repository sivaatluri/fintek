# Contract Tests

This directory contains contract tests that validate sample JSON payloads against their corresponding JSON schemas. These tests ensure that:

1. All JSON schemas are valid and well-formed
2. Sample payloads conform to their schemas
3. Data contracts remain consistent across changes

## Structure

```
tests/contract-tests/
├── README.md                    # This file
├── package.json                 # Node.js dependencies
├── validate-contracts.js        # Main test runner
└── python/                      # Python-based tests (optional)
    └── validate_contracts.py
```

## Prerequisites

- Node.js 16+ (for JavaScript tests)
- Python 3.8+ (for Python tests, optional)

## Running Tests

### JavaScript/Node.js Tests

1. **Install dependencies**:
   ```bash
   cd tests/contract-tests
   npm install
   ```

2. **Run tests**:
   ```bash
   npm test
   ```

3. **Run with verbose output**:
   ```bash
   npm run test:verbose
   ```

### From Repository Root

You can also run tests from the repository root:

```bash
# Run contract tests
make test-contracts

# Or directly with npm
cd tests/contract-tests && npm install && npm test
```

## Test Cases

The test suite validates the following schemas and samples:

### 1. Raw Cost Schema
- **Schema**: `data/contracts/raw_cost.schema.json`
- **Samples**:
  - `raw_cost_aws.json` - AWS CUR data example

### 2. Normalized Cost Schema
- **Schema**: `data/contracts/normalized_cost.schema.json`
- **Samples**:
  - `normalized_cost_aws.json` - Normalized AWS cost data

### 3. Allocated Cost Schema
- **Schema**: `data/contracts/allocated_cost.schema.json`
- **Samples**:
  - `allocated_cost_example.json` - Cost allocation with unit economics

### 4. Recommendation Schema
- **Schema**: `data/contracts/recommendation.schema.json`
- **Samples**:
  - `recommendation_rightsizing.json` - EC2 rightsizing recommendation

### 5. Event Schema
- **Schema**: `data/contracts/event.schema.json`
- **Samples**:
  - `event_budget_exceeded.json` - Budget threshold exceeded event
  - `event_anomaly_spike.json` - Cost anomaly detection event
  - `event_waste_detected.json` - Idle resource detection event
  - `event_commitment_low_utilization.json` - RI/SP low utilization event

### 6. Workflow Execution Schema
- **Schema**: `data/contracts/workflow_execution.schema.json`
- **Samples**:
  - `workflow_execution_completed.json` - Completed workflow execution

### 7. Integration Delivery Schema
- **Schema**: `data/contracts/integration_delivery.schema.json`
- **Samples**:
  - `integration_delivery_slack.json` - Slack notification delivery

## Adding New Tests

To add tests for a new schema:

1. **Create the JSON schema** in `data/contracts/`
2. **Add sample payloads** in `data/contracts/samples/`
3. **Update test configuration** in `validate-contracts.js`:
   ```javascript
   const testCases = [
     // ... existing test cases ...
     {
       schema: 'your_new_schema.schema.json',
       samples: ['your_sample.json']
     }
   ];
   ```

## Validation Libraries

### JavaScript (AJV)

We use [AJV (Another JSON Schema Validator)](https://ajv.js.org/) which supports:
- JSON Schema Draft-07
- Format validation (date-time, email, uuid, etc.)
- Strict mode for catching errors
- Custom error messages

### Python (jsonschema)

Alternative Python-based validation using the `jsonschema` library:

```bash
pip install jsonschema
python python/validate_contracts.py
```

## Continuous Integration

Contract tests should run on every:
- Pull request
- Commit to main branch
- Before deployment

Add to your CI pipeline:

```yaml
# .github/workflows/contract-tests.yml
name: Contract Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Run contract tests
        run: |
          cd tests/contract-tests
          npm install
          npm test
```

## Troubleshooting

### Common Issues

1. **Module not found errors**:
   ```bash
   cd tests/contract-tests
   npm install
   ```

2. **Schema validation errors**:
   - Use `--verbose` flag to see detailed error messages
   - Check that sample JSON matches the schema requirements
   - Verify required fields are present

3. **Path issues**:
   - Ensure you're running tests from the correct directory
   - Check that schema and sample paths are correct

### Debugging Failed Tests

Run with verbose output to see detailed validation errors:

```bash
npm run test:verbose
```

This will show:
- Which field failed validation
- What the expected type/format was
- What value was provided

## Best Practices

1. **Keep samples realistic**: Use real-world-like data in samples
2. **Test edge cases**: Include samples that test boundary conditions
3. **Update tests with schemas**: When schemas change, update samples
4. **Run tests locally**: Always run tests before committing
5. **Document special cases**: Add comments for non-obvious test cases

## Related Documentation

- [Data Contracts README](../../data/contracts/README.md)
- [Schema Evolution Guide](../../docs/architecture/data_quality_lineage.md)
- [API Guidelines](../../docs/api/api_guidelines.md)
