# Repository Structure

This document provides an overview of the FinOps SaaS platform monorepo structure.

## Overview

This is a comprehensive, cloud-agnostic FinOps (Financial Operations) SaaS platform organized as a monorepo. The platform provides multi-tenant cost management, optimization, and governance across AWS, Azure, GCP, Oracle Cloud, Akamai, and on-premises data centers.

## Root Directory Structure

```
fintek/
├── .editorconfig              # Editor configuration
├── .env.example               # Environment variables template
├── .eslintrc.js               # ESLint configuration
├── .gitignore                 # Git ignore rules
├── .prettierrc.json           # Prettier configuration
├── CHANGELOG.md               # Version history
├── CODEOWNERS                 # Code ownership assignments
├── CONTRIBUTING.md            # Contribution guidelines
├── LICENSE                    # MIT License
├── Makefile                   # Build and development tasks
├── README.md                  # Main documentation
├── SECURITY.md                # Security policies
├── docker-compose.dev.yml     # Development services
├── docker-compose.tools.yml   # Development tools
├── package.json               # Root package configuration
├── tsconfig.json              # TypeScript configuration
├── apps/                      # Frontend applications
├── data/                      # Data schemas and contracts
├── docs/                      # Documentation
├── infra/                     # Infrastructure as Code
├── packages/                  # Shared libraries
├── scripts/                   # Utility scripts
├── services/                  # Microservices
├── tests/                     # Test suites
└── tools/                     # Development tools config
```

## Key Directories

### `/apps` - Applications
Frontend applications for end users and administrators.

