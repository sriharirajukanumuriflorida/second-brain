# ADR-004: GitHub Integration Model

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform is GitHub-centric: the vault is stored in a private GitHub repository, generated artifacts are introduced through branches and pull requests, and GitHub serves as the approval mechanism. The platform must integrate with GitHub for repository cloning, branch creation, pull request management, and webhook handling.

## Decision
**Selected Approach: Phased Implementation**
- Phase 0-1: Use fine-grained Personal Access Token (PAT) for local prototype
- Phase 4+: Migrate to GitHub App for production-grade integration
- GitHub App provides better security, rate limits, and organization support for production

**Integration Capabilities:**
- Clone or fetch private GitHub repository
- Create branches for generated outputs
- Commit generated Markdown to branches
- Open pull requests with metadata
- Handle webhook events for PR status
- Manage branch naming and collision prevention

**Branch Naming Convention:**
```text
agent-output/{workflow}/{yyyyMMdd-HHmmss}-{short_run_id}
```

Example: `agent-output/grill-me/20260724-1955-a92f13`

## Alternatives Considered

### Personal Access Token (PAT) Only
- **Pros:** Simple to implement, no app registration
- **Cons:** Security risk, rate limits, no organization support, acceptable only for prototype

### Git Command-Line Integration
- **Pros:** Full git capabilities
- **Cons:** Requires shell access, security risk, harder to manage in cloud environment

### Direct API Without Branches
- **Pros:** Simpler workflow
- **Cons:** No PR review mechanism, violates governance model, rejected

## Consequences
- GitHub App requires registration and installation
- Branch naming follows convention to prevent collisions
- Pull requests are the approval mechanism
- No direct commits to main branch
- Generated artifacts are traceable through PR history
- GitHub handles merge conflicts through PR process

## Cost Impact
- GitHub App: free for personal repositories
- GitHub API usage within free tier limits for MVP
- No additional infrastructure cost
- Rate limits may require caching for larger vaults

## Security Impact
- GitHub App provides scoped permissions
- No hardcoded credentials in source code
- Secrets managed through vault or environment variables
- Fine-grained PAT for prototype only, not production
- Branch-based workflow prevents direct main branch mutations
- PR review provides human approval gate

## Operational Impact
- GitHub App installation required for production
- Branch management is automated
- PR creation is automated with metadata
- Merge conflicts resolved manually by user
- GitHub serves as audit trail for all generated content
- Rate limiting must be considered for large-scale operations

## Follow-Up Actions
- [x] Select phased approach (PAT for prototype, GitHub App for production)
- [ ] Generate fine-grained PAT for Phase 0-1
- [ ] Register GitHub App for Phase 4+
- [ ] Configure GitHub App permissions (repo, pull requests)
- [ ] Implement GitHub client for clone/fetch operations
- [ ] Implement branch creation with naming convention
- [ ] Implement PR creation with metadata template
- [ ] Implement webhook handling for PR status updates
- [ ] Test branch collision prevention
