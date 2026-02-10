import { AsyncLocalStorage } from 'async_hooks';
import { v4 as uuidv4 } from 'uuid';

/**
 * Context data stored in AsyncLocalStorage
 */
export interface RequestContext {
  requestId: string;
  orgId?: string;
  tenantId?: string;
  userId?: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

/**
 * AsyncLocalStorage for request context
 */
const contextStorage = new AsyncLocalStorage<RequestContext>();

/**
 * Initialize request context with a new request ID
 */
export function initializeContext(
  requestId?: string,
  data?: Partial<Omit<RequestContext, 'requestId' | 'timestamp'>>
): RequestContext {
  const context: RequestContext = {
    requestId: requestId || uuidv4(),
    timestamp: new Date(),
    ...data
  };
  return context;
}

/**
 * Run function within a new request context
 */
export function runWithContext<T>(
  context: RequestContext,
  fn: () => T
): T {
  return contextStorage.run(context, fn);
}

/**
 * Get current request context
 */
export function getContext(): RequestContext | undefined {
  return contextStorage.getStore();
}

/**
 * Get current request ID
 */
export function getRequestId(): string | undefined {
  const context = getContext();
  return context?.requestId;
}

/**
 * Get current organization ID
 */
export function getOrgId(): string | undefined {
  const context = getContext();
  return context?.orgId;
}

/**
 * Get current tenant ID
 */
export function getTenantId(): string | undefined {
  const context = getContext();
  return context?.tenantId;
}

/**
 * Get current user ID
 */
export function getUserId(): string | undefined {
  const context = getContext();
  return context?.userId;
}

/**
 * Update current context with partial data
 */
export function updateContext(data: Partial<RequestContext>): void {
  const context = getContext();
  if (context) {
    Object.assign(context, data);
  }
}

/**
 * Express/Connect middleware to initialize request context
 */
export function contextMiddleware() {
  return (req: any, res: any, next: any) => {
    const requestId = req.headers['x-request-id'] as string || uuidv4();
    const orgId = req.headers['x-org-id'] as string;
    const tenantId = req.headers['x-tenant-id'] as string;
    
    const context = initializeContext(requestId, {
      orgId,
      tenantId,
      userId: req.user?.id
    });

    // Set response header
    res.setHeader('x-request-id', context.requestId);

    runWithContext(context, () => {
      next();
    });
  };
}
