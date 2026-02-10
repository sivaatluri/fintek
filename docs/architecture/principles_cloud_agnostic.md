# Cloud-Agnostic Principles

## Overview

The FinOps SaaS platform is designed to run on any cloud provider or on-premises infrastructure. This document outlines the principles and patterns that enable cloud portability.

## Core Principles

### 1. Abstraction Layers

Create provider-neutral abstractions for all cloud services:

- **Object Storage**: S3-compatible interface (AWS S3, Azure Blob, GCS, MinIO)
- **Database**: Standard PostgreSQL (RDS, Azure Database, Cloud SQL, self-hosted)
- **Cache**: Standard Redis (ElastiCache, Azure Cache, Memorystore, self-hosted)
- **Message Queue**: Kafka API (MSK, Event Hubs, self-hosted)
- **Query Engine**: SQL interface (Athena, BigQuery, Synapse, Trino, Snowflake)

### 2. Infrastructure as Code

Use provider-agnostic IaC tools:

```
infra/terraform/
├── modules/           # Reusable, provider-agnostic modules
│   ├── network/
│   ├── database/
│   └── ...
└── providers/         # Provider-specific implementations
    ├── aws/
    ├── azure/
    ├── gcp/
    └── onprem/
```

### 3. Feature Detection

Detect available cloud features at runtime:

```typescript
interface CloudProvider {
  supportsNativeBackup(): boolean;
  supportsAutoScaling(): boolean;
  getStorageEndpoint(): string;
}

// Adapt behavior based on capabilities
if (provider.supportsNativeBackup()) {
  useNativeBackup();
} else {
  useCustomBackupSolution();
}
```

## Cloud Adapters

### Architecture

```
packages/cloud-adapters/
├── core/                    # Interfaces and base classes
│   ├── storage.interface.ts
│   ├── database.interface.ts
│   └── compute.interface.ts
├── aws/                     # AWS implementations
├── azure/                   # Azure implementations
├── gcp/                     # GCP implementations
└── datacenter/              # On-prem implementations
```

### Example: Object Storage Adapter

```typescript
// core/storage.interface.ts
export interface ObjectStorage {
  uploadFile(bucket: string, key: string, data: Buffer): Promise<void>;
  downloadFile(bucket: string, key: string): Promise<Buffer>;
  deleteFile(bucket: string, key: string): Promise<void>;
  listFiles(bucket: string, prefix?: string): Promise<string[]>;
}

// aws/s3-storage.ts
export class S3Storage implements ObjectStorage {
  async uploadFile(bucket: string, key: string, data: Buffer) {
    await this.s3Client.putObject({ Bucket: bucket, Key: key, Body: data });
  }
  // ... other methods
}

// azure/blob-storage.ts
export class BlobStorage implements ObjectStorage {
  async uploadFile(bucket: string, key: string, data: Buffer) {
    const containerClient = this.blobServiceClient.getContainerClient(bucket);
    const blockBlobClient = containerClient.getBlockBlobClient(key);
    await blockBlobClient.upload(data, data.length);
  }
  // ... other methods
}

// Factory pattern
export class StorageFactory {
  static create(provider: string): ObjectStorage {
    switch (provider) {
      case 'aws': return new S3Storage();
      case 'azure': return new BlobStorage();
      case 'gcp': return new GCSStorage();
      case 'minio': return new MinIOStorage();
      default: throw new Error(`Unknown provider: ${provider}`);
    }
  }
}
```

## Configuration Management

### Environment-Based Configuration

```typescript
// packages/config/src/cloud-config.ts
export interface CloudConfig {
  provider: 'aws' | 'azure' | 'gcp' | 'onprem';
  region: string;
  objectStorage: {
    endpoint: string;
    bucket: string;
    accessKey?: string;
    secretKey?: string;
  };
  database: {
    host: string;
    port: number;
    name: string;
    ssl: boolean;
  };
  messageQueue: {
    brokers: string[];
    type: 'kafka' | 'rabbitmq' | 'sqs' | 'pubsub';
  };
}

export function loadCloudConfig(): CloudConfig {
  const provider = process.env.CLOUD_PROVIDER || 'aws';
  return {
    provider,
    ...loadProviderSpecificConfig(provider)
  };
}
```

## Portable Query Engine

### Query Service Architecture

The Query Service provides a unified SQL interface regardless of underlying engine:

```typescript
export interface QueryEngine {
  executeQuery(sql: string, params?: any[]): Promise<QueryResult>;
  getCostEstimate(sql: string): Promise<CostEstimate>;
  getSchema(catalog: string, schema: string): Promise<TableSchema[]>;
}

// Implementations
class TrinoQueryEngine implements QueryEngine { ... }
class AthenaQueryEngine implements QueryEngine { ... }
class BigQueryEngine implements QueryEngine { ... }
class SynapseQueryEngine implements QueryEngine { ... }
class PostgresQueryEngine implements QueryEngine { ... }

// Factory
export class QueryEngineFactory {
  static create(config: QueryConfig): QueryEngine {
    switch (config.engine) {
      case 'trino': return new TrinoQueryEngine(config);
      case 'athena': return new AthenaQueryEngine(config);
      case 'bigquery': return new BigQueryEngine(config);
      case 'synapse': return new SynapseQueryEngine(config);
      case 'postgres': return new PostgresQueryEngine(config);
    }
  }
}
```

### SQL Compatibility

- Use ANSI SQL standard where possible
- Avoid provider-specific functions
- Provide compatibility layer for common functions

