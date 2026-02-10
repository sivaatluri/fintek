# Fintek - Multi-Tenant FinOps SaaS Platform

A modular, scalable FinOps (Financial Operations) platform built with modern microservices architecture.

## 🏗️ Architecture

Fintek is a monorepo containing multiple microservices, packages, and applications:

### Services
- **Gateway** (Port 8000) - API Gateway and routing
- **Auth** (Port 8001) - Authentication and authorization
- **Tenant** (Port 8002) - Multi-tenant management
- **Ingestion** (Port 8003) - Cost data ingestion and processing
- **Workflows** (Port 8004) - Workflow orchestration
- **Budgets** (Port 8005) - Budget management and alerting
- **Query** (Port 8006) - Query execution with Trino
- **Integrations** (Port 8007) - Cloud provider integrations

### Frontend
- **Web** (Port 3000) - React + TypeScript dashboard

### Infrastructure
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Kafka** - Event streaming
- **Trino** - Distributed SQL query engine
- **MinIO** - Object storage

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.11+ (for backend development)

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/sivaatluri/fintek.git
cd fintek
```

2. Start all services:
```bash
docker-compose up -d
```

3. Check service health:
```bash
# Gateway
curl http://localhost:8000/health

# Individual services
curl http://localhost:8001/health  # Auth
curl http://localhost:8002/health  # Tenant
curl http://localhost:8003/health  # Ingestion
curl http://localhost:8004/health  # Workflows
curl http://localhost:8005/health  # Budgets
curl http://localhost:8006/health  # Query
curl http://localhost:8007/health  # Integrations
```

4. Access the web dashboard:
```bash
cd apps/web
npm install
npm run dev
```
Visit http://localhost:5173

## 📁 Repository Structure

```
fintek/
├── services/           # Microservices
│   ├── gateway/
│   ├── auth/
│   ├── tenant/
│   ├── ingestion/
│   ├── workflows/
│   ├── budgets/
│   ├── query/
│   └── integrations/
├── packages/           # Shared packages
│   ├── common-schemas/
│   ├── rbac/
│   └── db-utils/
├── apps/              # Frontend applications
│   └── web/
├── connectors/        # External connectors (future)
├── data/             # Data schemas and migrations
├── infra/            # Infrastructure configuration
├── scripts/          # Utility scripts
├── tools/            # Development tools
├── docs/             # Documentation
└── docker-compose.yml
```

## 🔧 Development

### Service Development

Each service is a standalone FastAPI application:

```bash
cd services/gateway
pip install -e .
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd apps/web
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd services/gateway
pytest

# Frontend tests
cd apps/web
npm test
```

## 📊 Features

### Core Capabilities
- ✅ Multi-tenant architecture with tenant isolation
- ✅ Cost data ingestion from multiple cloud providers
- ✅ Real-time budget tracking and alerting
- ✅ Cloud provider integrations (AWS, Azure, GCP)
- ✅ Workflow orchestration for automation
- ✅ SQL query interface with Trino
- ✅ RBAC (Role-Based Access Control) placeholders
- ✅ Health check endpoints for all services
- ✅ Event-driven architecture with Kafka

### Schemas
- **Cost Records** - Canonical cost data schema
- **Events** - Platform-wide event schema
- **Tenants** - Multi-tenant configuration

## 🔐 Security

- RBAC placeholders implemented in `/packages/rbac`
- JWT-based authentication (placeholder in auth service)
- Tenant isolation at database and application level
- API Gateway for centralized access control

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database access
- **Pydantic** - Data validation
- **asyncpg** - Async PostgreSQL driver

### Frontend
- **React** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool

### Infrastructure
- **PostgreSQL** - Relational database
- **Redis** - Cache and session store
- **Kafka** - Event streaming
- **Trino** - Query engine
- **MinIO** - S3-compatible object storage

## 📝 API Documentation

Once services are running, access API documentation:

- Gateway: http://localhost:8000/docs
- Auth: http://localhost:8001/docs
- Tenant: http://localhost:8002/docs
- Ingestion: http://localhost:8003/docs
- Workflows: http://localhost:8004/docs
- Budgets: http://localhost:8005/docs
- Query: http://localhost:8006/docs
- Integrations: http://localhost:8007/docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🎯 Roadmap

- [ ] Complete authentication implementation
- [ ] Add cloud provider connectors
- [ ] Implement anomaly detection
- [ ] Add data visualization dashboards
- [ ] Implement cost optimization recommendations
- [ ] Add multi-cloud cost comparison
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipelines

## 📞 Support

For issues and questions, please open a GitHub issue.