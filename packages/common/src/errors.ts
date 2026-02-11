/**
 * Base error class for all FinOps platform errors
 */
export abstract class BaseError extends Error {
  public readonly code: string;
  public readonly statusCode: number;
  public readonly isOperational: boolean;
  public readonly timestamp: Date;
  public readonly context?: Record<string, any>;

  constructor(
    message: string,
    code: string,
    statusCode: number = 500,
    isOperational: boolean = true,
    context?: Record<string, any>
  ) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    this.timestamp = new Date();
    this.context = context;

    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      statusCode: this.statusCode,
      timestamp: this.timestamp.toISOString(),
      context: this.context,
      stack: this.stack
    };
  }
}

/**
 * 400 Bad Request - Client sent invalid data
 */
export class BadRequestError extends BaseError {
  constructor(message: string = 'Bad Request', context?: Record<string, any>) {
    super(message, 'BAD_REQUEST', 400, true, context);
  }
}

/**
 * 401 Unauthorized - Authentication required
 */
export class UnauthorizedError extends BaseError {
  constructor(message: string = 'Unauthorized', context?: Record<string, any>) {
    super(message, 'UNAUTHORIZED', 401, true, context);
  }
}

/**
 * 403 Forbidden - User doesn't have permission
 */
export class ForbiddenError extends BaseError {
  constructor(message: string = 'Forbidden', context?: Record<string, any>) {
    super(message, 'FORBIDDEN', 403, true, context);
  }
}

/**
 * 404 Not Found - Resource not found
 */
export class NotFoundError extends BaseError {
  constructor(message: string = 'Not Found', context?: Record<string, any>) {
    super(message, 'NOT_FOUND', 404, true, context);
  }
}

/**
 * 409 Conflict - Resource conflict (e.g., duplicate)
 */
export class ConflictError extends BaseError {
  constructor(message: string = 'Conflict', context?: Record<string, any>) {
    super(message, 'CONFLICT', 409, true, context);
  }
}

/**
 * 422 Unprocessable Entity - Validation failed
 */
export class ValidationError extends BaseError {
  constructor(message: string = 'Validation Failed', context?: Record<string, any>) {
    super(message, 'VALIDATION_ERROR', 422, true, context);
  }
}

/**
 * 500 Internal Server Error - Unexpected server error
 */
export class InternalServerError extends BaseError {
  constructor(message: string = 'Internal Server Error', context?: Record<string, any>) {
    super(message, 'INTERNAL_SERVER_ERROR', 500, false, context);
  }
}

/**
 * 503 Service Unavailable - Service temporarily unavailable
 */
export class ServiceUnavailableError extends BaseError {
  constructor(message: string = 'Service Unavailable', context?: Record<string, any>) {
    super(message, 'SERVICE_UNAVAILABLE', 503, true, context);
  }
}

/**
 * Check if error is an operational error (expected, can be handled)
 */
export function isOperationalError(error: Error): boolean {
  if (error instanceof BaseError) {
    return error.isOperational;
  }
  return false;
}
