import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';

export interface TelemetryConfig {
  serviceName: string;
  serviceVersion: string;
  otlpEndpoint: string;
  enabled?: boolean;
  samplingRate?: number;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

let sdk: NodeSDK | null = null;

/**
 * Initialize OpenTelemetry SDK
 */
export function initializeTelemetry(config: TelemetryConfig): NodeSDK {
  if (!config.enabled) {
    console.log('Telemetry disabled');
    return null as any;
  }

  const resource = new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: config.serviceName,
    [SemanticResourceAttributes.SERVICE_VERSION]: config.serviceVersion,
  });

  const traceExporter = new OTLPTraceExporter({
    url: `${config.otlpEndpoint}/v1/traces`,
  });

  const metricExporter = new OTLPMetricExporter({
    url: `${config.otlpEndpoint}/v1/metrics`,
  });

  const metricReader = new PeriodicExportingMetricReader({
    exporter: metricExporter,
    exportIntervalMillis: 60000, // Export every 60 seconds
  });

  sdk = new NodeSDK({
    resource,
    traceExporter,
    metricReader,
    instrumentations: [
      getNodeAutoInstrumentations({
        '@opentelemetry/instrumentation-fs': {
          enabled: false,
        },
      }),
    ],
  });

  sdk.start();
  console.log(`Telemetry initialized for service: ${config.serviceName}`);

  // Graceful shutdown
  process.on('SIGTERM', () => {
    sdk?.shutdown()
      .then(() => console.log('Telemetry shut down successfully'))
      .catch((error) => console.error('Error shutting down telemetry', error))
      .finally(() => process.exit(0));
  });

  return sdk;
}

/**
 * Shutdown telemetry
 */
export async function shutdownTelemetry(): Promise<void> {
  if (sdk) {
    await sdk.shutdown();
    sdk = null;
  }
}

/**
 * Get the active SDK instance
 */
export function getTelemetrySDK(): NodeSDK | null {
  return sdk;
}
