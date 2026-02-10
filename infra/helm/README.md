# Helm Charts

This directory contains Kubernetes Helm charts for deploying the FinOps SaaS platform.

## Available Charts

- `gateway-api`: API Gateway service
- `auth-service`: Authentication service
- `tenant-service`: Tenant management service
- `cost-pipeline`: Cost data ingestion and processing
- `workflows`: Workflow engine
- `query-service`: Query service
- `web`: Web application
- `admin-portal`: Admin portal

## Prerequisites

- Kubernetes 1.24+
- Helm 3.0+
- kubectl configured

## Installation

### Install entire platform

```bash
# Add Helm repository (if published)
helm repo add finops https://charts.finops.example.com
helm repo update

# Install with custom values
helm install finops finops/finops-platform \
  --namespace finops \
  --create-namespace \
  --values values/production.yaml
```

### Install individual chart

```bash
cd charts/gateway-api
helm install gateway-api . \
  --namespace finops \
  --values values.yaml
```

## Configuration

### Common Values

```yaml
# values.yaml
global:
  domain: finops.example.com
  environment: production
  
  image:
    registry: docker.io
    pullPolicy: IfNotPresent
  
  database:
    host: postgres.finops.svc.cluster.local
    port: 5432
    name: finops_db
  
  redis:
    host: redis.finops.svc.cluster.local
    port: 6379
  
  ingress:
    enabled: true
    className: nginx
    tls:
      enabled: true
```

### Service-Specific Values

Each chart has its own `values.yaml` with service-specific configuration.

## Deployment

### Development

```bash
helm install finops . \
  --namespace finops-dev \
  --values values/dev.yaml
```

### Production

```bash
helm install finops . \
  --namespace finops \
  --values values/prod.yaml
```

## Upgrade

```bash
helm upgrade finops . \
  --namespace finops \
  --values values/prod.yaml
```

## Rollback

```bash
helm rollback finops [REVISION] --namespace finops
```

## Uninstall

```bash
helm uninstall finops --namespace finops
```

## Chart Development

### Lint

```bash
helm lint charts/gateway-api
```

### Template

```bash
helm template finops charts/gateway-api \
  --values values/dev.yaml \
  --debug
```

### Package

```bash
helm package charts/gateway-api
```

## Monitoring

All charts include:
- Prometheus metrics endpoints
- Health check endpoints
- Liveness and readiness probes
- Resource requests and limits

## Security

- Non-root containers
- Read-only root filesystem
- Pod security policies
- Network policies
- Secret management via external secrets operator

See [infrastructure docs](/docs/architecture/) for more details.
