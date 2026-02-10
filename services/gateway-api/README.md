# Gateway API Service

API Gateway and Backend-for-Frontend (BFF) for the FinOps SaaS platform.

## Features

- **API Gateway**: Routes requests to appropriate microservices
- **Authentication**: Validates JWT tokens and session
- **Rate Limiting**: Per-user and per-org rate limits
- **Request Aggregation**: Combines data from multiple services
- **Response Transformation**: Formats responses for UI consumption

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python src/main.py

# Or with uvicorn
uvicorn src.main:app --reload --port 8000
```

### Docker

```bash
# Build image
docker build -t gateway-api:latest -f services/gateway-api/Dockerfile .

# Run container
docker run -p 8000:8000 gateway-api:latest
```

### Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## API Endpoints

### Health Checks
- `GET /health` - Basic health check
- `GET /ready` - Readiness check with dependencies

### Gateway API
- `GET /api/v1/status` - Service status
- `GET /api/v1/protected` - Example protected endpoint

## Configuration

Environment variables:

```bash
SERVICE_NAME=gateway-api
SERVICE_VERSION=1.0.0
ENVIRONMENT=development
PORT=8000
LOG_LEVEL=INFO
OTEL_ENABLED=true
OTEL_ENDPOINT=http://otel-collector:4317
```

See `.env.example` in repository root for all options.

## Architecture

```
src/
├── main.py           # Application entry point
├── routes/           # API route handlers
├── middleware/       # Custom middleware
├── services/         # Business logic
└── models/           # Pydantic models
```

## Dependencies

- finops-common: Shared utilities
- FastAPI: Web framework
- httpx: HTTP client for service calls
- Pydantic: Data validation

## Deployment

Kubernetes deployment via Helm chart in `infra/helm/charts/gateway-api/`.

## License

See LICENSE file in repository root.
