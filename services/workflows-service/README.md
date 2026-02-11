# Workflows Service

Event-driven workflow automation service for the FinOps SaaS platform. Consumes events from Kafka, matches them to workflow definitions, and executes automated actions through the integrations service.

## Features

### Core Capabilities

- **Event-Driven Automation** - Consumes events from Kafka topics defined by `data/contracts/event.schema.json`
- **State Machine** - Robust execution state management with 8 states
- **Deduplication** - SHA256-based deduplication with configurable cooldown windows
- **Condition Evaluation** - Complex rule matching with AND/OR logic
- **Escalation Rules** - Time and retry-based escalation
- **Integration Actions** - Jira, ServiceNow, Slack, Email, Webhook support
- **Template Rendering** - Jinja2 templates for all integrations
- **Dry-Run API** - Test workflows without execution

### Workflow States

The state machine supports 8 execution states:

1. **RECEIVED** - Event received from Kafka
2. **MATCHED** - Event matched to workflow definition(s)
3. **DEDUPED** - Execution skipped due to deduplication
4. **RUNNING** - Currently executing actions
5. **WAITING** - Waiting for external response or delay
6. **RETRYING** - Retrying after failure
7. **SUCCEEDED** - Completed successfully
8. **FAILED** - Failed permanently

### Deduplication

Dedupe keys are generated using SHA256 hash of:
- Organization ID
- Event type
- Scope fields (configurable)
- Period
- Threshold value
- Workflow version

This prevents duplicate workflow executions within the cooldown window.

## Architecture

```
Events (Kafka) → Dispatcher → State Machine → Executor → Integrations Service
                      ↓
                 Evaluator
                      ↓
                 Idempotency
                      ↓
                 Escalation
```

### Components

**Engine:**
- `state_machine.py` - State transition management
- `idempotency.py` - Deduplication and cooldown logic
- `dispatcher.py` - Event matching and workflow dispatch
- `evaluator.py` - Condition evaluation
- `context_builder.py` - Execution context construction
- `escalation.py` - Escalation rule processing
- `scheduler.py` - Delayed action scheduling

**Core:**
- `executor.py` - Workflow action execution
- `main.py` - FastAPI application and Kafka consumer
- `database.py` - Async database connection

**Models:**
- `WorkflowDefinition` - Workflow configuration
- `WorkflowExecution` - Execution tracking
- `WorkflowStep` - Individual action tracking
- `WorkflowExternalRef` - External system references

## API Endpoints

### Workflow Testing

**POST /api/v1/workflows/dry-run**

Test workflow execution without actually running actions.

```bash
curl -X POST http://localhost:8010/api/v1/workflows/dry-run \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-123" \
  -d '{
    "event": {
      "event_type": "budget.threshold_exceeded",
      "payload": {...}
    }
  }'
```

Response:
```json
{
  "matched_workflows": 2,
  "would_execute": true,
  "deduplicated": false,
  "dedup_reasons": [],
  "executions": [...]
}
```

### Workflow Management

**POST /api/v1/workflows/definitions**

Create a new workflow definition.

```bash
curl -X POST http://localhost:8010/api/v1/workflows/definitions \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-123" \
  -d '{
    "name": "Budget Alert Workflow",
    "trigger_type": "event",
    "trigger_config": {
      "event_types": ["budget.threshold_exceeded"]
    },
    "conditions": {
      "logic": "and",
      "rules": [
        {
          "field": "payload.threshold_percentage",
          "operator": "gte",
          "value": 80
        }
      ]
    },
    "actions": [
      {
        "name": "Create Jira Issue",
        "type": "jira",
        "template": "budget_exceeded",
        "integration": "jira-prod"
      }
    ],
    "dedupe_config": {
      "scope_fields": ["budget_id"],
      "cooldown_minutes": 60
    },
    "escalation_rules": {
      "rules": [
        {
          "name": "Escalate to manager",
          "trigger_type": "duration",
          "duration_minutes": 120,
          "actions": [
            {
              "type": "email",
              "to": "manager@example.com"
            }
          ]
        }
      ]
    }
  }'
```

**GET /api/v1/workflows/definitions**

List all workflow definitions for organization.

**GET /api/v1/workflows/executions**

List workflow executions.

**GET /api/v1/workflows/executions/{id}**

Get detailed execution information.

## Templates

### Available Templates

**Jira:**
- `templates/jira/budget_exceeded.j2`
- `templates/jira/anomaly_spike.j2`

**ServiceNow:**
- `templates/servicenow/budget_exceeded.j2`
- `templates/servicenow/anomaly_spike.j2`

**Slack:**
- `templates/slack/budget_exceeded.j2`
- `templates/slack/anomaly_spike.j2`

**Email:**
- `templates/email/budget_exceeded.j2`
- `templates/email/anomaly_spike.j2`

### Template Context

