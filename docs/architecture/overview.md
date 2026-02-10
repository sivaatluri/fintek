# Architecture Overview

## Executive Summary

The FinOps SaaS platform is a cloud-agnostic, multi-tenant financial operations system designed to provide unified cost visibility, optimization, and governance across multiple cloud providers and on-premises data centers.

## Design Principles

### 1. Cloud-Agnostic
- **Portable deployment**: Runs on AWS, Azure, GCP, or on-premises
- **Provider-neutral abstractions**: Unified interfaces for all cloud operations
- **Canonical data model**: Normalized cost schema across all providers

### 2. Multi-Tenant
- **Tenant isolation**: Secure data separation at all layers
- **Per-tenant customization**: Workflows, budgets, tags, and allocations
- **Workspace hierarchy**: Organizations → Tenants → Workspaces → Accounts

### 3. Scalable & Performant
- **Microservices architecture**: Independent scaling of components
- **Event-driven design**: Asynchronous processing for heavy workloads
- **Query optimization**: Portable query engines (Trino, Athena, BigQuery, etc.)

### 4. Extensible
- **Plugin architecture**: Easy addition of new cloud providers
- **Workflow DSL**: Custom alerting and automation rules
- **API-first**: All features accessible via REST/GraphQL APIs

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         External Systems                         │
│  Cloud APIs │ SSO/SAML │ Jira │ Slack │ ServiceNow │ Webhooks   │
└─────────────────────────────────────────────────────────────────┘
                                  ▲
                                  │
┌─────────────────────────────────┼───────────────────────────────┐
│                                 │                   Apps Layer   │
│                ┌────────────────┴────────────────┐              │
│                │       API Gateway / BFF          │              │
│                └──────────────┬──────────────────┘              │
│                               │                                  │
│          ┌────────────────────┼────────────────────┐            │
│          │                    │                    │            │
│    ┌─────▼─────┐       ┌─────▼─────┐       ┌─────▼─────┐      │
│    │  Web UI   │       │ Admin UI  │       │ Mobile API│      │
│    │ (React)   │       │           │       │           │      │
│    └───────────┘       └───────────┘       └───────────┘      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          Services Layer                          │
│                                                                   │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐   │
│  │   Auth    │  │  Tenant   │  │  Billing  │  │   Audit   │   │
│  │  Service  │  │  Service  │  │  Service  │  │  Service  │   │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           Cost Data Pipeline                              │   │
│  │  Ingestion → Normalization → Virtual Tags → Allocation  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐   │
│  │  Budgets  │  │Recommenda-│  │ Workflows │  │Integrations│   │
│  │  &Alerts  │  │   tions   │  │  Service  │  │  Service  │   │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘   │
│                                                                   │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐   │
│  │   Query   │  │ Reporting │  │Data Quality│  │ Metering  │   │
│  │  Service  │  │  Service  │  │  Service  │  │  Service  │   │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Data Layer                               │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │PostgreSQL│  │  Redis   │  │  Kafka   │  │  MinIO   │       │
│  │  (Meta)  │  │ (Cache)  │  │ (Events) │  │(Storage) │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Data Lake (Portable: S3/Azure Blob/GCS/MinIO)          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │   Raw    │  │Normalized│  │ Allocated│              │   │
│  │  │  Costs   │  │  Costs   │  │  Costs   │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Query Engine (Portable: Trino/Athena/BigQuery/...)     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### Cost Data Pipeline

1. **Ingestion Service**: Orchestrates data collection from cloud providers
2. **Connectors**: Provider-specific data extraction (AWS CUR, Azure EA, GCP Billing Export, etc.)
3. **Normalization Service**: Transforms raw data to canonical schema
4. **Virtual Tagging Service**: Applies rule-based tags
5. **Allocation Service**: Distributes costs to business units

### Query & Analytics

- **Query Service**: Unified query interface across storage backends
- **Reporting Service**: Scheduled reports and exports
- **Data Quality Service**: Reconciliation and lineage tracking

### Governance & Optimization

- **Budgets & Alerts Service**: Monitors spend, forecasts, detects anomalies
- **Recommendations Service**: Identifies waste and savings opportunities
- **Workflows Service**: Event-driven automation and notifications

### Integration & Platform

- **Auth Service**: SSO (OIDC/SAML), RBAC/ABAC, SCIM
- **Tenant Service**: Multi-tenant management
- **Integrations Service**: External system connectors (Jira, Slack, etc.)
- **API Gateway**: Rate limiting, auth, routing

## Data Flow

### Cost Ingestion Flow

```
Cloud Provider APIs
      ↓
  Connectors (scheduled jobs)
      ↓
  Raw Cost Data (Parquet/CSV in Data Lake)
      ↓
  Normalization Service
      ↓
  Normalized Cost Data (Canonical Schema)
      ↓
  Virtual Tagging Service
      ↓
  Tagged Cost Data
      ↓
  Allocation Service
      ↓
  Allocated Cost Data (Ready for queries)
```

### Alert & Workflow Flow

```
Budgets/Alerts Service (detects threshold breach)
      ↓
  Event Published (Kafka/PubSub)
      ↓
  Workflows Service (matches rules)
      ↓
  Condition Evaluation (Rego/CEL)
      ↓
  Action Execution (Send notification, create ticket, webhook)
      ↓
  Integrations Service
      ↓
  External System (Slack, Jira, ServiceNow, etc.)
```

## Technology Stack

### Backend
- **Node.js/TypeScript**: API services, workflows
- **Python**: Data processing, ML models
- **Go**: High-performance connectors

### Frontend
- **React/Next.js**: Web UI
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling

### Data
- **PostgreSQL**: Metadata, config
- **Redis**: Caching, sessions
- **Kafka/RabbitMQ**: Event streaming
- **S3/MinIO**: Object storage (portable)
- **Trino/Athena/BigQuery**: Query engines (portable)

### Infrastructure
- **Kubernetes**: Container orchestration
- **Terraform**: Infrastructure as Code
- **Helm**: Application deployment
- **Docker**: Containerization

### Observability
- **OpenTelemetry**: Traces, metrics, logs
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards
- **Jaeger**: Distributed tracing

## Deployment Models

### Cloud Deployment
- **AWS**: EKS, RDS, S3, Athena
- **Azure**: AKS, PostgreSQL, Blob Storage, Synapse
- **GCP**: GKE, Cloud SQL, GCS, BigQuery

### On-Premises
- **Kubernetes**: Self-managed or OpenShift
- **PostgreSQL**: Self-hosted or managed
- **MinIO**: S3-compatible storage
- **Trino**: Self-hosted query engine

## Security

- **Encryption**: TLS in transit, encryption at rest
- **Authentication**: SSO (OIDC/SAML), MFA
- **Authorization**: RBAC/ABAC with policy engine
- **Audit**: All actions logged
- **Secrets**: Vault/Secrets Manager integration
- **Network**: Private VPC, security groups

## Scalability

### Horizontal Scaling
- All services are stateless (except data stores)
- Auto-scaling based on metrics
- Load balancing across instances

### Data Partitioning
- Tenant-based partitioning
- Time-based partitioning (monthly)
- Provider-based partitioning

### Caching Strategy
- Redis for session and metadata
- CDN for static assets
- Query result caching

## Related Documentation

- [Cloud-Agnostic Principles](./principles_cloud_agnostic.md)
- [Multi-Tenancy](./multi_tenancy.md)
- [Canonical Cost Schema](./canonical_cost_schema.md)
- [Authentication & Authorization](./auth_sso_rbac_abac.md)
- [Data Lake & Query](./data_lake_and_query.md)
