import { Kafka, Producer, ProducerRecord, ProducerBatch, Message, RecordMetadata } from 'kafkajs';

export interface EventProducerConfig {
  clientId: string;
  brokers: string[];
  ssl?: boolean;
  sasl?: {
    mechanism: 'plain' | 'scram-sha-256' | 'scram-sha-512';
    username: string;
    password: string;
  };
  retries?: number;
  retryDelay?: number;
}

export interface EventMessage<T = any> {
  key?: string;
  value: T;
  headers?: Record<string, string>;
  partition?: number;
  timestamp?: string;
}

/**
 * Event producer with retry logic
 */
export class EventProducer {
  private kafka: Kafka;
  private producer: Producer;
  private retries: number;
  private retryDelay: number;
  private connected: boolean = false;

  constructor(config: EventProducerConfig) {
    this.kafka = new Kafka({
      clientId: config.clientId,
      brokers: config.brokers,
      ssl: config.ssl,
      sasl: config.sasl,
      retry: {
        retries: config.retries || 5,
        initialRetryTime: config.retryDelay || 300,
      },
    });

    this.producer = this.kafka.producer();
    this.retries = config.retries || 5;
    this.retryDelay = config.retryDelay || 300;
  }

  /**
   * Connect to Kafka
   */
  async connect(): Promise<void> {
    if (!this.connected) {
      await this.producer.connect();
      this.connected = true;
    }
  }

  /**
   * Disconnect from Kafka
   */
  async disconnect(): Promise<void> {
    if (this.connected) {
      await this.producer.disconnect();
      this.connected = false;
    }
  }

  /**
   * Send a single event
   */
  async send<T = any>(
    topic: string,
    message: EventMessage<T>
  ): Promise<RecordMetadata[]> {
    await this.connect();

    const kafkaMessage: Message = {
      key: message.key ? Buffer.from(message.key) : undefined,
      value: Buffer.from(JSON.stringify(message.value)),
      headers: message.headers,
      partition: message.partition,
      timestamp: message.timestamp,
    };

    const record: ProducerRecord = {
      topic,
      messages: [kafkaMessage],
    };

    return await this.sendWithRetry(record);
  }

  /**
   * Send multiple events in a batch
   */
  async sendBatch<T = any>(
    topic: string,
    messages: EventMessage<T>[]
  ): Promise<RecordMetadata[]> {
    await this.connect();

    const kafkaMessages: Message[] = messages.map(msg => ({
      key: msg.key ? Buffer.from(msg.key) : undefined,
      value: Buffer.from(JSON.stringify(msg.value)),
      headers: msg.headers,
      partition: msg.partition,
      timestamp: msg.timestamp,
    }));

    const record: ProducerRecord = {
      topic,
      messages: kafkaMessages,
    };

    return await this.sendWithRetry(record);
  }

  /**
   * Send with retry logic
   */
  private async sendWithRetry(
    record: ProducerRecord,
    attempt: number = 1
  ): Promise<RecordMetadata[]> {
    try {
      return await this.producer.send(record);
    } catch (error) {
      if (attempt < this.retries) {
        // Exponential backoff
        const delay = this.retryDelay * Math.pow(2, attempt - 1);
        await this.sleep(delay);
        return await this.sendWithRetry(record, attempt + 1);
      }
      
      // All retries exhausted, send to DLQ
      await this.sendToDLQ(record, error);
      throw error;
    }
  }

  /**
   * Send failed messages to Dead Letter Queue
   */
  private async sendToDLQ(record: ProducerRecord, error: any): Promise<void> {
    const dlqTopic = `${record.topic}.dlq`;
    
    try {
      const dlqMessages: Message[] = record.messages.map(msg => ({
        ...msg,
        headers: {
          ...msg.headers,
          'x-original-topic': record.topic,
          'x-error': error.message || 'Unknown error',
          'x-failed-at': new Date().toISOString(),
        },
      }));

      await this.producer.send({
        topic: dlqTopic,
        messages: dlqMessages,
      });
    } catch (dlqError) {
      console.error('Failed to send to DLQ:', dlqError);
    }
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
