# Budgets-Alerts Service

Production-ready budget monitoring and alerting service with intelligent detectors and Kafka event emission.

## Features

### Budget Management
- **Full CRUD Operations** - Create, read, update, delete budgets with org enforcement
- **Multi-Period Support** - Monthly, quarterly, yearly, or custom periods
- **Flexible Filters** - Apply budgets to specific cloud providers, services, tags
- **Configurable Thresholds** - Default 50%, 80%, 90%, 100% or custom
- **Current Spend Tracking** - Real-time budget utilization monitoring

### Intelligent Detectors

#### 1. Budget Threshold Detector
Monitors actual spend against budget thresholds.

**Features:**
- Configurable thresholds (default: 50%, 80%, 90%, 100%)
- State tracking prevents duplicate alerts
- Severity based on threshold (50%=low, 80%=medium, 90%=high, 100%=critical)
- Calculates actual vs budget percentage

**Example:**
```
Budget 'Production' has reached 90% (92.5% of $10,000).
Current spend: $9,250
```

#### 2. Forecast Detector
Predicts if spend will exceed budget using linear regression.

**Features:**
- Linear regression forecasting
- Projects spend to end of period
- Requires minimum 7 days of data
- Confidence scoring based on R² value
- Severity based on projected overage

**Example:**
```
Budget 'Production' forecast to exceed by $2,500 (25%).
Projected: $12,500, Budget: $10,000
```

#### 3. Anomaly Spike Detector
Detects unusual cost spikes using statistical analysis.

**Features:**
- 14-day baseline calculation
- Mean + 2 standard deviations threshold
- Confidence scoring
- Severity levels: low (2σ), medium (2-3σ), high (3-4σ), critical (4+σ)

**Example:**
```
Anomalous cost spike detected for budget 'Production'.
Current: $1,500, Baseline: $250 (3.2σ above mean)
```

### Event Emission

All detections emit canonical events to Kafka using the event-bus wrapper:

**Event Types:**
- `budget.threshold_exceeded` - Threshold crossed
- `budget.forecast_exceeded` - Forecast exceeds budget
- `anomaly.spike` - Anomalous cost spike

**Event Format** (follows `data/contracts/event.schema.json`):
```json
{
  "event_id": "uuid",
  "event_type": "budget.threshold_exceeded",
  "event_version": "1.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "budgets-alerts-service",
  "org_id": "org-123",
  "tenant_id": "tenant-456",
  "payload": {
    "budget_id": "budget-789",
    "budget_name": "Production Budget",
    "budget_amount": 10000,
    "current_spend": 9250,
    "severity": "high",
    "message": "Budget has reached 90%...",
    "threshold_percentage": 90,
    "actual_percentage": 92.5
  },
  "routing": {
    "priority": "high",
    "channels": ["workflow", "notification"]
  }
}
```

## API Endpoints

### Budget CRUD

#### Create Budget
```http
POST /api/v1/budgets
Headers: X-Org-ID: org-123
Content-Type: application/json

{
  "name": "Production Budget",
  "amount": 10000,
  "period": "monthly",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "tenant_id": "tenant-456",
  "filters": {
    "cloud_provider": "aws",
    "environment": "production"
  },
  "thresholds": [50, 80, 90, 100]
}
```

#### List Budgets
```http
GET /api/v1/budgets?tenant_id=tenant-456&status=active&skip=0&limit=100
Headers: X-Org-ID: org-123
```

#### Get Budget
```http
GET /api/v1/budgets/{budget_id}
Headers: X-Org-ID: org-123
```

#### Update Budget
```http
PUT /api/v1/budgets/{budget_id}
Headers: X-Org-ID: org-123
Content-Type: application/json

{
  "amount": 12000,
  "thresholds": [60, 85, 95, 100]
}
```

#### Delete Budget
```http
DELETE /api/v1/budgets/{budget_id}
Headers: X-Org-ID: org-123
```

#### Get Budget Alerts
```http
GET /api/v1/budgets/{budget_id}/alerts?skip=0&limit=100
Headers: X-Org-ID: org-123
```

### Detector Operations

#### Run Detectors (Test Mode)
```http
POST /api/v1/detectors/run
Headers: X-Org-ID: org-123
Content-Type: application/json

{
  "detector_name": "budget_threshold",  // Optional: run specific detector
  "budget_id": "budget-789",             // Optional: run for specific budget
  "test_mode": true                       // Don't emit events in test mode
}
```

**Response:**
```json
{
  "results": [
    {
      "budget_id": "budget-789",
      "budget_name": "Production Budget",
      "detector_name": "budget_threshold",
      "detected": true,
      "severity": "high",
      "message": "Budget 'Production Budget' has reached 90%...",
      "details": {
        "threshold_percentage": 90,
        "actual_percentage": 92.5,
        "current_spend": 9250,
        "budget_amount": 10000
      }
    }
  ],
  "total_detections": 1,
  "events_emitted": 0
}
```

