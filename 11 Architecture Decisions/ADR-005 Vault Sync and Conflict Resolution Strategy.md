# ADR-005: Vault Sync and Conflict Resolution Strategy

## Status
Proposed

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform must synchronize with a private GitHub repository containing the Obsidian vault. The user may edit the vault locally in Obsidian while the platform runs, creating potential conflicts. The platform must handle sync, indexing, and conflict resolution without data loss or corruption.

## Decision
**Source of Truth Model:**

```text
GitHub private repository = cloud source of truth
Local Obsidian vault = local editing workspace
Backend clone/working copy = disposable runtime copy
```

**Sync Rules:**
- Backend fetches latest main before indexing
- Backend fetches latest main before running workflow
- Backend never directly commits to main
- Every approved generated artifact is committed to a unique branch
- Every generated branch opens a pull request
- GitHub handles merge conflicts through PR process

**Local Edit Scenario:**
1. User edits locally in Obsidian
2. User pushes changes to GitHub
3. Backend fetches latest main before next sync or workflow
4. If generated PR conflicts, GitHub marks the conflict
5. User resolves conflict manually in GitHub or locally

**Incremental Sync Strategy (Phase 5):**
- Use file hash detection to skip unchanged files
- Track: file_path, file_hash, last_commit_sha, last_indexed_at, frontmatter_hash, content_hash, embedding_hash
- If file hash unchanged, skip re-parsing and re-embedding

**.obsidian Folder Handling:**
- Default: Ignore .obsidian/
- Do not index: workspace.json, plugins/, cache, appearance.json
- Future exception: Selected templates may be read if explicitly configured

## Alternatives Considered

### Direct Vault Access (No GitHub)
- **Pros:** Simpler, no sync complexity
- **Cons:** No version control, no PR review, violates governance model, rejected

### Automatic Conflict Resolution
- **Pros:** Faster workflow
- **Cons:** Risk of data loss, incorrect merges, rejected per safety requirements

### Real-Time Sync with Webhooks
- **Pros:** Immediate updates
- **Cons:** Complexity, race conditions, overkill for MVP

## Consequences
- Backend working copy is disposable and can be rebuilt
- No automatic conflict resolution
- User must resolve conflicts manually
- GitHub is the single source of truth
- Incremental sync reduces re-processing overhead
- .obsidian folder is excluded from indexing

## Cost Impact
- No direct cost impact
- Incremental sync reduces compute costs for large vaults
- GitHub API usage within free tier for MVP

## Security Impact
- No direct vault file exposure to public internet
- All access goes through backend APIs
- GitHub private repository ensures vault security
- Backend working copy isolation prevents cross-contamination
- Manual conflict resolution prevents automated data corruption

## Operational Impact
- Sync must happen before indexing and workflows
- Conflict resolution is manual but clear
- Incremental sync improves performance for large vaults
- .obsidian exclusion reduces noise in index
- Backend can recover from sync failures by re-cloning

## Follow-Up Actions
- [ ] Implement GitHub clone/fetch operations
- [ ] Implement file hash calculation
- [ ] Implement incremental sync logic
- [ ] Implement .obsidian folder exclusion
- [ ] Document conflict resolution process for users
- [ ] Test local edit + platform workflow scenario
- [ ] Implement sync status tracking and error handling
