# Auth Service

Enterprise authentication and authorization service with OIDC, SAML, SCIM, and RBAC support.

## Features

### Core Authentication
- ✅ **OIDC/OAuth2** - Keycloak integration with JWT validation
- 🚧 **SAML 2.0** - Enterprise SSO (interfaces defined, implementation pending)
- 🚧 **SCIM 2.0** - User provisioning (interfaces defined, implementation pending)
- ✅ **JWT Tokens** - Token validation and generation
- ✅ **Session Management** - Secure session handling

### Authorization (RBAC)
- ✅ **Role-Based Access Control** - 7 predefined roles
- ✅ **Permission System** - Fine-grained permissions
- ✅ **Org/Tenant Context** - Multi-tenant authorization
- ✅ **Database Models** - SQLAlchemy models for RBAC

### Security
- ✅ **Token Validation** - JWT signature and expiry verification
- ✅ **JWKS Support** - Public key fetching from Keycloak
- ✅ **Org Context Enforcement** - Required on all endpoints
- ✅ **Rate Limiting** - Configurable request limits
- ✅ **Secure Sessions** - HttpOnly cookies, SameSite protection

## Architecture

```
auth-service/
├── src/
│   ├── main.py              # FastAPI application
│   ├── oidc/                # OIDC/JWT implementation
│   │   ├── auth.py          # Authentication handler
│   │   └── jwt_utils.py     # JWT validation & generation
│   ├── saml/                # SAML scaffolding
│   │   ├── interfaces.py    # SAML interfaces
│   │   └── README.md        # Implementation guide
│   ├── models/              # Database models
│   │   └── rbac.py          # User, Role, Permission models
│   └── rbac/                # RBAC logic (future)
├── tests/                   # Comprehensive test suite
│   ├── test_jwt_utils.py
│   ├── test_oidc_auth.py
│   └── test_main.py
├── requirements.txt
└── Dockerfile
```

## Configuration

All configuration is loaded from environment variables (no hardcoded values):

```bash
# Keycloak/OIDC
AUTH_KEYCLOAK__SERVER_URL=http://keycloak:8081
AUTH_KEYCLOAK__REALM=finops
AUTH_KEYCLOAK__CLIENT_ID=finops-auth

# JWT
AUTH_JWT__SECRET_KEY=your-secret-key
AUTH_JWT__ALGORITHM=HS256
AUTH_JWT__ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database
AUTH_DATABASE_URL=postgresql://user:pass@host:5432/db

# Kafka Topics (configurable)
AUTH_KAFKA_TOPICS__USER_EVENTS=user-events
AUTH_KAFKA_TOPICS__LOGIN_EVENTS=login-events
```

See `packages/config-py` for full configuration schema.

## API Endpoints

### Authentication
- `GET /auth/me` - Get current user info (requires auth)
- `POST /auth/logout` - Logout current user (requires auth)
- `GET /auth/oidc/config` - OIDC discovery information

### SAML (Scaffolding)
- `POST /auth/saml/acs` - Assertion Consumer Service
- `GET /auth/saml/metadata` - SP metadata XML

### SCIM (Scaffolding)
- `GET /auth/scim/v2/Users` - List users
- `POST /auth/scim/v2/Users` - Create user

### Health
- `GET /health` - Health check
- `GET /ready` - Readiness check

## Usage Examples

### Get Current User
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8001/auth/me
```

Response:
```json
{
  "user_id": "user-123",
  "username": "john.doe",
  "email": "john@example.com",
  "roles": ["finops_engineer"],
  "org_id": "org-456",
  "tenant_id": "tenant-789"
}
```

### Logout
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"everywhere": false}' \
  http://localhost:8001/auth/logout
```

## Development

### Setup
```bash
cd services/auth-service

# Install dependencies
pip install -r requirements.txt

# Run migrations (TODO)
alembic upgrade head

# Start service
python src/main.py
```

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Environment Variables
Copy `.env.example` to `.env` and adjust values:
```bash
cp ../../.env.example .env
```

## OIDC Integration with Keycloak

### 1. Start Keycloak
```bash
make dev-tools-up
```

### 2. Configure Realm
1. Access Keycloak admin: http://localhost:8081
2. Create realm: `finops`
3. Create client: `finops-auth`
4. Configure client:
   - Client Protocol: openid-connect
   - Access Type: confidential
   - Valid Redirect URIs: http://localhost:*

