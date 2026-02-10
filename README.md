# FinOps SaaS Platform

A cloud-agnostic, multi-tenant FinOps (Financial Operations) SaaS platform for comprehensive cloud cost management, optimization, and governance.

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (v20.10+) or Docker Engine with Docker Compose
- Make (for using the Makefile commands)
- 8GB+ RAM available for Docker
- 20GB+ free disk space

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/sivaatluri/fintek.git
   cd fintek
   ```

2. **Bootstrap the development environment**
   ```bash
   make bootstrap
   ```
   This will:
   - Create `.env` from `.env.example`
   - Create necessary configuration directories
   - Start all development services
   - Start observability tools

3. **Verify services are running**
   ```bash
   make ps
   ```

## 📦 Development Services

### Core Infrastructure (`docker-compose.dev.yml`)

The development environment includes the following core services:

| Service    | Port(s)       | Purpose                          | Access                        |
|------------|---------------|----------------------------------|-------------------------------|
| PostgreSQL | 5432          | Primary database                 | `postgres://finops:***@localhost:5432/finops` |
| Redis      | 6379          | Cache & session store            | `redis://localhost:6379`      |
| Kafka      | 9092, 29092   | Event streaming                  | `localhost:9092`              |
| Zookeeper  | 2181          | Kafka coordination               | `localhost:2181`              |
| MinIO      | 9000, 9001    | S3-compatible object storage     | Console: http://localhost:9001 |
| Trino      | 8080          | Distributed SQL query engine     | http://localhost:8080         |

### Development Tools (`docker-compose.tools.yml`)

Additional tools for auth, observability, and testing:

| Service        | Port(s)       | Purpose                          | Access                        |
|----------------|---------------|----------------------------------|-------------------------------|
| Keycloak       | 8081          | SSO & identity management        | http://localhost:8081 (admin/admin) |
| MailHog        | 1025, 8025    | Email testing                    | UI: http://localhost:8025, SMTP: 1025 |
| OTEL Collector | 4317, 4318    | OpenTelemetry collector          | gRPC: 4317, HTTP: 4318        |
| Prometheus     | 9090          | Metrics collection               | http://localhost:9090         |
| Grafana        | 3000          | Observability dashboard          | http://localhost:3000 (admin/admin) |

## 🛠️ Common Commands

### Environment Management

```bash
# Start all development services
make dev-up

# Start observability tools
make dev-tools-up

# Stop all services
make dev-down
make dev-tools-down

# Restart services
make dev-restart

# Show running containers
make ps
make status
```

### Logs & Monitoring

```bash
# View logs (last 100 lines)
make logs

# Follow logs in real-time
make logs-follow

# View tool logs
make tools-logs
```

### Code Quality

```bash
# Run linters
make lint

# Run tests
make test

# Format code
make fmt

# Run all checks
make check

# Validate workflow YAML files
make validate-workflows
```

### Database Management

```bash
# Initialize database with migrations
make init-db

# Seed database with demo data
make seed-db
```

### Cleanup

```bash
# Stop services and remove containers
make clean

# Remove all data volumes (WARNING: deletes all data!)
make clean-volumes
```

### Help

```bash
# Show all available commands
make help
```

## 📁 Repository Structure

```
finops-saas/
├── apps/                    # Frontend applications
│   ├── web/                # Customer-facing UI
│   └── admin-portal/       # Internal admin portal
├── services/               # Backend microservices
│   ├── gateway-api/        # API gateway
│   ├── auth-service/       # Authentication & authorization
│   ├── tenant-service/     # Multi-tenancy management
│   ├── cost-ingestion-service/
│   ├── connectors/         # Cloud provider integrations
│   ├── workflows-service/  # Workflow automation
│   └── ...                 # 19 total services
├── packages/               # Shared libraries
│   ├── common/
│   ├── cloud-adapters/     # Cloud provider abstractions
│   ├── workflow-dsl/       # Workflow DSL and runtime
│   └── ...
├── data/
│   ├── contracts/          # Data schemas
│   └── db/                 # Database migrations
├── docs/                   # Documentation
│   ├── architecture/
│   ├── runbooks/
│   └── api/
├── infra/                  # Infrastructure as code
│   ├── terraform/
│   ├── helm/
│   └── ci/
├── tools/                  # Development tool configs
│   ├── trino/
│   ├── prometheus/
│   ├── grafana/
│   └── otel-collector/
├── scripts/                # Automation scripts
├── tests/                  # Test suites
├── docker-compose.dev.yml  # Development services
├── docker-compose.tools.yml # Development tools
├── Makefile                # Development automation
└── .env.example            # Environment variables template
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize as needed:

```bash
cp .env.example .env
```

Key configuration sections:
- **PostgreSQL**: Database connection settings
- **Redis**: Cache configuration
- **Kafka**: Event streaming configuration
- **MinIO**: Object storage (S3-compatible)
- **Keycloak**: SSO and authentication
- **Observability**: OTEL, Prometheus, Grafana

### Service Configuration

Individual service configurations are located in:
- `tools/trino/` - Trino query engine configuration
- `tools/prometheus/` - Prometheus scrape configs
- `tools/grafana/` - Grafana datasources and dashboards
- `tools/otel-collector/` - OpenTelemetry collector pipeline

## 🏗️ Architecture Overview

This platform follows a cloud-agnostic, microservices architecture:

- **Multi-tenant**: Secure tenant isolation with workspace hierarchy
- **Cloud-agnostic**: Adapters for AWS, Azure, GCP, Oracle, Akamai, and on-premises
- **Event-driven**: Kafka-based event streaming for workflows and integrations
- **Portable query layer**: Trino for unified data access across storage backends
- **Observability-first**: OpenTelemetry, Prometheus, and Grafana integration

### Key Capabilities

1. **Cost Ingestion & Normalization**
   - Multi-cloud billing data ingestion
   - Canonical cost schema transformation
   - Virtual tagging and enrichment

2. **Intelligence & Automation**
   - Budget tracking and alerts
   - Anomaly detection
   - Cost forecasting
   - Recommendation engine
   - Workflow automation (YAML DSL)

3. **Integrations**
   - OIDC/SAML SSO
   - Jira, ServiceNow, Zendesk
   - Slack, Teams, PagerDuty
   - Email and webhooks

4. **Persona-based Views**
   - Executive dashboards
   - FinOps team workspace
   - Engineering cost attribution
   - Product operations unit economics

## 🧪 Testing

```bash
# Run all tests
make test

# Run contract tests
npm run test:contract

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e
```

## 📚 Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [API Guidelines](docs/api/api_guidelines.md)
- [Runbooks](docs/runbooks/)
- [Personas](docs/personas/)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 🔒 Security

See [SECURITY.md](SECURITY.md) for security policies and reporting vulnerabilities.

## 📄 License

See [LICENSE](LICENSE) for license information.

## 🆘 Troubleshooting

### Services won't start

1. Check Docker has enough resources (8GB+ RAM recommended)
2. Ensure ports are not already in use
3. Check logs: `make logs-follow`

### Database connection issues

```bash
# Restart PostgreSQL
docker compose -f docker-compose.dev.yml restart postgres

# Check PostgreSQL logs
docker compose -f docker-compose.dev.yml logs postgres
```

### Clean slate restart

```bash
# Stop everything and remove volumes
make clean-volumes

# Start fresh
make bootstrap
```

### Check service health

```bash
# View all container statuses
make ps

# Check specific service logs
docker compose -f docker-compose.dev.yml logs <service-name>
```

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation in `docs/`
- Review runbooks in `docs/runbooks/`