Templates have access to:
- `event` - The full event object
- `event_type` - Event type string
- `payload` - Event payload
- `org_id` - Organization ID
- `routing` - Routing metadata (severity, priority, assignee, labels)

Example template:
```jinja2
**Budget Alert**: {{ event.payload.budget_name }}

*Current Spend:* ${{ "%.2f"|format(event.payload.current_spend) }}
*Budget:* ${{ "%.2f"|format(event.payload.budget_amount) }}
*Threshold:* {{ event.payload.threshold_percentage }}%

*Event ID:* {{ event.event_id }}
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/finops

# Integrations Service
INTEGRATIONS_SERVICE_URL=http://integrations-service:8011

# Kafka (optional - for production)
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_CONSUMER_GROUP=workflows-service
KAFKA_TOPIC=finops-events
```

### Workflow Definition

```json
{
  "name": "Workflow Name",
  "trigger_type": "event|schedule|manual",
  "trigger_config": {
    "event_types": ["budget.threshold_exceeded", "anomaly.cost_spike"]
  },
  "conditions": {
    "logic": "and|or",
    "rules": [
      {
        "field": "payload.severity",
        "operator": "eq|ne|gt|gte|lt|lte|in|contains",
        "value": "high"
      }
    ]
  },
  "actions": [
    {
      "name": "Action Name",
      "type": "jira|servicenow|slack|email|webhook",
      "template": "template_name",
      "integration": "integration_name",
      "required": true,
      "delay_minutes": 0
    }
  ],
  "dedupe_config": {
    "scope_fields": ["budget_id", "resource_id"],
    "period": "hourly|daily|weekly|monthly",
    "cooldown_minutes": 60
  },
  "escalation_rules": {
    "rules": [
      {
        "name": "Escalation Name",
        "trigger_type": "duration|retry",
        "duration_minutes": 120,
        "retry_count": 3,
        "actions": [...]
      }
    ]
  }
}
```

## Development

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start service
uvicorn src.main:app --reload --port 8010
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_state_machine.py -v
```

### Adding New Templates

1. Create template file in `templates/{integration_type}/{template_name}.j2`
2. Use Jinja2 syntax with available context variables
3. Reference in workflow action: `"template": "template_name"`

## Event Processing Flow

1. **Event Received** - Kafka consumer receives event, creates execution with RECEIVED status
2. **Matching** - Dispatcher finds workflows matching event type and conditions
3. **Deduplication** - Idempotency checker generates dedupe key and checks cooldown
4. **Status Transition** - RECEIVED → MATCHED (or DEDUPED if duplicate)
5. **Execution Start** - MATCHED → RUNNING, executor begins processing actions
6. **Action Execution** - Each action creates a WorkflowStep and calls integrations-service
7. **External References** - Jira keys, ServiceNow tickets stored in WorkflowExternalRef
8. **Completion** - RUNNING → SUCCEEDED (or FAILED if errors)
9. **Escalation** - If configured, escalation rules trigger additional actions

## Integration with Other Services

### Integrations Service

Workflows service calls integrations-service to execute actions:

```python
POST http://integrations-service:8011/api/v1/deliveries
{
  "integration_id": "jira-prod",
  "payload": {...},
  "workflow_execution_id": "exec-123",
  "workflow_step_id": "step-456"
}
```

### Budgets/Alerts Service

Events are consumed from Kafka topics populated by:
- budgets-alerts-service
- recommendations-service
- Other event producers

## Monitoring

### Health Checks

```bash
# Health check
curl http://localhost:8010/health

# Readiness check
curl http://localhost:8010/ready
```

### Metrics

Monitor execution states:
```sql
SELECT status, COUNT(*) 
FROM workflow_executions 
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY status;
```

## Troubleshooting

### Workflow Not Triggering

1. Check workflow is active: `is_active = true`
2. Verify event type matches trigger_config
3. Test conditions with dry-run API
4. Check deduplication - may be in cooldown period

### Actions Failing

1. Check integrations-service connectivity
2. Verify integration exists and is active
3. Review template rendering errors in logs
4. Check WorkflowStep error_message field

### Duplicate Executions

1. Review dedupe_config settings
2. Verify cooldown_minutes is appropriate
3. Check scope_fields include unique identifiers
4. Consider increasing cooldown period

## Production Deployment

### Kafka Consumer

In production, uncomment the Kafka consumer in `main.py`:

```python
async def startup_event():
    # Start Kafka consumer
    asyncio.create_task(process_kafka_events())
```

Configure Kafka connection:
```bash
KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092,kafka3:9092
KAFKA_CONSUMER_GROUP=workflows-service
```

### Scaling

- Run multiple instances with same consumer group for load balancing
- Each instance processes subset of Kafka partitions
- Database handles execution locking via dedupe keys

### Monitoring

- Track execution counts by status
- Monitor escalation trigger frequency
- Alert on FAILED executions
- Track integration delivery success rates

## License

Copyright © 2024 FinOps SaaS Platform
