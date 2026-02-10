import { PolicyContext, Resource } from './policy';
import { Permission } from './permissions';

/**
 * Decorator for requiring specific permissions
 */
export function RequirePermission(...permissions: Permission[]) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      // Extract context from first argument (assuming it's passed as first param)
      const context: PolicyContext = args[0]?.context || args[0];
      
      if (!context || !context.roles) {
        throw new Error('Unauthorized: No valid context provided');
      }

      // Check permissions
      const hasPermission = permissions.some(permission =>
        context.permissions?.includes(permission) ||
        context.roles.some(role => {
          // This would need the roleHasPermission check
          return false; // Simplified for decorator
        })
      );

      if (!hasPermission) {
        throw new Error(`Forbidden: Missing required permissions: ${permissions.join(', ')}`);
      }

      return await originalMethod.apply(this, args);
    };

    return descriptor;
  };
}

/**
 * Middleware function for Express to check permissions
 */
export function requirePermission(...permissions: Permission[]) {
  return (req: any, res: any, next: any) => {
    const context: PolicyContext = req.context || {
      userId: req.user?.id,
      roles: req.user?.roles || [],
      permissions: req.user?.permissions || [],
      orgId: req.user?.orgId,
    };

    // Check if user has any of the required permissions
    const hasPermission = permissions.some(permission =>
      context.permissions?.includes(permission)
    );

    if (!hasPermission) {
      return res.status(403).json({
        error: 'Forbidden',
        message: `Missing required permissions: ${permissions.join(', ')}`,
      });
    }

    next();
  };
}

/**
 * Middleware to check if user owns the resource
 */
export function requireOwnership(resourceIdParam: string = 'id') {
  return (req: any, res: any, next: any) => {
    const context: PolicyContext = req.context || {
      userId: req.user?.id,
      roles: req.user?.roles || [],
    };

    const resourceOwnerId = req.resource?.ownerId || req.params[resourceIdParam];

    if (context.userId !== resourceOwnerId) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'You do not have permission to access this resource',
      });
    }

    next();
  };
}

/**
 * Middleware to check organization membership
 */
export function requireOrganization() {
  return (req: any, res: any, next: any) => {
    const context: PolicyContext = req.context || {
      userId: req.user?.id,
      roles: req.user?.roles || [],
      orgId: req.user?.orgId,
    };

    const resource: Resource = req.resource || {
      type: req.params.resourceType,
      orgId: req.params.orgId,
    };

    if (context.orgId !== resource.orgId) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Resource belongs to a different organization',
      });
    }

    next();
  };
}
