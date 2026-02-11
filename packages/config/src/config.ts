import { z } from 'zod';
import * as dotenv from 'dotenv';

/**
 * Configuration schema using Zod for validation
 */
export const configSchema = z.object({
  // Environment
  nodeEnv: z.enum(['development', 'test', 'staging', 'production']).default('development'),
  port: z.coerce.number().int().positive().default(3000),
  
  // Database
  database: z.object({
    host: z.string().default('localhost'),
    port: z.coerce.number().int().positive().default(5432),
    name: z.string().default('finops'),
    user: z.string().default('finops'),
    password: z.string().default('finops'),
    ssl: z.boolean().default(false),
    poolMin: z.coerce.number().int().nonnegative().default(2),
    poolMax: z.coerce.number().int().positive().default(10),
  }),
  
  // Redis
  redis: z.object({
    host: z.string().default('localhost'),
    port: z.coerce.number().int().positive().default(6379),
    password: z.string().optional(),
    db: z.coerce.number().int().nonnegative().default(0),
    keyPrefix: z.string().default('finops:'),
  }),
  
  // Kafka
  kafka: z.object({
    brokers: z.string().transform(str => str.split(',')).default('localhost:9092'),
    clientId: z.string().default('finops'),
    groupId: z.string().default('finops-group'),
    ssl: z.boolean().default(false),
    saslMechanism: z.enum(['plain', 'scram-sha-256', 'scram-sha-512']).optional(),
    saslUsername: z.string().optional(),
    saslPassword: z.string().optional(),
  }),
  
  // OpenTelemetry
  telemetry: z.object({
    enabled: z.boolean().default(true),
    serviceName: z.string().default('finops-service'),
    serviceVersion: z.string().default('1.0.0'),
    otlpEndpoint: z.string().default('http://localhost:4318'),
    samplingRate: z.coerce.number().min(0).max(1).default(1.0),
    logLevel: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  }),
  
  // Authentication
  auth: z.object({
    jwtSecret: z.string().default('change-me-in-production'),
    jwtExpiresIn: z.string().default('1h'),
    bcryptRounds: z.coerce.number().int().positive().default(10),
    sessionSecret: z.string().default('change-me-in-production'),
  }),
  
  // CORS
  cors: z.object({
    enabled: z.boolean().default(true),
    origin: z.string().or(z.array(z.string())).default('*'),
    credentials: z.boolean().default(true),
  }),
  
  // Rate Limiting
  rateLimit: z.object({
    enabled: z.boolean().default(true),
    windowMs: z.coerce.number().int().positive().default(15 * 60 * 1000), // 15 minutes
    maxRequests: z.coerce.number().int().positive().default(100),
  }),
});

export type Config = z.infer<typeof configSchema>;

/**
 * Load configuration from environment variables
 */
export function loadConfig(envPath?: string): Config {
  // Load .env file if specified
  if (envPath) {
    dotenv.config({ path: envPath });
  } else {
    dotenv.config();
  }

  const rawConfig = {
    nodeEnv: process.env.NODE_ENV,
    port: process.env.PORT,
    
    database: {
      host: process.env.DB_HOST,
      port: process.env.DB_PORT,
      name: process.env.DB_NAME,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      ssl: process.env.DB_SSL === 'true',
      poolMin: process.env.DB_POOL_MIN,
      poolMax: process.env.DB_POOL_MAX,
    },
    
    redis: {
      host: process.env.REDIS_HOST,
      port: process.env.REDIS_PORT,
      password: process.env.REDIS_PASSWORD,
      db: process.env.REDIS_DB,
      keyPrefix: process.env.REDIS_KEY_PREFIX,
    },
    
    kafka: {
      brokers: process.env.KAFKA_BROKERS,
      clientId: process.env.KAFKA_CLIENT_ID,
      groupId: process.env.KAFKA_GROUP_ID,
      ssl: process.env.KAFKA_SSL === 'true',
      saslMechanism: process.env.KAFKA_SASL_MECHANISM,
      saslUsername: process.env.KAFKA_SASL_USERNAME,
      saslPassword: process.env.KAFKA_SASL_PASSWORD,
    },
    
    telemetry: {
      enabled: process.env.TELEMETRY_ENABLED !== 'false',
      serviceName: process.env.TELEMETRY_SERVICE_NAME,
      serviceVersion: process.env.TELEMETRY_SERVICE_VERSION,
      otlpEndpoint: process.env.OTLP_ENDPOINT,
      samplingRate: process.env.TELEMETRY_SAMPLING_RATE,
      logLevel: process.env.LOG_LEVEL,
    },
    
    auth: {
      jwtSecret: process.env.JWT_SECRET,
      jwtExpiresIn: process.env.JWT_EXPIRES_IN,
      bcryptRounds: process.env.BCRYPT_ROUNDS,
      sessionSecret: process.env.SESSION_SECRET,
    },
    
    cors: {
      enabled: process.env.CORS_ENABLED !== 'false',
      origin: process.env.CORS_ORIGIN,
      credentials: process.env.CORS_CREDENTIALS !== 'false',
    },
    
    rateLimit: {
      enabled: process.env.RATE_LIMIT_ENABLED !== 'false',
      windowMs: process.env.RATE_LIMIT_WINDOW_MS,
      maxRequests: process.env.RATE_LIMIT_MAX_REQUESTS,
    },
  };

  try {
    return configSchema.parse(rawConfig);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const formattedErrors = error.errors.map(err => 
        `${err.path.join('.')}: ${err.message}`
      ).join('\n');
      throw new Error(`Configuration validation failed:\n${formattedErrors}`);
    }
    throw error;
  }
}

/**
 * Validate configuration without loading
 */
export function validateConfig(config: unknown): Config {
  return configSchema.parse(config);
}

/**
 * Get configuration value by path
 */
export function getConfigValue<T>(config: Config, path: string): T {
  const keys = path.split('.');
  let value: any = config;
  
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key as keyof typeof value];
    } else {
      throw new Error(`Configuration path not found: ${path}`);
    }
  }
  
  return value as T;
}
