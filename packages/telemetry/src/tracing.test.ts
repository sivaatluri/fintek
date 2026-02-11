import { withSpan, startSpan, addSpanEvent, setSpanAttribute, setSpanAttributes } from '../tracing';

describe('Tracing', () => {
  describe('withSpan', () => {
    it('should execute function within span', async () => {
      const result = await withSpan('test-span', async (span) => {
        return 'test-result';
      });
      
      expect(result).toBe('test-result');
    });

    it('should handle errors', async () => {
      await expect(
        withSpan('test-span', async () => {
          throw new Error('Test error');
        })
      ).rejects.toThrow('Test error');
    });

    it('should add attributes to span', async () => {
      await withSpan(
        'test-span',
        async (span) => {
          span.setAttribute('key', 'value');
          return 'done';
        },
        { attr1: 'value1' }
      );
    });
  });

  describe('startSpan', () => {
    it('should start a new span', () => {
      const span = startSpan('test-span', { key: 'value' });
      expect(span).toBeDefined();
      span.end();
    });
  });

  describe('addSpanEvent', () => {
    it('should add event to span', async () => {
      await withSpan('test-span', async () => {
        addSpanEvent('test-event', { key: 'value' });
      });
    });
  });

  describe('setSpanAttribute', () => {
    it('should set attribute on span', async () => {
      await withSpan('test-span', async () => {
        setSpanAttribute('key', 'value');
      });
    });
  });

  describe('setSpanAttributes', () => {
    it('should set multiple attributes on span', async () => {
      await withSpan('test-span', async () => {
        setSpanAttributes({
          key1: 'value1',
          key2: 'value2',
          key3: 123,
        });
      });
    });
  });
});
