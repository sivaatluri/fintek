import { EventConsumer, MessageHandler } from '../consumer';

// Mock kafkajs
jest.mock('kafkajs', () => {
  const mockConsumer = {
    connect: jest.fn().mockResolvedValue(undefined),
    disconnect: jest.fn().mockResolvedValue(undefined),
    subscribe: jest.fn().mockResolvedValue(undefined),
    run: jest.fn().mockResolvedValue(undefined),
    commitOffsets: jest.fn().mockResolvedValue(undefined),
  };

  return {
    Kafka: jest.fn(() => ({
      consumer: jest.fn(() => mockConsumer),
      producer: jest.fn(() => ({
        connect: jest.fn().mockResolvedValue(undefined),
        send: jest.fn().mockResolvedValue([]),
        disconnect: jest.fn().mockResolvedValue(undefined),
      })),
    })),
  };
});

describe('EventConsumer', () => {
  let consumer: EventConsumer;

  beforeEach(() => {
    consumer = new EventConsumer({
      clientId: 'test-client',
      brokers: ['localhost:9092'],
      groupId: 'test-group',
      maxRetries: 3,
      retryDelay: 100,
    });
  });

  afterEach(async () => {
    await consumer.stop();
  });

  describe('on', () => {
    it('should register a message handler', () => {
      const handler: MessageHandler = async (message, metadata) => {
        console.log('Handling message:', message);
      };

      consumer.on('test-topic', handler);
      // Should not throw
    });
  });

  describe('start', () => {
    it('should start consuming messages', async () => {
      const handler: MessageHandler = jest.fn().mockResolvedValue(undefined);
      consumer.on('test-topic', handler);

      await consumer.start(['test-topic']);
      expect(consumer.isConnected()).toBe(true);
    });
  });

  describe('stop', () => {
    it('should stop consuming and disconnect', async () => {
      await consumer.start(['test-topic']);
      await consumer.stop();
      expect(consumer.isConnected()).toBe(false);
    });
  });

  describe('isConnected', () => {
    it('should return false initially', () => {
      expect(consumer.isConnected()).toBe(false);
    });

    it('should return true after starting', async () => {
      await consumer.start(['test-topic']);
      expect(consumer.isConnected()).toBe(true);
    });
  });
});
