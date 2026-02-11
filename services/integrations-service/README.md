# Integrations Service

Production-ready integrations service for FinOps SaaS platform with provider interfaces, delivery tracking, HMAC signing, and automatic retries.

## Features

### Supported Integrations

- **Webhook** - HTTP webhooks with HMAC signing and retry logic
- **Email** - SMTP email delivery (Mailhog compatible for local dev)
- **Jira** - Create issues and add comments (with mock mode)
- **ServiceNow** - Create and update incidents (with mock mode)

### Delivery Management

- ✅ Automatic retry with exponential backoff (2^n minutes, max 60)
- ✅ Configurable max attempts (default: 3)
- ✅ Complete delivery tracking in database
- ✅ Status lifecycle: pending → sent → delivered/failed/retrying
- ✅ Duration tracking for performance monitoring
- ✅ External ID/URL capture for tracking in remote systems
- ✅ Workflow integration support

### Security

- ✅ HMAC-SHA256 webhook signing
- ✅ Timestamp-based replay protection
- ✅ Organization context enforcement on all operations
- ✅ Credentials encrypted in database
- ✅ SSL/TLS verification options

## API Endpoints

### Integrations

```
POST   /api/v1/integrations              Create integration
GET    /api/v1/integrations              List integrations
GET    /api/v1/integrations/{id}         Get integration
PUT    /api/v1/integrations/{id}         Update integration
DELETE /api/v1/integrations/{id}         Delete integration
POST   /api/v1/integrations/{id}/verify  Verify integration
POST   /api/v1/integrations/{id}/test    Test integration
```

### Deliveries

```
POST   /api/v1/deliveries                Create delivery (send)
GET    /api/v1/deliveries                List deliveries
GET    /api/v1/deliveries/{id}           Get delivery
POST   /api/v1/deliveries/{id}/retry     Retry failed delivery
```

### Internal (Background Worker)

```
POST   /api/v1/internal/retry-pending    Retry pending deliveries
```

## Usage Examples

### Create Webhook Integration

```bash
curl -X POST http://localhost:8011/api/v1/integrations \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-123" \
  -d '{
    "name": "Production Webhook",
    "integration_type": "webhook",
    "config": {
      "url": "https://api.example.com/webhook",
      "method": "POST",
      "signature_header": "X-Webhook-Signature",
      "timestamp_header": "X-Webhook-Timestamp"
    },
    "credentials": {
      "signing_secret": "your-secret-key"
    }
  }'
```

### Create Email Integration

```bash
curl -X POST http://localhost:8011/api/v1/integrations \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-123" \
  -d '{
    "name": "Email Notifications",
    "integration_type": "email",
    "config": {
      "smtp_host": "localhost",
      "smtp_port": 1025,
      "from_email": "finops@example.com",
      "from_name": "FinOps Platform"
    }
  }'
```

### Send via Integration

```bash
curl -X POST http://localhost:8011/api/v1/deliveries \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-123" \
  -d '{
    "integration_id": "integration-456",
    "payload": {
      "event": "budget_exceeded",
      "budget_name": "AWS Production",
      "current_spend": 15000,
      "budget_limit": 10000
    }
  }'
```

### Create Jira Issue (Mock Mode)

```bash
curl -X POST http://localhost:8011/api/v1/integrations \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-123" \
  -d '{
    "name": "Jira Integration",
    "integration_type": "jira",
    "config": {
      "base_url": "https://company.atlassian.net",
      "project_key": "FINOPS",
      "issue_type": "Task",
      "mock_mode": true
    }
  }'

# Send via Jira
curl -X POST http://localhost:8011/api/v1/deliveries \
  -H "Content-Type: application/json" \
  -H "X-Org-ID: org-123" \
  -d '{
    "integration_id": "jira-integration-id",
    "payload": {
      "action": "create_issue",
      "summary": "High cloud costs detected",
      "description": "AWS costs exceeded budget by 50%",
      "priority": "High"
    }
  }'
```

## Webhook HMAC Signing

The webhook provider implements HMAC-SHA256 signing for secure delivery verification.

### Signature Format

```
signature = HMAC-SHA256(signing_secret, "{timestamp}.{json_payload}")
```

### Headers Sent

```
X-Webhook-Signature: <hex_signature>
X-Webhook-Timestamp: <unix_timestamp>
```

### Verification (Receiver Side)

```python
import hmac
import hashlib
import json
import time

def verify_webhook(payload, signature, timestamp, secret):
    # Reject old requests (> 5 minutes)
    if abs(int(time.time()) - int(timestamp)) > 300:
        return False
    
    # Reconstruct signature
    payload_str = json.dumps(payload, sort_keys=True)
    expected_sig = hmac.new(
        secret.encode(),
        f"{timestamp}.{payload_str}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison
    return hmac.compare_digest(signature, expected_sig)
```

## Retry Logic

### Exponential Backoff

Delivery attempts use exponential backoff with these intervals:

- Attempt 1: Immediate
- Attempt 2: 2 minutes later (2^1)
- Attempt 3: 4 minutes later (2^2)
- Additional: Up to 60 minutes (2^6, capped)

### Status Transitions

