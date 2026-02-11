import {
  BaseError,
  BadRequestError,
  UnauthorizedError,
  ForbiddenError,
  NotFoundError,
  ConflictError,
  ValidationError,
  InternalServerError,
  ServiceUnavailableError,
  isOperationalError
} from '../errors';

describe('Errors', () => {
  describe('BaseError', () => {
    class TestError extends BaseError {
      constructor(message: string) {
        super(message, 'TEST_ERROR', 500, true);
      }
    }

    it('should create error with correct properties', () => {
      const error = new TestError('Test message');
      
      expect(error.message).toBe('Test message');
      expect(error.code).toBe('TEST_ERROR');
      expect(error.statusCode).toBe(500);
      expect(error.isOperational).toBe(true);
      expect(error.timestamp).toBeInstanceOf(Date);
      expect(error.name).toBe('TestError');
    });

    it('should include context when provided', () => {
      const context = { userId: '123', action: 'test' };
      const error = new TestError('Test message');
      error.context = context;
      
      expect(error.context).toEqual(context);
    });

    it('should serialize to JSON correctly', () => {
      const error = new TestError('Test message');
      const json = error.toJSON();
      
      expect(json.name).toBe('TestError');
      expect(json.message).toBe('Test message');
      expect(json.code).toBe('TEST_ERROR');
      expect(json.statusCode).toBe(500);
      expect(json.timestamp).toBeDefined();
      expect(json.stack).toBeDefined();
    });
  });

  describe('BadRequestError', () => {
    it('should create 400 error', () => {
      const error = new BadRequestError('Invalid input');
      
      expect(error.statusCode).toBe(400);
      expect(error.code).toBe('BAD_REQUEST');
      expect(error.message).toBe('Invalid input');
      expect(error.isOperational).toBe(true);
    });
  });

  describe('UnauthorizedError', () => {
    it('should create 401 error', () => {
      const error = new UnauthorizedError('Not authenticated');
      
      expect(error.statusCode).toBe(401);
      expect(error.code).toBe('UNAUTHORIZED');
      expect(error.message).toBe('Not authenticated');
    });
  });

  describe('ForbiddenError', () => {
    it('should create 403 error', () => {
      const error = new ForbiddenError('Access denied');
      
      expect(error.statusCode).toBe(403);
      expect(error.code).toBe('FORBIDDEN');
    });
  });

  describe('NotFoundError', () => {
    it('should create 404 error', () => {
      const error = new NotFoundError('Resource not found');
      
      expect(error.statusCode).toBe(404);
      expect(error.code).toBe('NOT_FOUND');
    });
  });

  describe('ConflictError', () => {
    it('should create 409 error', () => {
      const error = new ConflictError('Resource already exists');
      
      expect(error.statusCode).toBe(409);
      expect(error.code).toBe('CONFLICT');
    });
  });

  describe('ValidationError', () => {
    it('should create 422 error', () => {
      const error = new ValidationError('Validation failed');
      
      expect(error.statusCode).toBe(422);
      expect(error.code).toBe('VALIDATION_ERROR');
    });
  });

  describe('InternalServerError', () => {
    it('should create 500 error', () => {
      const error = new InternalServerError('Something went wrong');
      
      expect(error.statusCode).toBe(500);
      expect(error.code).toBe('INTERNAL_SERVER_ERROR');
      expect(error.isOperational).toBe(false);
    });
  });

  describe('ServiceUnavailableError', () => {
    it('should create 503 error', () => {
      const error = new ServiceUnavailableError('Service down');
      
      expect(error.statusCode).toBe(503);
      expect(error.code).toBe('SERVICE_UNAVAILABLE');
    });
  });

  describe('isOperationalError', () => {
    it('should return true for operational errors', () => {
      const error = new BadRequestError();
      expect(isOperationalError(error)).toBe(true);
    });

    it('should return false for non-operational errors', () => {
      const error = new InternalServerError();
      expect(isOperationalError(error)).toBe(false);
    });

    it('should return false for standard errors', () => {
      const error = new Error('Standard error');
      expect(isOperationalError(error)).toBe(false);
    });
  });
});
