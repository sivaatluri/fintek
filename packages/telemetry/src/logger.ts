import pino, { Logger as PinoLogger } from 'pino';
import { trace, context, SpanStatusCode, Span } from '@opentelemetry/api';

export interface LoggerConfig {
  level?: 'debug' | 'info' | 'warn' | 'error';
  pretty?: boolean;
  serviceName?: string;
}

/**
 * Logger class wrapping Pino with OpenTelemetry integration
 */
export class Logger {
  private logger: PinoLogger;
  private serviceName: string;

  constructor(config: LoggerConfig = {}) {
    this.serviceName = config.serviceName || 'finops-service';
    
    const pinoOptions: any = {
      level: config.level || 'info',
      name: this.serviceName,
      timestamp: pino.stdTimeFunctions.isoTime,
    };

    if (config.pretty) {
      this.logger = pino({
        ...pinoOptions,
        transport: {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: 'SYS:standard',
            ignore: 'pid,hostname',
          },
        },
      });
    } else {
      this.logger = pino(pinoOptions);
    }
  }

  /**
   * Get context fields including trace information
   */
  private getContextFields(): Record<string, any> {
    const activeSpan = trace.getSpan(context.active());
    if (activeSpan) {
      const spanContext = activeSpan.spanContext();
      return {
        traceId: spanContext.traceId,
        spanId: spanContext.spanId,
        traceFlags: spanContext.traceFlags,
      };
    }
    return {};
  }

  /**
   * Debug level log
   */
  debug(message: string, data?: Record<string, any>): void {
    this.logger.debug({ ...this.getContextFields(), ...data }, message);
  }

  /**
   * Info level log
   */
  info(message: string, data?: Record<string, any>): void {
    this.logger.info({ ...this.getContextFields(), ...data }, message);
  }

  /**
   * Warn level log
   */
  warn(message: string, data?: Record<string, any>): void {
    this.logger.warn({ ...this.getContextFields(), ...data }, message);
  }

  /**
   * Error level log
   */
  error(message: string, error?: Error, data?: Record<string, any>): void {
    const errorData = error ? {
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
      }
    } : {};
    
    this.logger.error({ ...this.getContextFields(), ...errorData, ...data }, message);
  }

  /**
   * Create a child logger with additional context
   */
  child(bindings: Record<string, any>): Logger {
    const childLogger = new Logger({ serviceName: this.serviceName });
    childLogger.logger = this.logger.child(bindings);
    return childLogger;
  }
}

/**
 * Create a logger instance
 */
export function createLogger(config?: LoggerConfig): Logger {
  return new Logger(config);
}

/**
 * Default logger instance
 */
export const logger = createLogger();
