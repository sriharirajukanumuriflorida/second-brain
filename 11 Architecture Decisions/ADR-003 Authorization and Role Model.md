# ADR-003: Authorization and Role Model

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform requires server-side authorization to enforce permissions beyond authentication. While MVP may be single-user, the permission model should be coded cleanly to support future multi-user access. Authorization must protect vault access, workflow execution, and administrative operations.

## Decision
**Permission Model:**

```text
can_read_vault
can_sync_repo
can_run_workflow
can_approve_draft
can_create_pr
can_view_costs
can_admin_config
```

**Initial Roles:**

```text
Admin
ReadOnly
```

**MVP Implementation:**
- Only `Admin` role enabled initially
- Permission checks must be implemented server-side
- Permission model must be extensible for multi-user support
- Authorization must be enforced on all API endpoints

## Alternatives Considered

### No Authorization (Auth-Only)
- **Pros:** Simpler implementation
- **Cons:** No defense-in-depth, cannot support multi-user, rejected per security requirements

### RBAC with Complex Role Hierarchy
- **Pros:** Fine-grained control for large organizations
- **Cons:** Over-engineering for MVP, unnecessary complexity

### Attribute-Based Access Control (ABAC)
- **Pros:** Highly flexible, policy-based
- **Cons:** Complex implementation, overkill for MVP

## Consequences
- All API endpoints must enforce permissions
- Authorization checks are server-side (not client-side only)
- Permission model is extensible for future multi-user scenarios
- Admin role has all permissions in MVP
- ReadOnly role can be added later for review-only access
- Permission checks must be implemented before any protected operation

## Cost Impact
- No direct cost impact
- Slight development overhead for permission system
- Future multi-user licensing costs not considered in MVP

## Security Impact
- Defense-in-depth: authorization beyond authentication
- Server-side enforcement prevents client-side bypass
- Least privilege principle can be applied with ReadOnly role
- Audit trail can capture permission denials
- Vault access is protected by explicit permissions
- Workflow execution is controlled by can_run_workflow permission

## Operational Impact
- Permission denials are logged for audit
- Role changes can be made without code deployment
- Multi-user onboarding is supported by existing permission model
- Admin operations are clearly separated from user operations
- Permission model can be extended for organizational needs

## Follow-Up Actions
- [ ] Implement permission checking middleware
- [ ] Implement Admin role with all permissions
- [ ] Add permission checks to all API endpoints
- [ ] Log permission denials
- [ ] Document permission model for future multi-user support
- [ ] Consider ReadOnly role implementation for review workflows
