# FinOps Platform - Shared Packages

This directory contains shared libraries used across all FinOps platform services.

## Packages

### [@finops/common](./common)
Common utilities including custom errors, request context management, and org/tenant ID tracking.

**Features:**
- Custom error classes (BadRequest, Unauthorized, Forbidden, NotFound, etc.)
- AsyncLocalStorage-based request context
- Request ID, organization ID, tenant ID, and user ID tracking
- Express middleware for context initialization

**Installation:**
```bash
npm install @finops/common
```

**Usage:**
```typescript
import { BadRequestError, getRequestId, contextMiddleware } from '@finops/common';

// Express middleware
app.use(contextMiddleware());

// In handlers
const requestId = getRequestId();
throw new BadRequestError('Invalid input', { field: 'email' });
```

---

### [@finops/config](./config)
Environment configuration management with type-safe validation using Zod.

**Features:**
- Environment variable loading with dotenv
- Zod schema validation
- Type-safe configuration access
- Support for database, Redis, Kafka, telemetry, auth, CORS, and rate limiting configs

**Installation:**
```bash
npm install @finops/config
```

**Usage:**
```typescript
import { loadConfig } from '@finops/config';

const config = loadConfig();
console.log(config.database.host); // Type-safe access
```

---

### [@finops/telemetry](./telemetry)
OpenTelemetry integration for logging and distributed tracing.

**Features:**
- OpenTelemetry SDK initialization
- Pino logger with automatic trace context injection
- Tracing helpers (withSpan, decorators)
- Automatic instrumentation for Node.js libraries

**Installation:**
```bash
npm install @finops/telemetry
```

**Usage:**
```typescript
import { initializeTelemetry, createLogger, withSpan } from '@finops/telemetry';

// Initialize once at startup
initializeTelemetry({
  serviceName: 'my-service',
  serviceVersion: '1.0.0',
  otlpEndpoint: 'http://localhost:4318',
});

// Create logger
const logger = createLogger({ level: 'info' });
logger.info('Service started');

// Tracing
await withSpan('process-data', async (span) => {
  span.setAttribute('records', 100);
  // Your code here
});
```

---

### [@finops/policy-engine](./policy-engine)
RBAC (Role-Based Access Control) and ABAC (Attribute-Based Access Control) policy engine.

**Features:**
- Predefined roles and permissions
- Policy evaluation engine
- RBAC and ABAC policy creators
- Express middleware and decorators for authorization

**Installation:**
```bash
npm install @finops/policy-engine
```

**Usage:**
```typescript
import { 
  PolicyEngine, 
  Role, 
  Permission, 
  requirePermission 
} from '@finops/policy-engine';

// Express middleware
app.get('/budgets', 
  requirePermission(Permission['budgets:read']),
  (req, res) => {
    // Handler
  }
);

// Policy engine
const engine = new PolicyEngine();
const allowed = engine.hasPermission(context, Permission['costs:write']);
```

---

### [@finops/event-bus](./event-bus)
Kafka producer/consumer wrappers with retry logic and Dead Letter Queue (DLQ) pattern.

**Features:**
- Kafka producer with automatic retry
- Kafka consumer with message handling
- Dead Letter Queue (DLQ) for failed messages
- Batch message support
- Automatic offset management

**Installation:**
```bash
npm install @finops/event-bus
```

**Usage:**
```typescript
import { EventProducer, EventConsumer } from '@finops/event-bus';

// Producer
const producer = new EventProducer({
  clientId: 'my-service',
  brokers: ['localhost:9092'],
});

await producer.send('my-topic', {
  key: 'event-key',
  value: { data: 'my-data' },
});

// Consumer
const consumer = new EventConsumer({
  clientId: 'my-service',
  brokers: ['localhost:9092'],
  groupId: 'my-group',
});

consumer.on('my-topic', async (message, metadata) => {
  console.log('Received:', message);
});

await consumer.start(['my-topic']);
```

---

## Development

### Building All Packages

```bash
# From packages directory
for dir in */; do
  cd "$dir"
  npm install
  npm run build
  cd ..
done
```

### Running Tests

```bash
# Test all packages
for dir in */; do
  cd "$dir"
  npm test
  cd ..
done

# Or with coverage
for dir in */; do
  cd "$dir"
  npm run test:coverage
  cd ..
done
```

### Package Structure

Each package follows this structure:
```
package-name/
├── src/
│   ├── index.ts          # Main entry point
│   ├── *.ts              # Source files
│   └── *.test.ts         # Test files
├── dist/                 # Compiled output (gitignored)
├── package.json
├── tsconfig.json
└── jest.config.js
```

## TypeScript Configuration

All packages use:
- TypeScript 5.0+
- Target: ES2020
- Strict mode enabled
- CommonJS modules
- Declaration files generated

## Testing

All packages use:
- Jest for unit testing
- ts-jest for TypeScript support
- Coverage thresholds: 70-80%

## Publishing

```bash
# Build and test before publishing
npm run build
npm test

# Publish to npm (requires authentication)
npm publish --access public
```

## License

MIT
