/**
 * Standard roles in the FinOps platform
 */
export enum Role {
  SUPER_ADMIN = 'super_admin',
  ORG_ADMIN = 'org_admin',
  ORG_MEMBER = 'org_member',
  FINOPS_MANAGER = 'finops_manager',
  FINOPS_ANALYST = 'finops_analyst',
  ENGINEER = 'engineer',
  VIEWER = 'viewer',
}

/**
 * Permissions in the FinOps platform
 */
export enum Permission {
  // Cost Management
  'costs:read' = 'costs:read',
  'costs:write' = 'costs:write',
  'costs:delete' = 'costs:delete',
  
  // Budget Management
  'budgets:read' = 'budgets:read',
  'budgets:write' = 'budgets:write',
  'budgets:delete' = 'budgets:delete',
  
  // Recommendations
  'recommendations:read' = 'recommendations:read',
  'recommendations:write' = 'recommendations:write',
  'recommendations:approve' = 'recommendations:approve',
  
  // Alerts
  'alerts:read' = 'alerts:read',
  'alerts:write' = 'alerts:write',
  'alerts:delete' = 'alerts:delete',
  
  // Reports
  'reports:read' = 'reports:read',
  'reports:write' = 'reports:write',
  'reports:delete' = 'reports:delete',
  
  // Users
  'users:read' = 'users:read',
  'users:write' = 'users:write',
  'users:delete' = 'users:delete',
  
  // Organizations
  'orgs:read' = 'orgs:read',
  'orgs:write' = 'orgs:write',
  'orgs:delete' = 'orgs:delete',
  
  // Settings
  'settings:read' = 'settings:read',
  'settings:write' = 'settings:write',
  
  // Integrations
  'integrations:read' = 'integrations:read',
  'integrations:write' = 'integrations:write',
  'integrations:delete' = 'integrations:delete',
}

/**
 * Role to permissions mapping
 */
export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  [Role.SUPER_ADMIN]: [
    ...Object.values(Permission),
  ],
  
  [Role.ORG_ADMIN]: [
    Permission['costs:read'],
    Permission['costs:write'],
    Permission['budgets:read'],
    Permission['budgets:write'],
    Permission['budgets:delete'],
    Permission['recommendations:read'],
    Permission['recommendations:approve'],
    Permission['alerts:read'],
    Permission['alerts:write'],
    Permission['alerts:delete'],
    Permission['reports:read'],
    Permission['reports:write'],
    Permission['users:read'],
    Permission['users:write'],
    Permission['orgs:read'],
    Permission['orgs:write'],
    Permission['settings:read'],
    Permission['settings:write'],
    Permission['integrations:read'],
    Permission['integrations:write'],
    Permission['integrations:delete'],
  ],
  
  [Role.ORG_MEMBER]: [
    Permission['costs:read'],
    Permission['budgets:read'],
    Permission['recommendations:read'],
    Permission['alerts:read'],
    Permission['reports:read'],
  ],
  
  [Role.FINOPS_MANAGER]: [
    Permission['costs:read'],
    Permission['costs:write'],
    Permission['budgets:read'],
    Permission['budgets:write'],
    Permission['budgets:delete'],
    Permission['recommendations:read'],
    Permission['recommendations:write'],
    Permission['recommendations:approve'],
    Permission['alerts:read'],
    Permission['alerts:write'],
    Permission['alerts:delete'],
    Permission['reports:read'],
    Permission['reports:write'],
    Permission['reports:delete'],
    Permission['settings:read'],
    Permission['integrations:read'],
  ],
  
  [Role.FINOPS_ANALYST]: [
    Permission['costs:read'],
    Permission['budgets:read'],
    Permission['budgets:write'],
    Permission['recommendations:read'],
    Permission['recommendations:write'],
    Permission['alerts:read'],
    Permission['alerts:write'],
    Permission['reports:read'],
    Permission['reports:write'],
  ],
  
  [Role.ENGINEER]: [
    Permission['costs:read'],
    Permission['budgets:read'],
    Permission['recommendations:read'],
    Permission['reports:read'],
  ],
  
  [Role.VIEWER]: [
    Permission['costs:read'],
    Permission['budgets:read'],
    Permission['recommendations:read'],
    Permission['alerts:read'],
    Permission['reports:read'],
  ],
};

/**
 * Check if role has permission
 */
export function roleHasPermission(role: Role, permission: Permission): boolean {
  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
}

/**
 * Get all permissions for a role
 */
export function getPermissionsForRole(role: Role): Permission[] {
  return ROLE_PERMISSIONS[role] || [];
}
