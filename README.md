# FinOps SaaS Platform

A comprehensive, cloud-agnostic FinOps (Financial Operations) platform for multi-tenant cost management, optimization, and governance across AWS, Azure, GCP, Oracle Cloud, Akamai, and on-premises data centers.

## 🌟 Features

- **Multi-Cloud Support**: Unified cost visibility across AWS, Azure, GCP, Oracle, Akamai, and data centers
- **Multi-Tenancy**: Secure tenant isolation with workspace-based organization
- **Cost Normalization**: Canonical cost schema for consistent analysis across providers
- **Virtual Tagging**: Rule-based tagging for resources without native tags
- **Unit Economics**: Allocate cloud costs to business metrics (users, API calls, features)
- **Budgets & Alerts**: Proactive monitoring with forecasting and anomaly detection
- **Recommendations**: Automated savings opportunities and commitment analysis
- **Workflows & Automation**: Event-driven workflows for alerts, approvals, and integrations
- **Enterprise SSO**: OIDC and SAML support with RBAC/ABAC
- **Integrations**: Jira, ServiceNow, Slack, Teams, PagerDuty, and webhooks

## 🏗️ Architecture

This is a microservices-based monorepo built with:
- **Services**: Independent, scalable microservices (Node.js, Python, Go)
- **Packages**: Shared libraries and utilities
- **Apps**: Web UI and admin portal
- **Infrastructure**: Cloud-agnostic deployment (Terraform + Helm)
- **Data Pipeline**: Ingestion → Normalization → Virtual Tagging → Allocation
- **Query Layer**: Portable (Trino/Athena/BigQuery/Snowflake/Synapse/Postgres)

See [Architecture Overview](docs/architecture/overview.md) for details.

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **Go** 1.21+ (optional, for some services)
- **Docker** & **Docker Compose**
- **PostgreSQL** 15+
- **Redis** 7+
- **Terraform** 1.5+ (for infrastructure deployment)
- **kubectl** & **Helm** (for Kubernetes deployment)

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/sivaatluri/fintek.git
cd fintek
make install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Development Environment

```bash
# Start development tools (Postgres, Redis, MinIO, Kafka, etc.)
make tools

# Start core services
make dev
```

### 4. Bootstrap Database

```bash
make migrate
make seed
```

### 5. Access Applications

- **Web UI**: http://localhost:3001
- **API Gateway**: http://localhost:3000
- **Grafana**: http://localhost:3003 (admin/admin)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **MailHog**: http://localhost:8025
- **Keycloak**: http://localhost:8081 (admin/admin)

## 📁 Repository Structure

```
finops-saas/
├── packages/          # Shared libraries
├── services/          # Microservices
├── apps/              # Web applications
├── data/              # Schemas and database
├── infra/             # Infrastructure as Code
├── scripts/           # Utility scripts
├── tests/             # Test suites
├── tools/             # Development tools config
└── docs/              # Documentation
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test suites
make test-unit
make test-integration
make test-e2e

# Run smoke tests
make smoke-test
```

## 🔍 Development

```bash
# Install dependencies
make install

# Run linters
make lint

# Fix linting issues
make lint-fix

# Validate workflow definitions
make validate-workflows

# Generate API documentation
make generate-api

# View Docker logs
make docker-logs

# Clean build artifacts
make clean
```

## 📖 Documentation

- [Architecture](docs/architecture/)
  - [Overview](docs/architecture/overview.md)
  - [Cloud-Agnostic Principles](docs/architecture/principles_cloud_agnostic.md)
  - [Multi-Tenancy](docs/architecture/multi_tenancy.md)
  - [Canonical Cost Schema](docs/architecture/canonical_cost_schema.md)
  - [Authentication & Authorization](docs/architecture/auth_sso_rbac_abac.md)
- [API Documentation](docs/api/)
- [Runbooks](docs/runbooks/)
- [Personas](docs/personas/)

## 🔐 Security

See [SECURITY.md](SECURITY.md) for security policies and vulnerability reporting.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 📝 License

See [LICENSE](LICENSE) for license information.

## 📮 Support

For issues and questions:
- GitHub Issues: https://github.com/sivaatluri/fintek/issues
- Documentation: [docs/](docs/)

## 🗺️ Roadmap

See [CHANGELOG.md](CHANGELOG.md) for version history and upcoming features.

---

Built with ❤️ for FinOps practitioners