import { Role, Permission, roleHasPermission, getPermissionsForRole } from '../permissions';

describe('Permissions', () => {
  describe('roleHasPermission', () => {
    it('should return true for super admin with any permission', () => {
      expect(roleHasPermission(Role.SUPER_ADMIN, Permission['costs:read'])).toBe(true);
      expect(roleHasPermission(Role.SUPER_ADMIN, Permission['users:delete'])).toBe(true);
    });

    it('should return true for org admin with admin permissions', () => {
      expect(roleHasPermission(Role.ORG_ADMIN, Permission['costs:write'])).toBe(true);
      expect(roleHasPermission(Role.ORG_ADMIN, Permission['users:write'])).toBe(true);
    });

    it('should return false for viewer with write permissions', () => {
      expect(roleHasPermission(Role.VIEWER, Permission['costs:write'])).toBe(false);
      expect(roleHasPermission(Role.VIEWER, Permission['budgets:write'])).toBe(false);
    });

    it('should return true for viewer with read permissions', () => {
      expect(roleHasPermission(Role.VIEWER, Permission['costs:read'])).toBe(true);
      expect(roleHasPermission(Role.VIEWER, Permission['budgets:read'])).toBe(true);
    });
  });

  describe('getPermissionsForRole', () => {
    it('should return all permissions for super admin', () => {
      const permissions = getPermissionsForRole(Role.SUPER_ADMIN);
      expect(permissions.length).toBeGreaterThan(0);
      expect(permissions).toContain(Permission['costs:read']);
      expect(permissions).toContain(Permission['users:delete']);
    });

    it('should return limited permissions for viewer', () => {
      const permissions = getPermissionsForRole(Role.VIEWER);
      expect(permissions).toContain(Permission['costs:read']);
      expect(permissions).not.toContain(Permission['costs:write']);
    });
  });
});