### 3. Test Token Validation
```bash
# Get token from Keycloak
TOKEN=$(curl -X POST \
  http://localhost:8081/realms/finops/protocol/openid-connect/token \
  -d "client_id=finops-auth" \
  -d "client_secret=<secret>" \
  -d "grant_type=password" \
  -d "username=demo" \
  -d "password=demo" \
  | jq -r '.access_token')

# Use token with auth service
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/auth/me
```

## RBAC Models

### Roles
- `SUPER_ADMIN` - Full system access
- `ORG_ADMIN` - Organization administration
- `TENANT_ADMIN` - Tenant administration
- `FINOPS_ENGINEER` - FinOps operations
- `DEVELOPER` - Development access
- `VIEWER` - Read-only access
- `AUDITOR` - Audit log access

### Permissions
Format: `resource:action`

Examples:
- `costs:read`, `costs:write`
- `budgets:read`, `budgets:write`
- `users:read`, `users:write`
- `admin:all`

### Database Schema
```sql
-- Users table
users (id, username, email, external_id, external_provider, ...)

-- Roles table
roles (id, name, display_name, description, is_system, ...)

-- Permissions table
permissions (id, name, resource, action, ...)

-- Many-to-many relationships
user_roles (user_id, role_id, org_id)
role_permissions (role_id, permission_id)

-- Organization context
user_organizations (user_id, org_id, is_active)

-- Sessions
sessions (id, user_id, session_token, id_token, expires_at, ...)
```

## Security Considerations

### Token Validation
- ✅ Signature verification using JWKS
- ✅ Expiration checking
- ✅ Issuer validation
- ✅ Audience validation
- ✅ Algorithm verification (RS256 for Keycloak)

### Session Security
- ✅ HttpOnly cookies (prevent XSS)
- ✅ SameSite=Lax (CSRF protection)
- ✅ Secure flag (HTTPS only in production)
- ✅ Session expiration
- ✅ Refresh token rotation

### Best Practices
- ✅ No secrets in code or logs
- ✅ All config from environment
- ✅ Structured logging with trace IDs
- ✅ Rate limiting on auth endpoints
- ✅ Org context required for all operations
- ✅ Comprehensive error handling

## Monitoring

### Metrics (Prometheus)
- `auth_login_total` - Login attempts
- `auth_login_failures` - Failed logins
- `auth_token_validation_duration` - Token validation time
- `auth_sessions_active` - Active sessions

### Logs (JSON)
All logs include:
- Request ID
- User ID (if authenticated)
- Org ID (if in context)
- Trace ID (OpenTelemetry)

### Events (Kafka)
- `user-events` - User lifecycle (created, updated, deleted)
- `login-events` - Login/logout events
- `permission-changes` - RBAC changes
- `session-events` - Session created/expired

## Roadmap

### Phase 1: OIDC (Complete ✅)
- [x] Keycloak integration
- [x] JWT validation
- [x] Token refresh
- [x] User info endpoint
- [x] Logout support

### Phase 2: RBAC (In Progress)
- [x] Database models
- [x] Permission system
- [ ] Role assignment API
- [ ] Permission checking
- [ ] Org/tenant scoping

### Phase 3: SAML (Planned)
- [ ] Implement ISAMLIdentityProvider
- [ ] Implement ISAMLServiceProvider
- [ ] XML signature validation
- [ ] Metadata management
- [ ] Multi-IdP support

### Phase 4: SCIM (Planned)
- [ ] User provisioning
- [ ] Group sync
- [ ] Attribute mapping
- [ ] Webhook notifications

### Phase 5: Advanced Features
- [ ] MFA support
- [ ] Passwordless auth
- [ ] Social login
- [ ] Device management
- [ ] Audit logging
- [ ] Session analytics

## Troubleshooting

### Token Validation Fails
```bash
# Check Keycloak is running
curl http://localhost:8081/realms/finops/.well-known/openid-configuration

# Check JWKS endpoint
curl http://localhost:8081/realms/finops/protocol/openid-connect/certs

# Verify token
jwt decode <token>
```

### Database Connection Issues
```bash
# Check PostgreSQL
psql -h localhost -U finops -d finops

# Run migrations
alembic current
alembic upgrade head
```

### Kafka Not Working
```bash
# Check Kafka topics
kafka-topics --list --bootstrap-server localhost:9092

# Check topic messages
kafka-console-consumer --topic finops.user-events \
  --bootstrap-server localhost:9092 --from-beginning
```

## Contributing

1. Follow the established patterns
2. Add tests for new features
3. Update documentation
4. No hardcoded values
5. Use type hints
6. Add logging

## License

Proprietary - FinOps SaaS Platform
