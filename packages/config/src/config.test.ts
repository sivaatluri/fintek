import { loadConfig, validateConfig, getConfigValue, Config } from '../config';

describe('Config', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  describe('loadConfig', () => {
    it('should load config with defaults', () => {
      const config = loadConfig();
      
      expect(config.nodeEnv).toBe('development');
      expect(config.port).toBe(3000);
      expect(config.database.host).toBe('localhost');
      expect(config.redis.port).toBe(6379);
      expect(config.telemetry.enabled).toBe(true);
    });

    it('should load config from environment variables', () => {
      process.env.NODE_ENV = 'production';
      process.env.PORT = '8080';
      process.env.DB_HOST = 'db.example.com';
      process.env.REDIS_PORT = '6380';
      
      const config = loadConfig();
      
      expect(config.nodeEnv).toBe('production');
      expect(config.port).toBe(8080);
      expect(config.database.host).toBe('db.example.com');
      expect(config.redis.port).toBe(6380);
    });

    it('should parse Kafka brokers as array', () => {
      process.env.KAFKA_BROKERS = 'broker1:9092,broker2:9092,broker3:9092';
      
      const config = loadConfig();
      
      expect(config.kafka.brokers).toEqual(['broker1:9092', 'broker2:9092', 'broker3:9092']);
    });

    it('should convert string booleans correctly', () => {
      process.env.DB_SSL = 'true';
      process.env.KAFKA_SSL = 'true';
      process.env.TELEMETRY_ENABLED = 'false';
      
      const config = loadConfig();
      
      expect(config.database.ssl).toBe(true);
      expect(config.kafka.ssl).toBe(true);
      expect(config.telemetry.enabled).toBe(false);
    });

    it('should throw on invalid configuration', () => {
      process.env.PORT = 'not-a-number';
      
      expect(() => loadConfig()).toThrow('Configuration validation failed');
    });
  });

  describe('validateConfig', () => {
    it('should validate correct config', () => {
      const validConfig = {
        nodeEnv: 'production' as const,
        port: 3000,
        database: {
          host: 'localhost',
          port: 5432,
          name: 'finops',
          user: 'finops',
          password: 'secret',
          ssl: false,
          poolMin: 2,
          poolMax: 10,
        },
        redis: {
          host: 'localhost',
          port: 6379,
          db: 0,
          keyPrefix: 'finops:',
        },
        kafka: {
          brokers: ['localhost:9092'],
          clientId: 'finops',
          groupId: 'finops-group',
          ssl: false,
        },
        telemetry: {
          enabled: true,
          serviceName: 'test-service',
          serviceVersion: '1.0.0',
          otlpEndpoint: 'http://localhost:4318',
          samplingRate: 1.0,
          logLevel: 'info' as const,
        },
        auth: {
          jwtSecret: 'secret',
          jwtExpiresIn: '1h',
          bcryptRounds: 10,
          sessionSecret: 'session-secret',
        },
        cors: {
          enabled: true,
          origin: '*',
          credentials: true,
        },
        rateLimit: {
          enabled: true,
          windowMs: 900000,
          maxRequests: 100,
        },
      };
      
      expect(() => validateConfig(validConfig)).not.toThrow();
    });

    it('should reject invalid config', () => {
      const invalidConfig = {
        nodeEnv: 'invalid',
        port: -1,
      };
      
      expect(() => validateConfig(invalidConfig)).toThrow();
    });
  });

  describe('getConfigValue', () => {
    it('should get nested config value', () => {
      const config = loadConfig();
      
      const dbHost = getConfigValue<string>(config, 'database.host');
      expect(dbHost).toBe('localhost');
      
      const redisPort = getConfigValue<number>(config, 'redis.port');
      expect(redisPort).toBe(6379);
    });

    it('should throw on invalid path', () => {
      const config = loadConfig();
      
      expect(() => getConfigValue(config, 'invalid.path')).toThrow('Configuration path not found');
    });
  });
});
