import { PolicyEngine, PolicyContext, Resource } from '../policy';
import { Role, Permission } from '../permissions';

describe('PolicyEngine', () => {
  let engine: PolicyEngine;
  let adminContext: PolicyContext;
  let viewerContext: PolicyContext;
  let resource: Resource;

  beforeEach(() => {
    engine = new PolicyEngine();
    
    adminContext = {
      userId: 'admin-123',
      roles: [Role.ORG_ADMIN],
      orgId: 'org-456',
    };

    viewerContext = {
      userId: 'viewer-123',
      roles: [Role.VIEWER],
      orgId: 'org-456',
    };

    resource = {
      type: 'budget',
      id: 'budget-789',
      orgId: 'org-456',
      ownerId: 'admin-123',
    };
  });

  describe('hasPermission', () => {
    it('should return true for admin with write permission', () => {
      expect(engine.hasPermission(adminContext, Permission['costs:write'])).toBe(true);
    });

    it('should return false for viewer with write permission', () => {
      expect(engine.hasPermission(viewerContext, Permission['costs:write'])).toBe(false);
    });

    it('should return true for viewer with read permission', () => {
      expect(engine.hasPermission(viewerContext, Permission['costs:read'])).toBe(true);
    });
  });

  describe('hasRole', () => {
    it('should return true for matching role', () => {
      expect(engine.hasRole(adminContext, Role.ORG_ADMIN)).toBe(true);
    });

    it('should return false for non-matching role', () => {
      expect(engine.hasRole(viewerContext, Role.ORG_ADMIN)).toBe(false);
    });
  });

  describe('belongsToOrganization', () => {
    it('should return true for same organization', () => {
      expect(engine.belongsToOrganization(adminContext, resource)).toBe(true);
    });

    it('should return false for different organization', () => {
      const otherOrgContext = { ...adminContext, orgId: 'org-999' };
      expect(engine.belongsToOrganization(otherOrgContext, resource)).toBe(false);
    });
  });

  describe('ownsResource', () => {
    it('should return true for resource owner', () => {
      expect(engine.ownsResource(adminContext, resource)).toBe(true);
    });

    it('should return false for non-owner', () => {
      expect(engine.ownsResource(viewerContext, resource)).toBe(false);
    });
  });

  describe('evaluate', () => {
    it('should allow access with matching policy', async () => {
      engine.registerPolicy('test', () => ({
        allowed: true,
        reason: 'Test policy',
      }));

      const result = await engine.evaluate(adminContext, resource, 'read');
      expect(result.allowed).toBe(true);
    });

    it('should deny access without matching policy', async () => {
      const result = await engine.evaluate(adminContext, resource, 'read');
      expect(result.allowed).toBe(false);
    });
  });

  describe('createRBACPolicy', () => {
    it('should create RBAC policy that allows admin', async () => {
      const policy = PolicyEngine.createRBACPolicy(Permission['costs:write']);
      const result = await policy(adminContext, resource, 'write');
      expect(result.allowed).toBe(true);
    });

    it('should create RBAC policy that denies viewer', async () => {
      const policy = PolicyEngine.createRBACPolicy(Permission['costs:write']);
      const result = await policy(viewerContext, resource, 'write');
      expect(result.allowed).toBe(false);
    });
  });

  describe('createOrgResourcePolicy', () => {
    it('should allow access for same org with permission', async () => {
      const policy = PolicyEngine.createOrgResourcePolicy(Permission['costs:read']);
      const result = await policy(adminContext, resource, 'read');
      expect(result.allowed).toBe(true);
    });

    it('should deny access for different org', async () => {
      const policy = PolicyEngine.createOrgResourcePolicy(Permission['costs:read']);
      const otherOrgContext = { ...adminContext, orgId: 'org-999' };
      const result = await policy(otherOrgContext, resource, 'read');
      expect(result.allowed).toBe(false);
    });
  });

  describe('createOwnerPolicy', () => {
    it('should allow access for owner with permission', async () => {
      const policy = PolicyEngine.createOwnerPolicy(Permission['costs:write']);
      const result = await policy(adminContext, resource, 'write');
      expect(result.allowed).toBe(true);
    });

    it('should deny access for non-owner', async () => {
      const policy = PolicyEngine.createOwnerPolicy(Permission['costs:write']);
      const result = await policy(viewerContext, resource, 'write');
      expect(result.allowed).toBe(false);
    });
  });
});
