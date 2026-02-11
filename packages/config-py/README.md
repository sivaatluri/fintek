# Config-PY - Configuration Management Package

Typed configuration schemas for FinOps services using Pydantic.

## Features

- **Type-safe configuration** with Pydantic validation
- **Environment variable loading** with .env file support
- **Service-specific schemas** with shared base
- **No hardcoded values** - all configuration from environment
- **Kafka topics configuration** per service
- **Integration configs** (Keycloak, SAML, etc.)

## Installation

```bash
pip install -e packages/config-py
```

## Usage

```python
from finops_config import AuthServiceConfig

# Load configuration from environment
config = AuthServiceConfig()

# Access typed configuration
print(config.keycloak.server_url)
print(config.jwt.secret_key)
print(config.kafka.topics.user_events)
```

## Service Configs

- `AuthServiceConfig` - Authentication service
- `TenantServiceConfig` - Tenant management
- `CostServiceConfig` - Cost ingestion/normalization
- More to come...

## Configuration Sources

1. Environment variables
2. .env files
3. Config files (optional)
4. Defaults (for development)

## Validation

All configurations are validated on load:
- Required fields must be present
- Types must match
- Formats are validated (URLs, ports, etc.)
- Enums are enforced

## Testing

```bash
cd packages/config-py
pytest tests/
```
