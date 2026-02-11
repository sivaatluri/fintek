import { EventProducer, EventMessage } from '../producer';

// Mock kafkajs
jest.mock('kafkajs', () => {
  const mockSend = jest.fn().mockResolvedValue([
    { topicName: 'test-topic', partition: 0, errorCode: 0, offset: '0' }
  ]);
  
  const mockProducer = {
    connect: jest.fn().mockResolvedValue(undefined),
    disconnect: jest.fn().mockResolvedValue(undefined),
    send: mockSend,
  };

  return {
    Kafka: jest.fn(() => ({
      producer: jest.fn(() => mockProducer),
    })),
  };
});

describe('EventProducer', () => {
  let producer: EventProducer;

  beforeEach(() => {
    producer = new EventProducer({
      clientId: 'test-client',
      brokers: ['localhost:9092'],
      retries: 3,
      retryDelay: 100,
    });
  });

  afterEach(async () => {
    await producer.disconnect();
  });

  describe('send', () => {
    it('should send a single message', async () => {
      const message: EventMessage = {
        key: 'test-key',
        value: { data: 'test-data' },
      };

      const result = await producer.send('test-topic', message);
      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
    });

    it('should send message without key', async () => {
      const message: EventMessage = {
        value: { data: 'test-data' },
      };

      const result = await producer.send('test-topic', message);
      expect(result).toBeDefined();
    });

    it('should send message with headers', async () => {
      const message: EventMessage = {
        value: { data: 'test-data' },
        headers: {
          'x-request-id': 'req-123',
        },
      };

      const result = await producer.send('test-topic', message);
      expect(result).toBeDefined();
    });
  });

  describe('sendBatch', () => {
    it('should send multiple messages', async () => {
      const messages: EventMessage[] = [
        { key: 'key1', value: { data: 'data1' } },
        { key: 'key2', value: { data: 'data2' } },
        { key: 'key3', value: { data: 'data3' } },
      ];

      const result = await producer.sendBatch('test-topic', messages);
      expect(result).toBeDefined();
    });
  });

  describe('connect/disconnect', () => {
    it('should connect to Kafka', async () => {
      await producer.connect();
      // Should not throw
    });

    it('should disconnect from Kafka', async () => {
      await producer.connect();
      await producer.disconnect();
      // Should not throw
    });
  });
});
