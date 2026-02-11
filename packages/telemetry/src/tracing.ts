import { trace, context, SpanStatusCode, Span, SpanKind, Attributes } from '@opentelemetry/api';

/**
 * Get the active tracer
 */
export function getTracer(name: string = 'finops') {
  return trace.getTracer(name);
}

/**
 * Start a new span
 */
export function startSpan(
  name: string,
  attributes?: Attributes,
  kind: SpanKind = SpanKind.INTERNAL
): Span {
  const tracer = getTracer();
  return tracer.startSpan(name, {
    kind,
    attributes,
  });
}

/**
 * Execute function within a span
 */
export async function withSpan<T>(
  name: string,
  fn: (span: Span) => Promise<T>,
  attributes?: Attributes
): Promise<T> {
  const span = startSpan(name, attributes);
  
  try {
    const result = await context.with(trace.setSpan(context.active(), span), async () => {
      return await fn(span);
    });
    
    span.setStatus({ code: SpanStatusCode.OK });
    return result;
  } catch (error) {
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error instanceof Error ? error.message : String(error),
    });
    
    if (error instanceof Error) {
      span.recordException(error);
    }
    
    throw error;
  } finally {
    span.end();
  }
}

/**
 * Add event to current span
 */
export function addSpanEvent(name: string, attributes?: Attributes): void {
  const span = trace.getSpan(context.active());
  if (span) {
    span.addEvent(name, attributes);
  }
}

/**
 * Set attribute on current span
 */
export function setSpanAttribute(key: string, value: string | number | boolean): void {
  const span = trace.getSpan(context.active());
  if (span) {
    span.setAttribute(key, value);
  }
}

/**
 * Set multiple attributes on current span
 */
export function setSpanAttributes(attributes: Attributes): void {
  const span = trace.getSpan(context.active());
  if (span) {
    span.setAttributes(attributes);
  }
}

/**
 * Record exception on current span
 */
export function recordSpanException(error: Error): void {
  const span = trace.getSpan(context.active());
  if (span) {
    span.recordException(error);
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error.message,
    });
  }
}

/**
 * Decorator for tracing methods
 */
export function Traced(spanName?: string) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    const name = spanName || `${target.constructor.name}.${propertyKey}`;

    descriptor.value = async function (...args: any[]) {
      return await withSpan(name, async (span) => {
        return await originalMethod.apply(this, args);
      });
    };

    return descriptor;
  };
}
