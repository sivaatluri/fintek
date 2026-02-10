import { Role, Permission, roleHasPermission } from './permissions';

/**
 * User context for policy evaluation
 */
export interface PolicyContext {
  userId: string;
  roles: Role[];
  orgId?: string;
  tenantId?: string;
  permissions?: Permission[];
  metadata?: Record<string, any>;
}

/**
 * Resource being accessed
 */
export interface Resource {
  type: string;
  id?: string;
  orgId?: string;
  tenantId?: string;
  ownerId?: string;
  attributes?: Record<string, any>;
}

/**
 * Policy evaluation result
 */
export interface PolicyResult {
  allowed: boolean;
  reason?: string;
}

/**
 * Policy evaluation function type
 */
export type PolicyEvaluator = (
  context: PolicyContext,
  resource: Resource,
  action: string
) => PolicyResult | Promise<PolicyResult>;

/**
 * Base policy engine
 */
export class PolicyEngine {
  private policies: Map<string, PolicyEvaluator> = new Map();

  /**
   * Register a policy evaluator
   */
  registerPolicy(name: string, evaluator: PolicyEvaluator): void {
    this.policies.set(name, evaluator);
  }

  /**
   * Check if user has required permission
   */
  hasPermission(context: PolicyContext, permission: Permission): boolean {
    // Check explicit permissions
    if (context.permissions?.includes(permission)) {
      return true;
    }

    // Check role-based permissions
    return context.roles.some(role => roleHasPermission(role, permission));
  }

  /**
   * Check if user has any of the required permissions
   */
  hasAnyPermission(context: PolicyContext, permissions: Permission[]): boolean {
    return permissions.some(permission => this.hasPermission(context, permission));
  }

  /**
   * Check if user has all required permissions
   */
  hasAllPermissions(context: PolicyContext, permissions: Permission[]): boolean {
    return permissions.every(permission => this.hasPermission(context, permission));
  }

  /**
   * Check if user has required role
   */
  hasRole(context: PolicyContext, role: Role): boolean {
    return context.roles.includes(role);
  }

  /**
   * Check if user has any of the required roles
   */
  hasAnyRole(context: PolicyContext, roles: Role[]): boolean {
    return roles.some(role => this.hasRole(context, role));
  }

  /**
   * Check if user belongs to the same organization as resource
   */
  belongsToOrganization(context: PolicyContext, resource: Resource): boolean {
    return context.orgId === resource.orgId;
  }

  /**
   * Check if user owns the resource
   */
  ownsResource(context: PolicyContext, resource: Resource): boolean {
    return context.userId === resource.ownerId;
  }

  /**
   * Evaluate access using registered policies
   */
  async evaluate(
    context: PolicyContext,
    resource: Resource,
    action: string
  ): Promise<PolicyResult> {
    // Try each registered policy
    for (const [name, evaluator] of this.policies) {
      const result = await evaluator(context, resource, action);
      if (result.allowed) {
        return result;
      }
    }

    // Default deny
    return {
      allowed: false,
      reason: 'No policy granted access',
    };
  }

  /**
   * Create RBAC policy evaluator
   */
  static createRBACPolicy(requiredPermission: Permission): PolicyEvaluator {
    return (context) => {
      const engine = new PolicyEngine();
      const allowed = engine.hasPermission(context, requiredPermission);
      return {
        allowed,
        reason: allowed ? 'User has required permission' : 'Missing required permission',
      };
    };
  }

  /**
   * Create ABAC policy evaluator for organization resources
   */
  static createOrgResourcePolicy(requiredPermission: Permission): PolicyEvaluator {
    return (context, resource) => {
      const engine = new PolicyEngine();
      
      // Check permission
      if (!engine.hasPermission(context, requiredPermission)) {
        return {
          allowed: false,
          reason: 'Missing required permission',
        };
      }

      // Check organization membership
      if (!engine.belongsToOrganization(context, resource)) {
        return {
          allowed: false,
          reason: 'User does not belong to resource organization',
        };
      }

      return {
        allowed: true,
        reason: 'User has permission and belongs to organization',
      };
    };
  }

  /**
   * Create ABAC policy evaluator for owned resources
   */
  static createOwnerPolicy(requiredPermission: Permission): PolicyEvaluator {
    return (context, resource) => {
      const engine = new PolicyEngine();
      
      // Check permission
      if (!engine.hasPermission(context, requiredPermission)) {
        return {
          allowed: false,
          reason: 'Missing required permission',
        };
      }

      // Check ownership
      if (!engine.ownsResource(context, resource)) {
        return {
          allowed: false,
          reason: 'User does not own the resource',
        };
      }

      return {
        allowed: true,
        reason: 'User has permission and owns resource',
      };
    };
  }
}

/**
 * Default policy engine instance
 */
export const defaultPolicyEngine = new PolicyEngine();