#### List Available Detectors
```http
GET /api/v1/detectors
```

## Database Models

### Budget
- `id` (UUID)
- `org_id` (UUID) - Organization context
- `tenant_id` (UUID, optional) - Tenant context
- `name` (string)
- `description` (text, optional)
- `amount` (float) - Budget amount
- `period` (enum) - monthly, quarterly, yearly, custom
- `start_date` (datetime)
- `end_date` (datetime)
- `filters` (JSON) - Cost filters
- `thresholds` (JSON array) - Alert thresholds
- `current_spend` (float) - Current spend tracking
- `alert_state` (JSON) - Threshold alert state
- `status` (enum) - active, inactive, expired
- Timestamps and audit fields

### BudgetAlert
- `id` (UUID)
- `budget_id` (UUID, FK)
- `org_id` (UUID)
- `alert_type` (string) - threshold, forecast, anomaly
- `severity` (enum) - low, medium, high, critical
- `threshold_percentage` (float, optional)
- `actual_spend` (float)
- `budget_amount` (float)
- `forecast_amount` (float, optional)
- `baseline_value` (float, optional)
- `current_value` (float, optional)
- `confidence` (float) - 0.0 to 1.0
- `message` (text)
- `details` (JSON)
- `event_id` (UUID) - Kafka event ID
- `event_sent` (boolean)
- `created_at` (datetime)

## Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/finops
PORT=8009
LOG_LEVEL=INFO

# Kafka configuration (via event-bus)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_BUDGET_EVENTS=budget-events
```

## Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
cd ../../../data/db/alembic
alembic upgrade head

# Start service
cd -
python src/main.py
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_threshold_detector.py -v

# Run specific test
pytest tests/test_threshold_detector.py::test_threshold_90_percent -v
```

### Test Data

Tests use synthetic cost data:
```python
# Generate 30 days of cost data
cost_data = synthetic_cost_data(
    days=30,
    daily_avg=300.0,
    variance=0.2
)
```

## Production Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
CMD ["python", "src/main.py"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: budgets-alerts-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: budgets-alerts-service
  template:
    metadata:
      labels:
        app: budgets-alerts-service
    spec:
      containers:
      - name: service
        image: budgets-alerts-service:latest
        ports:
        - containerPort: 8009
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
```

## Integration

### With Workflows Service
Detections emit events that trigger workflows:
```yaml
# Budget threshold workflow
name: "Budget Alert Workflow"
trigger_type: event
trigger_config:
  event_types:
    - budget.threshold_exceeded
actions:
  - type: jira
    template: budget_exceeded
  - type: email
    to: finance@company.com
```

### With Cost Data
In production, cost data comes from cost database:
```python
# Replace synthetic data generation with real query
from cost_service import query_costs

cost_data = await query_costs(
    org_id=org_id,
    filters=budget.filters,
    start_date=budget.start_date,
    end_date=datetime.utcnow()
)
```

## Architecture

```
┌─────────────────────────────────────────┐
│      Budgets-Alerts Service             │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐    ┌────────────────┐ │
│  │   Budget    │───▶│   Detectors    │ │
│  │    CRUD     │    │  - Threshold   │ │
│  └─────────────┘    │  - Forecast    │ │
│                     │  - Anomaly     │ │
│                     └────────────────┘ │
│                            │            │
│                            ▼            │
│                     ┌────────────────┐ │
│                     │  Event Bus     │ │
│                     │   (Kafka)      │ │
│                     └────────────────┘ │
└─────────────────────────────────────────┘
                           │
                           ▼
                 ┌──────────────────┐
                 │ Workflows Service │
                 └──────────────────┘
```

## Monitoring

### Metrics
- Budget CRUD operations count
- Detector execution duration
- Detection count by type and severity
- Event emission success/failure rate
- API request latency

### Logging
Structured JSON logs with:
- Request ID
- Org ID
- Budget ID
- Detector name
- Detection results

### Health Checks
```http
GET /health     # Basic health check
GET /ready      # Readiness check (DB connection)
```

## Troubleshooting

### Common Issues

**No detections:**
- Check cost data availability
- Verify budget thresholds configuration
- Ensure sufficient historical data (7+ days for forecast, 14+ for anomaly)

**Events not emitting:**
- Check Kafka connectivity
- Verify event-bus configuration
- Check test_mode flag in detector run

**High false positives:**
- Adjust anomaly threshold (default: 2σ, try 2.5σ or 3σ)
- Increase baseline period
- Review budget filters

## License

Proprietary - All Rights Reserved