- **web/**: Customer-facing React/Next.js application with persona-based dashboards
- **admin-portal/**: Internal admin and support portal

### `/packages` - Shared Libraries
Reusable packages used across services and applications.

- **common/**: Types, errors, utilities, HTTP clients
- **config/**: Configuration loading and validation
- **telemetry/**: OpenTelemetry wrappers and logging
- **policy-engine/**: RBAC/ABAC policy enforcement
- **feature-flags/**: Feature gating per tenant/plan
- **secrets/**: Vault/Secrets Manager abstraction
- **cloud-adapters/**: Provider-neutral cloud service abstractions
- **cost-model/**: Canonical cost schemas and transformations
- **workflow-dsl/**: Workflow DSL schemas and runtime
- **ui-kit/**: Shared React components
- **sdk/**: Public SDKs (TypeScript, Python, Go)

### `/services` - Microservices
Independent, scalable backend services.

**Core Services:**
- **gateway-api/**: API Gateway/BFF for UI and public API
- **auth-service/**: OIDC, SAML SSO, sessions, SCIM, RBAC
- **tenant-service/**: Multi-tenant management
- **billing-service/**: SaaS billing and invoicing

**Cost Pipeline:**
- **cost-ingestion-service/**: Orchestrates data collection
- **connectors/**: Provider-specific ingestion (AWS, Azure, GCP, Oracle, etc.)
- **cost-normalization-service/**: Transforms to canonical schema
- **virtual-tagging-service/**: Rule-based tagging
- **allocation-service/**: Unit economics and chargeback

**Analytics & Optimization:**
- **query-service/**: Unified query layer (Trino/Athena/BigQuery)
- **budgets-alerts-service/**: Budgets, forecasting, anomaly detection
- **recommendations-service/**: Savings opportunities
- **reporting-service/**: Scheduled reports and exports
- **data-quality-service/**: Reconciliation and lineage

**Automation:**
- **workflows-service/**: Event-driven workflow engine
- **integrations-service/**: External integrations (Jira, Slack, etc.)

**Platform:**
- **metering-service/**: App metrics for unit economics
- **audit-service/**: Audit trails
- **admin-ops-service/**: Support tooling

### `/data` - Data Layer
Data schemas, contracts, and database artifacts.

- **contracts/**: Canonical schemas (normalized_cost, events, etc.)
- **db/**: Database migrations, seeds, views
- **dbt/**: Data transformation models (optional)

### `/docs` - Documentation
Comprehensive platform documentation.

- **architecture/**: System design and architecture docs
- **runbooks/**: Operational procedures and troubleshooting
- **api/**: OpenAPI specs and API guidelines
- **personas/**: User persona documentation (Executive, FinOps, Engineering, etc.)

### `/infra` - Infrastructure as Code
Deployment and infrastructure configurations.

- **terraform/**: Infrastructure provisioning
  - **modules/**: Reusable Terraform modules
  - **providers/**: Provider-specific configs (AWS, Azure, GCP, on-prem)
  - **envs/**: Environment-specific configurations
- **helm/**: Kubernetes Helm charts
- **ci/**: CI/CD configurations

### `/scripts` - Utility Scripts
Development and operational scripts.

- **bootstrap_dev.sh**: Bootstrap development environment
- **run_migrations.sh**: Run database migrations
- **seed_demo_data.sh**: Seed demo data
- **validate_workflows.sh**: Validate workflow definitions
- **smoke_test.sh**: Run smoke tests

### `/tests` - Test Suites
Comprehensive testing infrastructure.

- **contract-tests/**: Schema and API contract tests
- **integration-tests/**: Service-to-service tests
- **e2e/**: End-to-end UI tests (Playwright)
- **load/**: Performance tests (k6)

### `/tools` - Development Tools
Local development tool configurations.

- **trino/**: Portable query engine config
- **minio/**: S3-compatible object storage
- **postgres/**: Database configuration
- **redis/**: Cache configuration
- **kafka/**: Message queue configuration
- **otel-collector/**: OpenTelemetry collector
- **grafana/**: Monitoring dashboards
- **prometheus/**: Metrics collection
- **keycloak/**: Local SSO
- **mailhog/**: Email testing

## Key Files Created

### Configuration Files
- `.gitignore` - Comprehensive ignore patterns
- `.editorconfig` - Editor configuration
- `.env.example` - Environment variable template
- `tsconfig.json` - TypeScript configuration
- `.eslintrc.js` - Linting rules
- `.prettierrc.json` - Code formatting rules
- `Makefile` - Build automation
- `docker-compose.dev.yml` - Development services
- `docker-compose.tools.yml` - Development tools
- `package.json` - Monorepo configuration

### Documentation
- `README.md` - Main project documentation
- `CONTRIBUTING.md` - Contribution guidelines
- `SECURITY.md` - Security policies
- `CHANGELOG.md` - Version history
- `LICENSE` - MIT License
- `CODEOWNERS` - Code ownership

### Architecture Documentation
- `docs/architecture/overview.md` - System architecture
- `docs/architecture/principles_cloud_agnostic.md` - Cloud portability
- `docs/architecture/multi_tenancy.md` - Multi-tenant design
- `docs/architecture/canonical_cost_schema.md` - Data schema

### Persona Documentation
- `docs/personas/executive.md` - Executive user guide
- `docs/personas/finops.md` - FinOps practitioner guide

### Operational Documentation
- `docs/runbooks/oncall.md` - On-call procedures
- `docs/api/openapi.yaml` - API specification

### Data Contracts
- `data/contracts/normalized_cost.schema.json` - Canonical cost schema
- `data/contracts/event.schema.json` - Event schema

### Workflow DSL
- `packages/workflow-dsl/schemas/workflow.schema.json`
- `packages/workflow-dsl/schemas/condition.schema.json`
- `packages/workflow-dsl/schemas/action.schema.json`
- `packages/workflow-dsl/examples/budget_threshold.yml`
- `packages/workflow-dsl/examples/anomaly_spike.yml`

### Service Configurations
- `services/gateway-api/Dockerfile`
- `services/gateway-api/package.json`
- `services/budgets-alerts-service/Dockerfile`
- `services/budgets-alerts-service/requirements.txt`
- `apps/web/Dockerfile`
- `apps/web/package.json`
- `packages/common/package.json`

### Scripts
- `scripts/bootstrap_dev.sh` - Development setup
- `scripts/run_migrations.sh` - Database migrations
- `scripts/seed_demo_data.sh` - Demo data seeding
- `scripts/validate_workflows.sh` - Workflow validation
- `scripts/smoke_test.sh` - Smoke tests

### Infrastructure
- `infra/terraform/providers/aws/README.md` - AWS deployment guide
- `infra/helm/README.md` - Kubernetes deployment guide

## Total Files Created

- **59** configuration, documentation, and code files
- **Complete directory structure** with ~100+ directories
- **Comprehensive documentation** covering architecture, operations, and user guides
- **Development environment** ready to use

## Technology Stack

### Backend
- Node.js/TypeScript (API services)
- Python (Data processing, ML)
- Go (High-performance connectors)

### Frontend
- React/Next.js
- TypeScript
- Tailwind CSS

### Data
- PostgreSQL (Metadata)
- Redis (Caching)
- Kafka (Events)
- S3/MinIO (Object storage)
- Trino/Athena/BigQuery (Query engines)

### Infrastructure
- Kubernetes
- Terraform
- Helm
- Docker

### Observability
- OpenTelemetry
- Prometheus
- Grafana
- Jaeger

## Getting Started

1. **Clone repository**
   ```bash
   git clone https://github.com/sivaatluri/fintek.git
   cd fintek
   ```

2. **Install dependencies**
   ```bash
   make install
   ```

3. **Start development environment**
   ```bash
   make tools  # Start infrastructure
   make dev    # Start services
   ```

4. **Bootstrap database**
   ```bash
   make migrate
   make seed
   ```

5. **Access applications**
   - Web UI: http://localhost:3001
   - API: http://localhost:3000
   - Grafana: http://localhost:3003

## Next Steps

This monorepo structure is now ready for:
1. Implementing service code
2. Adding comprehensive tests
3. Deploying to cloud providers
4. Onboarding development teams
5. Building features

See documentation in `/docs` for detailed guides.