```
PENDING → SENT → DELIVERED (success)
PENDING → SENT → RETRYING (failure, attempts < max)
PENDING → SENT → FAILED (failure, attempts >= max)
```

### Background Worker

Run periodically (e.g., every minute) to retry failed deliveries:

```bash
curl -X POST http://localhost:8011/api/v1/internal/retry-pending
```

Or via cron:

```cron
* * * * * curl -X POST http://localhost:8011/api/v1/internal/retry-pending
```

## Provider Configuration

### Webhook Provider

```json
{
  "url": "https://api.example.com/webhook",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer token"
  },
  "signature_header": "X-Webhook-Signature",
  "timestamp_header": "X-Webhook-Timestamp",
  "timeout": 30,
  "verify_ssl": true
}
```

### Email Provider

```json
{
  "smtp_host": "localhost",
  "smtp_port": 1025,
  "use_tls": false,
  "use_ssl": false,
  "from_email": "finops@example.com",
  "from_name": "FinOps Platform"
}
```

### Jira Provider

```json
{
  "base_url": "https://company.atlassian.net",
  "project_key": "FINOPS",
  "issue_type": "Task",
  "mock_mode": true
}
```

**Credentials:**
```json
{
  "username": "user@example.com",
  "api_token": "your-api-token"
}
```

### ServiceNow Provider

```json
{
  "instance_url": "https://company.service-now.com",
  "table": "incident",
  "mock_mode": true
}
```

**Credentials:**
```json
{
  "username": "admin",
  "password": "password"
}
```

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
make db-migrate

# Start service
cd src
python main.py
```

### With Docker Compose

```bash
# Start all services
make dev-up

# Run migrations
make db-migrate

# Start integrations service
cd services/integrations-service
uvicorn src.main:app --host 0.0.0.0 --port 8011 --reload
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_webhook_signing.py
pytest tests/test_retry_logic.py
```

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/finops

# Service
SERVICE_NAME=integrations-service
SERVICE_VERSION=1.0.0
PORT=8011
LOG_LEVEL=info

# For local dev with Mailhog
SMTP_HOST=localhost
SMTP_PORT=1025
```

## Architecture

### Database Schema

**integrations** table:
- id, org_id, name, integration_type
- config (JSON), credentials (JSON encrypted)
- is_active, is_verified
- last_verified_at, last_used_at
- failure_count
- timestamps

**integration_deliveries** table:
- id, integration_id, org_id
- workflow_execution_id, workflow_step_id
- status, payload (JSON), response (JSON)
- error_message, http_status
- external_id, external_url
- attempts, max_attempts, next_retry_at
- sent_at, delivered_at, duration_ms
- timestamps

### Provider Interface

All providers implement:

```python
class IntegrationProvider(ABC):
    async def send(payload: dict) -> ProviderResponse
    async def verify() -> ProviderResponse
    async def test(payload: dict) -> ProviderResponse
```

### Adding New Providers

1. Create provider class in `src/providers/`:
   ```python
   from .base import IntegrationProvider, ProviderResponse
   
   class MyProvider(IntegrationProvider):
       async def send(self, payload):
           # Implementation
           pass
   ```

2. Register in `src/providers/registry.py`:
   ```python
   ProviderRegistry.register(IntegrationType.MY_PROVIDER, MyProvider)
   ```

3. Add integration type to models.

## Monitoring

### Key Metrics

- Delivery success rate by provider
- Average delivery duration
- Retry rate
- Failure count per integration
- Queue depth (pending retries)

### Health Checks

```bash
# Service health
curl http://localhost:8011/health

# Database connectivity
curl http://localhost:8011/ready
```

## Production Deployment

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: integrations-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: integrations-service
        image: finops/integrations-service:latest
        ports:
        - containerPort: 8011
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
```

### Background Worker

Deploy separate cron job for retries:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: integration-retry-worker
spec:
  schedule: "*/1 * * * *"  # Every minute
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: retry-worker
            image: curlimages/curl:latest
            command:
            - curl
            - -X
            - POST
            - http://integrations-service:8011/api/v1/internal/retry-pending
```

## Security Considerations

1. **Credentials Storage**: Encrypt credentials in database
2. **HMAC Secrets**: Use strong, random secrets (32+ characters)
3. **Timestamp Validation**: Reject webhooks older than 5 minutes
4. **SSL/TLS**: Always verify SSL in production
5. **Rate Limiting**: Implement per-integration rate limits
6. **Org Isolation**: All queries enforce org_id context

## Troubleshooting

### Deliveries Stuck in RETRYING

Check `next_retry_at` timestamp and ensure retry worker is running:

```sql
SELECT id, status, attempts, next_retry_at, error_message
FROM integration_deliveries
WHERE status = 'retrying'
ORDER BY next_retry_at;
```

### High Failure Rate

Check integration failure counts:

```sql
SELECT name, integration_type, failure_count, last_used_at
FROM integrations
WHERE failure_count > 10
ORDER BY failure_count DESC;
```

### Webhook Signature Failures

Verify:
1. Secret matches on both sides
2. Timestamp is included in signature
3. JSON payload is sorted consistently
4. Timestamp tolerance is reasonable

## License

See LICENSE file in repository root.
