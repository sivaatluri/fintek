import {
  Kafka,
  Consumer,
  ConsumerConfig,
  ConsumerSubscribeTopics,
  EachMessagePayload,
  EachBatchPayload,
} from 'kafkajs';

export interface EventConsumerConfig {
  clientId: string;
  brokers: string[];
  groupId: string;
  ssl?: boolean;
  sasl?: {
    mechanism: 'plain' | 'scram-sha-256' | 'scram-sha-512';
    username: string;
    password: string;
  };
  fromBeginning?: boolean;
  maxRetries?: number;
  retryDelay?: number;
}

export type MessageHandler<T = any> = (
  message: T,
  metadata: MessageMetadata
) => Promise<void>;

export interface MessageMetadata {
  topic: string;
  partition: number;
  offset: string;
  key?: string;
  headers?: Record<string, string>;
  timestamp: string;
}

/**
 * Event consumer with retry and DLQ pattern
 */
export class EventConsumer {
  private kafka: Kafka;
  private consumer: Consumer;
  private handlers: Map<string, MessageHandler> = new Map();
  private maxRetries: number;
  private retryDelay: number;
  private connected: boolean = false;
  private fromBeginning: boolean;

  constructor(config: EventConsumerConfig) {
    this.kafka = new Kafka({
      clientId: config.clientId,
      brokers: config.brokers,
      ssl: config.ssl,
      sasl: config.sasl,
    });

    const consumerConfig: ConsumerConfig = {
      groupId: config.groupId,
      retry: {
        retries: config.maxRetries || 5,
        initialRetryTime: config.retryDelay || 300,
      },
    };

    this.consumer = this.kafka.consumer(consumerConfig);
    this.maxRetries = config.maxRetries || 3;
    this.retryDelay = config.retryDelay || 1000;
    this.fromBeginning = config.fromBeginning || false;
  }

  /**
   * Register a message handler for a topic
   */
  on<T = any>(topic: string, handler: MessageHandler<T>): void {
    this.handlers.set(topic, handler);
  }

  /**
   * Connect and start consuming
   */
  async start(topics: string[]): Promise<void> {
    await this.consumer.connect();
    this.connected = true;

    const subscribeTopics: ConsumerSubscribeTopics = {
      topics,
      fromBeginning: this.fromBeginning,
    };

    await this.consumer.subscribe(subscribeTopics);

    await this.consumer.run({
      eachMessage: async (payload: EachMessagePayload) => {
        await this.handleMessage(payload);
      },
    });
  }

  /**
   * Stop consuming and disconnect
   */
  async stop(): Promise<void> {
    if (this.connected) {
      await this.consumer.disconnect();
      this.connected = false;
    }
  }

  /**
   * Handle incoming message with retry logic
   */
  private async handleMessage(
    payload: EachMessagePayload,
    attempt: number = 1
  ): Promise<void> {
    const { topic, partition, message } = payload;
    
    try {
      // Get handler for topic
      const handler = this.handlers.get(topic);
      if (!handler) {
        console.warn(`No handler registered for topic: ${topic}`);
        return;
      }

      // Parse message
      const value = message.value ? JSON.parse(message.value.toString()) : null;
      const key = message.key?.toString();
      const headers = this.parseHeaders(message.headers);

      const metadata: MessageMetadata = {
        topic,
        partition,
        offset: message.offset,
        key,
        headers,
        timestamp: message.timestamp,
      };

      // Execute handler
      await handler(value, metadata);

      // Commit offset
      await this.consumer.commitOffsets([
        {
          topic,
          partition,
          offset: (parseInt(message.offset) + 1).toString(),
        },
      ]);
    } catch (error) {
      console.error(`Error processing message from ${topic}:`, error);

      // Check if we should retry
      if (attempt < this.maxRetries) {
        // Exponential backoff
        const delay = this.retryDelay * Math.pow(2, attempt - 1);
        await this.sleep(delay);
        await this.handleMessage(payload, attempt + 1);
      } else {
        // Max retries reached, send to DLQ
        await this.sendToDLQ(payload, error);
        
        // Commit offset to move on
        await this.consumer.commitOffsets([
          {
            topic,
            partition,
            offset: (parseInt(payload.message.offset) + 1).toString(),
          },
        ]);
      }
    }
  }

  /**
   * Send failed message to Dead Letter Queue
   */
  private async sendToDLQ(payload: EachMessagePayload, error: any): Promise<void> {
    const { topic, partition, message } = payload;
    const dlqTopic = `${topic}.dlq`;

    try {
      const producer = this.kafka.producer();
      await producer.connect();

      await producer.send({
        topic: dlqTopic,
        messages: [
          {
            key: message.key,
            value: message.value,
            headers: {
              ...message.headers,
              'x-original-topic': topic,
              'x-original-partition': partition.toString(),
              'x-original-offset': message.offset,
              'x-error': error.message || 'Unknown error',
              'x-failed-at': new Date().toISOString(),
              'x-retry-count': this.maxRetries.toString(),
            },
          },
        ],
      });

      await producer.disconnect();
      console.log(`Message sent to DLQ: ${dlqTopic}`);
    } catch (dlqError) {
      console.error('Failed to send message to DLQ:', dlqError);
    }
  }

  /**
   * Parse Kafka headers
   */
  private parseHeaders(headers: any): Record<string, string> {
    if (!headers) return {};
    
    const parsed: Record<string, string> = {};
    for (const [key, value] of Object.entries(headers)) {
      if (Buffer.isBuffer(value)) {
        parsed[key] = value.toString();
      }
    }
    return parsed;
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Check if consumer is connected
   */
  isConnected(): boolean {
    return this.connected;
  }
}
