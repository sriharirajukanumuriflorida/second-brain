# FDE Vault Agent Platform - Multi-Phase Implementation Plan (Updated Governance Revision)

## Documentation Authority

### Authority Model

- `multiple phases.md` = roadmap, sequencing, phase gates, delivery strategy.
- `implementationplan.md` = implementation, operations, security, testing, deployment, observability, and cost-governance source of truth.

### Conflict Resolution

If conflicts exist:

- `implementationplan.md` overrides implementation details.
- `multiple phases.md` overrides roadmap sequencing and phase boundaries.

### Documentation Maintenance Rule

Any change affecting:

- Phase boundaries
- Architecture Decisions (ADRs)
- Security controls
- Authentication strategy
- Sync strategy
- Testing strategy
- Cost controls
- Operational baselines

must evaluate whether both documents require updates.

---

## Phase -1: Architecture Decision Finalization

### Purpose

Finalize all major architecture decisions before implementation begins.

### ADR Lifecycle

**Statuses**

- Proposed
- Approved
- Superseded
- Rejected

**Owner**

- Hari Kanumuri

**Approval Requirement**

- All mandatory Phase -1 ADRs must be approved before Phase 0 begins.

### Required ADRs

- ADR-001 Hosting Provider and Deployment Model
- ADR-002 Authentication Provider and Session Strategy
- ADR-003 Authorization and Role Model
- ADR-004 GitHub Integration Model
- ADR-005 Vault Sync and Conflict Resolution Strategy
- ADR-006 Application Database Choice
- ADR-007 Vector Store and Embedding Strategy
- ADR-008 LLM Provider Strategy
- ADR-009 Cost Governance Strategy
- ADR-010 Observability and Logging Strategy
- ADR-011 Disaster Recovery Strategy
- ADR-012 CI/CD Strategy

### ADR Template

```text
Title
Status
Owner
Date

Context
Decision
Alternatives Considered
Consequences
Cost Impact
Security Impact
Operational Impact
Follow-Up Actions
```

### Go / No-Go Gate

No implementation work may start until all mandatory ADRs are approved.

---

## Cross-Phase Validation Policy

Before entering the next phase:

- Unit tests pass
- Integration tests pass
- Previous phase acceptance criteria satisfied
- No unresolved critical defects
- No unresolved critical security findings
- No unresolved architecture blockers

---

## Phase Rollback Policy

Each phase must define:

- Success Criteria
- Exit Criteria
- Rollback Triggers
- Rollback Procedure

### Typical Rollback Triggers

- Critical defects
- Security vulnerabilities
- Cost governance violations
- Failed architecture validation
- Failed production readiness review

### Typical Rollback Actions

- Restore previous deployment
- Disable workflow or feature flag
- Revert branch or release
- Restore previous index state
- Roll back infrastructure changes

---

## Phase 4 Addendum - Pull Request Failure Handling

### Rejected Draft Handling

```text
PR closed
Branch archived or deleted
Workflow marked rejected
Audit trail retained
Cost records retained
```

### Merge Failure Handling

```text
User notified
Branch retained
Workflow marked merge_failed
Manual resolution required
Audit record updated
```

### Conflict Resolution

The platform must not automatically resolve merge conflicts.

```text
GitHub detects conflict
User resolves conflict
Branch revalidated
Merge proceeds after validation
```

---

## Reference Documents

Operational implementation details remain in `implementationplan.md`.

That document is the authoritative source for:

- Embedding model defaults
- Rate limits
- Evaluation vault fixture
- Testing baselines
- Disaster recovery procedures
- Observability stack
- Authentication defaults
- Cost governance baselines
- Retrieval baselines
- LLM failure handling

---

## Updated Phase Order

```text
Phase -1: Architecture Decision Finalization
Phase 0: Foundation and Guardrails
Phase 1: Backend Vault Indexing
Phase 2: Responsive Web UI
Phase 3: Internal Knowledge Workflows
Phase 4: GitHub Pull Request Workflow
Phase 5: Semantic and Hybrid Retrieval
Phase 6: Monthly Knowledge Refresh
Phase 7: Controlled Note Promotion
Phase 8: Multi-Agent Orchestration
```

## Final Safety Statement

The platform is considered safe only when:

- Architecture decisions are finalized first.
- Read-only indexing precedes any LLM workflows.
- Generated outputs are isolated.
- GitHub PR review remains mandatory.
- Research workflows remain human-triggered.
- Multi-agent orchestration is implemented last.
