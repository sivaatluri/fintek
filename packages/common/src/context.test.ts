import {
  initializeContext,
  runWithContext,
  getContext,
  getRequestId,
  getOrgId,
  getTenantId,
  getUserId,
  updateContext,
  contextMiddleware,
  RequestContext
} from '../context';

describe('Context', () => {
  describe('initializeContext', () => {
    it('should create context with generated requestId', () => {
      const context = initializeContext();
      
      expect(context.requestId).toBeDefined();
      expect(context.timestamp).toBeInstanceOf(Date);
    });

    it('should create context with provided requestId', () => {
      const requestId = 'test-request-id';
      const context = initializeContext(requestId);
      
      expect(context.requestId).toBe(requestId);
    });

    it('should include additional data', () => {
      const context = initializeContext('req-1', {
        orgId: 'org-123',
        tenantId: 'tenant-456',
        userId: 'user-789'
      });
      
      expect(context.orgId).toBe('org-123');
      expect(context.tenantId).toBe('tenant-456');
      expect(context.userId).toBe('user-789');
    });
  });

  describe('runWithContext', () => {
    it('should run function with context', () => {
      const context = initializeContext('req-1');
      let capturedContext: RequestContext | undefined;
      
      runWithContext(context, () => {
        capturedContext = getContext();
      });
      
      expect(capturedContext).toEqual(context);
    });

    it('should isolate contexts', () => {
      const context1 = initializeContext('req-1');
      const context2 = initializeContext('req-2');
      
      let id1: string | undefined;
      let id2: string | undefined;
      
      runWithContext(context1, () => {
        id1 = getRequestId();
      });
      
      runWithContext(context2, () => {
        id2 = getRequestId();
      });
      
      expect(id1).toBe('req-1');
      expect(id2).toBe('req-2');
    });
  });

  describe('getContext', () => {
    it('should return undefined when no context', () => {
      expect(getContext()).toBeUndefined();
    });

    it('should return current context', () => {
      const context = initializeContext('req-1');
      
      runWithContext(context, () => {
        expect(getContext()).toEqual(context);
      });
    });
  });

  describe('getRequestId', () => {
    it('should return request ID from context', () => {
      const context = initializeContext('req-123');
      
      runWithContext(context, () => {
        expect(getRequestId()).toBe('req-123');
      });
    });
  });

  describe('getOrgId', () => {
    it('should return org ID from context', () => {
      const context = initializeContext('req-1', { orgId: 'org-456' });
      
      runWithContext(context, () => {
        expect(getOrgId()).toBe('org-456');
      });
    });
  });

  describe('getTenantId', () => {
    it('should return tenant ID from context', () => {
      const context = initializeContext('req-1', { tenantId: 'tenant-789' });
      
      runWithContext(context, () => {
        expect(getTenantId()).toBe('tenant-789');
      });
    });
  });

  describe('getUserId', () => {
    it('should return user ID from context', () => {
      const context = initializeContext('req-1', { userId: 'user-123' });
      
      runWithContext(context, () => {
        expect(getUserId()).toBe('user-123');
      });
    });
  });

  describe('updateContext', () => {
    it('should update context with new data', () => {
      const context = initializeContext('req-1');
      
      runWithContext(context, () => {
        updateContext({ orgId: 'org-new' });
        expect(getOrgId()).toBe('org-new');
      });
    });
  });

  describe('contextMiddleware', () => {
    it('should initialize context from headers', () => {
      const middleware = contextMiddleware();
      const req = {
        headers: {
          'x-request-id': 'req-from-header',
          'x-org-id': 'org-123',
          'x-tenant-id': 'tenant-456'
        }
      };
      const res = {
        setHeader: jest.fn()
      };
      const next = jest.fn();
      
      middleware(req, res, next);
      
      expect(res.setHeader).toHaveBeenCalledWith('x-request-id', 'req-from-header');
      expect(next).toHaveBeenCalled();
    });

    it('should generate request ID when not provided', () => {
      const middleware = contextMiddleware();
      const req = {
        headers: {}
      };
      const res = {
        setHeader: jest.fn()
      };
      const next = jest.fn();
      
      middleware(req, res, next);
      
      expect(res.setHeader).toHaveBeenCalled();
      const requestId = (res.setHeader as jest.Mock).mock.calls[0][1];
      expect(typeof requestId).toBe('string');
      expect(requestId).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });
  });
});
