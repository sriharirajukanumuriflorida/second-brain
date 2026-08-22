# Write Restrictions Policy

## Status
Active

## Purpose
Define the write boundaries for the FDE Vault Agent Platform MVP to prevent accidental corruption of the existing Obsidian vault.

## Allowed Write Location

The MVP may write **only** to:

```text
14 Agent Outputs/
```

## Prohibited Write Locations

The MVP must **not** write to:

```text
03 Permanent Notes/
05 Projects/
10 FDE Playbooks/
11 Architecture Decisions/
12 Solution Patterns/
13 Governance/
99 Archive/
```

## Promotion Workflow

Content from `14 Agent Outputs/` can be promoted to higher-value folders only through:
1. Controlled promotion workflow (Phase 7)
2. GitHub pull request review
3. Manual human approval
4. Template-based transformation

## Prohibited Operations

The MVP must not perform:
- Delete operations
- Rename operations
- Overwrite operations
- Bulk edits
- Direct modifications to existing notes
- Automatic promotions

## Enforcement

- Backend must enforce write path validation
- All generated outputs must include metadata with target path
- GitHub PR workflow provides additional audit trail
- Any write outside `14 Agent Outputs/` is a critical defect

## Phase 0 Status

- ✅ Write restrictions documented
- ✅ 14 Agent Outputs/ folder created
- ⏳ Backend enforcement to be implemented in Phase 1
- ⏳ Promotion workflow to be implemented in Phase 7
