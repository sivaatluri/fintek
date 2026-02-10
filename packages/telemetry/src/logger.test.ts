import { Logger, createLogger } from '../logger';

describe('Logger', () => {
  let logger: Logger;

  beforeEach(() => {
    logger = createLogger({
      level: 'debug',
      serviceName: 'test-service',
    });
  });

  it('should create logger instance', () => {
    expect(logger).toBeInstanceOf(Logger);
  });

  it('should log debug messages', () => {
    expect(() => {
      logger.debug('Debug message', { key: 'value' });
    }).not.toThrow();
  });

  it('should log info messages', () => {
    expect(() => {
      logger.info('Info message', { key: 'value' });
    }).not.toThrow();
  });

  it('should log warn messages', () => {
    expect(() => {
      logger.warn('Warning message', { key: 'value' });
    }).not.toThrow();
  });

  it('should log error messages', () => {
    const error = new Error('Test error');
    expect(() => {
      logger.error('Error message', error, { key: 'value' });
    }).not.toThrow();
  });

  it('should create child logger', () => {
    const childLogger = logger.child({ requestId: '123' });
    expect(childLogger).toBeInstanceOf(Logger);
    
    expect(() => {
      childLogger.info('Child logger message');
    }).not.toThrow();
  });
});