```typescript
// Example: Date functions
const dateFunction = {
  trino: "date_trunc('day', timestamp)",
  athena: "date_trunc('day', timestamp)",
  bigquery: "DATE(timestamp)",
  synapse: "CAST(timestamp AS DATE)",
  postgres: "DATE_TRUNC('day', timestamp)"
};

function buildDateQuery(engine: string): string {
  return `SELECT ${dateFunction[engine]} as usage_date FROM costs`;
}
```

## Data Lake Portability

### Unified Storage Format

Use open formats that work everywhere:

- **Parquet**: Columnar storage, wide support
- **Avro**: Row-based with schema evolution
- **JSON/JSONL**: Human-readable fallback

### Partitioning Strategy

Provider-agnostic partitioning:

```
s3://bucket/costs/
  tenant_id=abc123/
    provider=aws/
      year=2026/
        month=02/
          day=10/
            data.parquet
```

Works identically on:
- AWS S3: `s3://bucket/costs/...`
- Azure Blob: `https://account.blob.core.windows.net/bucket/costs/...`
- GCS: `gs://bucket/costs/...`
- MinIO: `http://minio:9000/bucket/costs/...`

## Container Portability

### Docker Images

Build once, run anywhere:

```dockerfile
# Base image
FROM node:18-alpine AS base
WORKDIR /app

# Dependencies
COPY package*.json ./
RUN npm ci --only=production

# Application
COPY dist ./dist
CMD ["node", "dist/main.js"]
```

### Kubernetes Deployment

Use standard Kubernetes manifests:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gateway-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: gateway-api
        image: finops/gateway-api:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
```

Works on:
- Amazon EKS
- Azure AKS
- Google GKE
- Self-managed Kubernetes
- OpenShift

## Secrets Management

### Unified Secrets Interface

```typescript
export interface SecretsManager {
  getSecret(key: string): Promise<string>;
  setSecret(key: string, value: string): Promise<void>;
  deleteSecret(key: string): Promise<void>;
}

// Implementations
class VaultSecretsManager implements SecretsManager { ... }
class AWSSecretsManager implements SecretsManager { ... }
class AzureKeyVault implements SecretsManager { ... }
class GCPSecretManager implements SecretsManager { ... }
```

## Cost Provider Abstraction

### Unified Cost Interface

All cloud provider cost data is normalized to a canonical schema:

```typescript
export interface CostRecord {
  tenant_id: string;
  provider: 'aws' | 'azure' | 'gcp' | 'oracle' | 'akamai' | 'datacenter';
  account_id: string;
  service: string;
  region: string;
  usage_date: Date;
  cost: number;
  currency: string;
  tags: Record<string, string>;
  resource_id?: string;
  // ... normalized fields
}
```

### Provider Connectors

Each provider has a dedicated connector that transforms native format to canonical schema:

- **AWS**: CUR (Cost and Usage Report) → Canonical
- **Azure**: EA/MCA Export → Canonical
- **GCP**: Billing Export → Canonical
- **Oracle**: Cost Reports → Canonical
- **Data Center**: CSV/API → Canonical

## Deployment Strategies

### Multi-Cloud Deployment

Deploy the same codebase across clouds:

```bash
# Deploy to AWS
cd infra/terraform/providers/aws
terraform apply

# Deploy to Azure
cd infra/terraform/providers/azure
terraform apply

# Deploy to GCP
cd infra/terraform/providers/gcp
terraform apply
```

### Hybrid Deployment

Control plane in cloud, data plane on-prem:

```
┌─────────────────────────────┐
│         Cloud (AWS)         │
│  ┌────────┐  ┌────────┐    │
│  │ Web UI │  │  APIs  │    │
│  └────────┘  └────────┘    │
└──────────────┬──────────────┘
               │ HTTPS
┌──────────────▼──────────────┐
│       On-Premises           │
│  ┌────────┐  ┌────────┐    │
│  │  Data  │  │ Query  │    │
│  │  Lake  │  │ Engine │    │
│  └────────┘  └────────┘    │
└─────────────────────────────┘
```

## Testing Portability

### Local Development

Use portable tools for local dev:

- **MinIO** instead of S3
- **PostgreSQL** instead of managed DB
- **Kafka** instead of managed queue
- **Trino** instead of cloud query engines

### Integration Tests

Test against multiple backends:

```typescript
describe('ObjectStorage', () => {
  const backends = ['s3', 'azure-blob', 'gcs', 'minio'];
  
  backends.forEach(backend => {
    describe(`with ${backend}`, () => {
      it('should upload and download files', async () => {
        const storage = StorageFactory.create(backend);
        // ... test implementation
      });
    });
  });
});
```

## Best Practices

1. **Use abstractions**: Always code against interfaces, not implementations
2. **Feature flags**: Use flags for provider-specific features
3. **Graceful degradation**: Fall back to alternative approaches
4. **Configuration**: Make everything configurable
5. **Documentation**: Document provider differences
6. **Testing**: Test on multiple providers
7. **Monitoring**: Track provider-specific metrics

## Migration Path

### From Single Cloud to Multi-Cloud

1. **Phase 1**: Introduce abstraction layer
2. **Phase 2**: Implement alternative providers
3. **Phase 3**: Add configuration management
4. **Phase 4**: Test on target platforms
5. **Phase 5**: Deploy to new platform
6. **Phase 6**: Migrate data (if needed)

## Conclusion

By following these cloud-agnostic principles, the FinOps SaaS platform can run on any infrastructure, giving customers deployment flexibility and avoiding vendor lock-in.
