# FDE Vault Agent Platform - Implementation Plan

## Executive Summary

This project will build a cloud-hosted, mobile-accessible, GitHub-backed FDE AI/ML knowledge workflow platform using an existing Obsidian vault as the knowledge base.

The goal is not to replace Obsidian. The goal is to add a controlled AI workflow layer on top of the vault so the user can search, reason over, critique, evolve, and generate structured knowledge artifacts using an agentic workflow system.

The platform will support:

- Obsidian as the Markdown knowledge base.
- GitHub as the version-controlled cloud source of truth.
- A secure cloud backend as the controlled gateway.
- A responsive web UI usable from desktop and phone.
- Cost-controlled LLM workflows.
- GitHub pull request review for generated outputs.
- Monthly knowledge refresh workflows for external research.
- Human approval before any generated content enters the vault.

---

## What We Are Trying To Build

We are building an **FDE Vault Agent Platform**.

In this context, FDE means the knowledge base is designed around a Forward Deployed Engineer-style AI/ML workflow. The system should help with:

- AI/ML architecture thinking.
- LLM and RAG engineering notes.
- Agentic workflow design.
- Governance and security review.
- Implementation planning.
- Grill-me style critique.
- Solution briefs.
- Research refresh and knowledge evolution.
- Documentation generation.
- Long-term learning and technical memory.

The existing Obsidian vault already contains:

- Inbox notes.
- Daily notes.
- Literature notes.
- Permanent notes.
- Code snippets.
- Projects.
- Maps of Content.
- Resource library.
- Attachments.
- Templates.
- Archive.

The platform will preserve this structure and add a controlled FDE layer.

---

## Core Design Decision

The platform will use a **GitHub-centric model**.

Instead of exposing the Obsidian vault directly to the cloud platform, the vault will be stored in a private GitHub repository.

```text
Local Obsidian Vault
        |
        | git push / pull
        v
Private GitHub Repository
        |
        v
Cloud Hosted FDE Agent Platform
```

This gives the system:

- Version control.
- Rollback.
- Pull request review.
- Auditability.
- Branch-based generated outputs.
- Mobile-friendly review through GitHub and the custom UI.

---

## End-State Architecture

```text
Phone / Desktop Browser
        |
        | HTTPS
        v
Responsive Web UI
        |
        v
Cloud Hosted FastAPI Backend
        |
        v
Authentication + Authorization Layer
        |
        v
Workflow Engine
        |
        v
Retrieval Layer + Cost Guardrails
        |
        v
Private GitHub Repository Working Copy
        |
        v
Generated Draft Branches / Pull Requests
```

---

# Phase -1: Architecture Decision Finalization

## Objective

Before implementation begins, resolve the major architecture decisions that would otherwise cause ambiguity, rework, security gaps, or cost surprises.

This phase exists because the platform is cloud-hosted, mobile-accessible, GitHub-backed, and LLM-enabled. Those choices require explicit decisions before coding starts.

## Required Architecture Decision Records

Create the following ADRs before Phase 0 starts:

```text
ADR-001 Hosting Provider and Deployment Model
ADR-002 Authentication Provider and Session Strategy
ADR-003 Authorization and Role Model
ADR-004 GitHub Integration Model
ADR-005 Vault Sync and Conflict Resolution Strategy
ADR-006 Application Database Choice
ADR-007 Vector Store and Embedding Strategy
ADR-008 LLM Provider Strategy
ADR-009 Cost Governance Strategy
ADR-010 Observability and Logging Strategy
ADR-011 Disaster Recovery Strategy
ADR-012 CI/CD Strategy
```

## Recommended Default Decisions

Unless overridden later, use the following defaults:

```text
Cloud provider: Azure, if enterprise-style deployment is preferred
Frontend hosting: Azure Static Web Apps, or equivalent
Backend hosting: Azure Container Apps or Azure App Service
Application database: PostgreSQL in cloud; SQLite only for local prototype
Vector store: PostgreSQL with pgvector for cloud; FAISS only for local prototype
Secrets: Azure Key Vault, or equivalent managed secret store
Monitoring: Application Insights, or equivalent cloud observability service
CI/CD: GitHub Actions
Auth provider: GitHub OAuth for personal MVP, Microsoft Entra ID if enterprise alignment is required
GitHub integration: GitHub App preferred; fine-grained PAT acceptable only for throwaway prototype
```

## Deliverables

- ADRs created and reviewed.
- Hosting model selected.
- Auth provider selected.
- Application database selected.
- Vector store selected.
- GitHub integration model selected.
- Cost and observability strategies documented.

## Go / No-Go Gate

Proceed only if:

- The platform deployment target is known.
- Authentication model is selected.
- GitHub access model is selected.
- Database and vector store choices are documented.
- Sync/conflict model is documented.
- Cost governance method is documented.

---

# Security Approach

This is considered a private knowledge platform. Security is not optional.

The platform must follow these principles:

1. **No anonymous access**
   - Every user must authenticate.

2. **Authorization is enforced server-side**
   - Login alone is not enough.
   - APIs must enforce permissions.

3. **Vault files are not publicly exposed**
   - The UI must not directly serve raw vault folders.
   - All access must go through backend APIs.

4. **Write operations are restricted**
   - MVP writes only to `14 Agent Outputs/`.

5. **No destructive operations in MVP**
   - No delete.
   - No rename.
   - No overwrite.
   - No bulk edits.

6. **LLM output is not trusted by default**
   - All generated output is treated as draft.
   - Human review is required.

7. **GitHub pull requests are the approval mechanism**
   - No direct commits to main.
   - Each generated artifact must be traceable.

---

# Authentication and Authorization Plan

## MVP Authentication Options

Choose one before implementation:

```text
Option A: GitHub OAuth
Best for personal GitHub-backed MVP.

Option B: Microsoft Entra ID
Best for enterprise-style identity control.

Option C: Auth0 or similar managed identity provider
Best if multi-provider support is desired.
```

Do not build custom username/password authentication in the MVP.

## Recommended MVP Choice

```text
GitHub OAuth for personal MVP
Microsoft Entra ID if enterprise alignment is required
```

## Session Management

The system should use:

- Secure HTTP-only cookies when browser-based sessions are used.
- Short-lived access sessions.
- Refresh token strategy only if required by the chosen auth provider.
- Server-side session invalidation support.
- Logout endpoint.
- CSRF protection if cookie-based auth is used.

## Authorization Model

MVP can be single-user, but the backend should still use permission checks.

Recommended permissions:

```text
can_read_vault
can_sync_repo
can_run_workflow
can_approve_draft
can_create_pr
can_view_costs
can_admin_config
```

Recommended initial roles:

```text
Admin
ReadOnly
```

For MVP, only `Admin` may be enabled, but the permission model should be coded cleanly so multi-user access can be added later.

## Rate Limiting

Add rate limiting by:

```text
Authenticated user ID
IP address
Workflow type
LLM provider call volume
```

Minimum MVP protections:

- Limit workflow runs per hour.
- Require confirmation for high-context workflows.
- Block research workflow after monthly budget is reached unless admin override is enabled.

---

# Infrastructure and Operations Plan

## Hosting Decision

The implementation must explicitly choose a hosting provider before deployment.

Recommended enterprise-style default:

```text
Frontend: Azure Static Web Apps
Backend: Azure Container Apps or Azure App Service
Database: Azure Database for PostgreSQL
Secrets: Azure Key Vault
Monitoring: Application Insights
CI/CD: GitHub Actions
```

Recommended personal low-friction alternative:

```text
Frontend: Vercel or Azure Static Web Apps
Backend: Render, Fly.io, Railway, or Azure App Service
Database: Managed PostgreSQL provider
Secrets: Platform-managed environment secrets
Monitoring: Platform logs plus structured app logs
CI/CD: GitHub Actions
```

## Deployment Strategy

Use environment-based deployment:

```text
dev
staging
production
```

Minimum MVP deployment:

```text
staging
production
```

Deployment rules:

- Main branch deploys to production only after review.
- Pull requests deploy to preview/staging if supported.
- Secrets must never be stored in source control.
- Environment-specific configuration must be externalized.

## CI/CD Pipeline

GitHub Actions should perform:

```text
Install dependencies
Run linting
Run unit tests
Run integration tests where possible
Build frontend
Build backend container
Run security checks where possible
Deploy to staging
Manual approval for production deployment
Deploy to production
```

## Observability

Minimum logging and monitoring:

- API request logs.
- Authentication events.
- GitHub sync events.
- Workflow run status.
- LLM call metadata.
- Cost events.
- Errors and exceptions.
- Latency per endpoint.
- Retrieval latency.
- GitHub API failures.

Do not log raw secrets, access tokens, or full sensitive note content.

## Disaster Recovery

Disaster recovery must cover:

```text
Application database backup
Configuration backup
Secret rotation procedure
GitHub repository rollback
Platform redeployment instructions
Vector index rebuild procedure
```

The vault itself is protected primarily by GitHub, but the platform database still needs backups because it stores workflow runs, cost logs, cache metadata, and audit records.

---

# Vault Sync and Conflict Resolution Strategy

## Source of Truth

```text
GitHub private repository = cloud source of truth
Local Obsidian vault = local editing workspace
Backend clone/working copy = disposable runtime copy
```

The backend working copy must be treated as disposable. It can always be rebuilt from GitHub.

## Sync Rules

- Backend fetches latest main before indexing.
- Backend fetches latest main before running a workflow.
- Backend never directly commits to main.
- Every approved generated artifact is committed to a unique branch.
- Every generated branch opens a pull request.
- GitHub handles merge conflicts through the PR process.

## Local Edit Scenario

If the user edits the vault locally while the platform runs:

```text
1. User edits locally in Obsidian.
2. User pushes changes to GitHub.
3. Backend fetches latest main before next sync or workflow.
4. If a generated PR conflicts, GitHub marks the conflict.
5. User resolves conflict manually in GitHub or locally.
```

The backend must not try to automatically resolve content conflicts.

## Incremental Sync Strategy

Phase 1 may use a full scan.

Phase 5 must add incremental sync using:

```text
file_path
file_hash
last_commit_sha
last_indexed_at
frontmatter_hash
content_hash
embedding_hash
```

If file hash is unchanged, skip re-parsing and re-embedding.

## `.obsidian` Folder Handling

Default MVP behavior:

```text
Ignore .obsidian/
```

Do not index:

```text
.obsidian/workspace.json
.obsidian/plugins/
.obsidian/cache
.obsidian/appearance.json
```

Future exception:

- Selected templates may be read later if explicitly configured.
- Plugin state and workspace data should remain ignored.

## Branch Collision Prevention

Use unique branch names:

```text
agent-output/{workflow}/{yyyyMMdd-HHmmss}-{short_run_id}
```

Example:

```text
agent-output/grill-me/20260724-1955-a92f13
```

---

# Cost-Control Approach

Because LLMs are involved, cost control must be part of the architecture from day one.

The platform must distinguish between:

## Low-Cost Internal Workflows

These use only the vault as context.

Examples:

- Grill Me Review.
- Implementation Plan Generator.
- FDE Solution Brief.
- Vault search.
- Note summarization.

These should use one LLM call by default.

## Higher-Cost Research Workflows

These use the vault plus external research.

Examples:

- Monthly Knowledge Refresh.
- Technology Radar.
- Research Gap Analysis.

These should be manually triggered, require cost confirmation, and run only occasionally.

## Cost Categories To Track

Track more than LLM cost:

```text
LLM token cost
Embedding cost
External search/API cost
GitHub API usage where applicable
Hosting cost
Database cost
Storage cost
Monitoring/logging cost
Bandwidth cost
Secret management cost
```

## Budget Enforcement

Minimum controls:

```text
Monthly total budget
Monthly LLM budget
Monthly embedding budget
Monthly research workflow budget
Per-workflow max estimated cost
Warnings at 50%, 80%, and 100%
Block high-cost workflows after budget exceeded unless admin override is enabled
```

## Cost Attribution

Even if the MVP is single-user, store cost records with:

```text
user_id
workflow_id
repo_id
organization_id nullable
model
provider
input_tokens
output_tokens
estimated_cost
actual_cost if available
created_at
```

---

# LLM Usage Rules

Use deterministic code for:

- GitHub sync.
- Folder scanning.
- Markdown parsing.
- YAML extraction.
- Tag extraction.
- Backlink extraction.
- File hash detection.
- Search ranking.
- Audit logs.
- Cost logs.
- Diff generation.
- Pull request creation.

Use LLMs only for:

- Reasoning.
- Synthesis.
- Critique.
- Architecture review.
- Implementation planning.
- Knowledge refresh analysis.
- Draft generation.

The LLM must not be used as a file parser, folder scanner, or metadata extractor.

---

# Technical Decisions

## Application Database

Recommended:

```text
Cloud deployment: PostgreSQL
Local prototype: SQLite
```

Rationale:

- SQLite is simple for local prototyping.
- PostgreSQL is more appropriate for cloud hosting, concurrent requests, workflow history, audit logs, and future multi-user needs.

## Vector Store

Recommended:

```text
Cloud deployment: PostgreSQL with pgvector
Local prototype: FAISS
```

Avoid managed vector databases in MVP unless scale demands it.

## Embedding Model Strategy

Do not hardcode embedding logic tightly to one provider.

Store the following per embedded chunk:

```text
embedding_model
embedding_model_version
chunk_hash
file_hash
embedded_at
embedding_dimensions
```

## Re-Embedding Strategy

If the embedding model changes:

```text
Mark old embeddings as stale.
Do not immediately re-embed the entire vault.
Re-embed lazily on access or through a controlled admin job.
Log estimated embedding cost before bulk re-embedding.
```

## LLM Provider Strategy

Implement a provider abstraction.

Supported later:

```text
Claude
Azure OpenAI
OpenAI
NASH LLM
Local model
```

Provider config must be externalized and stored securely.

---

# Testing and Evaluation Strategy

## Unit Tests

Required for:

```text
Markdown parser
YAML parser
Tag extractor
Backlink extractor
Folder rule enforcement
Search ranking
Cost estimator
Git branch naming
Path safety validation
```

## Integration Tests

Required for:

```text
GitHub clone/fetch mocked or test repo
Index rebuild
Search API
Workflow API
Draft creation
PR creation mocked
Auth-protected routes
```

## End-to-End Tests

Required for:

```text
Login
Search note
Preview note
Run workflow
Preview draft
Approve draft
Create PR
View workflow history
```

## Retrieval Quality Metrics

Maintain a small evaluation vault with known expected results.

Track:

```text
precision_at_k
recall_at_k
source_relevance_score
manual_rating
retrieval_regression_failures
```

## LLM Output Evaluation

Each workflow should have regression prompts and expected structural checks.

Minimum checks:

```text
Output includes required headings
Output includes Sources Used
Output does not claim unsupported facts
Output does not instruct direct edits to existing notes
Output respects non-goals
Output includes cost/security risks for Grill Me workflow
Output includes phase boundaries for Implementation Plan workflow
```

Use deterministic validators first. Add LLM-as-judge only later and only with cost awareness.

---

# Failure Handling and Edge Cases

## Workflow Status Model

Every workflow run must have a status:

```text
queued
running
retrieval_failed
llm_failed
partial_output_available
draft_generated
approval_pending
approved
pr_creation_failed
pr_created
rejected
cancelled
```

## LLM Failure Handling

If the LLM fails:

- Store workflow status as `llm_failed`.
- Store non-sensitive error metadata.
- Preserve retrieved source IDs.
- Do not create a draft unless valid output exists.
- Allow retry only with explicit user action.

## Partial Output Recovery

If partial output is available:

- Store it as partial output.
- Mark it clearly as incomplete.
- Do not allow PR creation from incomplete output unless user explicitly converts it to draft.

## Large Vault Performance

For vaults with 1000+ notes:

- Use pagination.
- Use incremental indexing.
- Use file hashes.
- Use background jobs for sync and indexing.
- Do not scan the entire vault on each request.
- Cache search indexes.

## Simultaneous Workflows

Prevent branch collisions using unique run IDs.

Prevent race conditions by:

- Locking per workflow run.
- Fetching latest main before branch creation.
- Validating target output path uniqueness.

---

# Implementation Defaults and Operational Baselines

## Purpose

This section removes remaining ambiguity before handing the plan to an implementation agent. These defaults are not intended to be permanent enterprise standards. They are MVP baselines that allow the platform to be built safely, tested consistently, and operated with predictable cost and reliability.

If a future ADR overrides any default below, the ADR becomes the source of truth.

---

## 1. Default Embedding Model

## MVP Decision

The platform must support embedding provider abstraction, but it should still define a practical MVP default.

Recommended defaults:

```text
Cloud MVP default:
Use a low-cost, general-purpose embedding model such as text-embedding-3-small or an equivalent approved model.

Enterprise/internal default:
Use an approved internal embedding model if NASH or another enterprise AI platform provides one.

Local prototype default:
Use sentence-transformers/all-MiniLM-L6-v2 or equivalent lightweight local embedding model.
```

## Design Rules

The embedding model must not be hardcoded into retrieval logic.

Every embedded chunk must store:

```text
embedding_provider
embedding_model
embedding_model_version
embedding_dimensions
chunk_hash
file_hash
embedded_at
```

## Re-Embedding Baseline

If the embedding model changes:

```text
1. Mark existing embeddings as stale.
2. Do not automatically re-embed the entire vault.
3. Re-embed lazily when notes are accessed or through a controlled admin job.
4. Estimate and display cost before bulk re-embedding.
5. Log all re-embedding activity.
```

## MVP Acceptance Criteria

```text
Embedding model is configurable.
Embedding metadata is stored per chunk.
Changing the embedding model does not break existing search.
Bulk re-embedding requires explicit admin action.
```

---

## 2. MVP Rate Limits

## Purpose

Rate limits protect the platform from accidental overuse, runaway LLM cost, brute-force login attempts, and excessive mobile-triggered workflow execution.

## Default Rate Limits

```yaml
rate_limits:
  search:
    limit: 60
    window: 1 minute

  note_preview:
    limit: 120
    window: 1 minute

  vault_sync:
    limit: 5
    window: 1 hour

  internal_workflow:
    limit: 10
    window: 1 hour

  high_context_workflow:
    limit: 3
    window: 24 hours

  knowledge_refresh:
    limit: 2
    window: 30 days

  failed_login:
    limit: 5
    window: 15 minutes
```

## Enforcement Rules

Rate limiting must be enforced by:

```text
authenticated_user_id
IP address
workflow_type
LLM provider call volume
```

## Admin Override Rules

```text
Admin override may be allowed for workflow and budget limits.
Admin override must not bypass failed-login protection.
Admin override events must be audit logged.
```

## MVP Acceptance Criteria

```text
Search and preview endpoints are rate limited.
Workflow execution endpoints are rate limited.
Knowledge Refresh cannot be run repeatedly without explicit override.
Failed login throttling is enforced.
Rate-limit violations are logged.
```

---

## 3. Evaluation Vault Fixture

## Purpose

The platform needs a small deterministic evaluation vault so search, retrieval, workflow formatting, and LLM output structure can be regression tested before using the real vault.

## Required Fixture Structure

Create the following test fixture:

```text
tests/fixtures/evaluation-vault/
├── 03 Permanent Notes/
│   ├── RAG Evaluation Metrics.md
│   ├── Agent Memory Patterns.md
│   ├── Context Engineering Basics.md
│   └── Vector Database Tradeoffs.md
├── 05 Projects/
│   └── Sample AI Project.md
├── 06 Maps of Content/
│   └── LLM Engineering MOC.md
├── 10 FDE Playbooks/
│   └── Architecture Review Playbook.md
├── 13 Governance/
│   └── PII Handling in LLM Workflows.md
└── 14 Agent Outputs/
```

## Required Test Notes

Each fixture note should include:

```text
YAML front matter
tags
at least one backlink
at least one heading
short body content
```

Example front matter:

```yaml
---
type: permanent-note
domain: llm-engineering
status: active
tags:
  - rag
  - evaluation
  - fde-agent-test
---
```

## Retrieval Test Cases

```yaml
retrieval_tests:
  - name: rag_evaluation_query
    query: How should I evaluate a RAG system?
    expected_sources:
      - 03 Permanent Notes/RAG Evaluation Metrics.md
      - 06 Maps of Content/LLM Engineering MOC.md

  - name: agent_memory_risk_query
    query: What are the risks of agent memory?
    expected_sources:
      - 03 Permanent Notes/Agent Memory Patterns.md
      - 13 Governance/PII Handling in LLM Workflows.md

  - name: ai_project_implementation_plan_query
    query: Create an implementation plan for the sample AI project
    expected_sources:
      - 05 Projects/Sample AI Project.md
      - 10 FDE Playbooks/Architecture Review Playbook.md
```

## Retrieval Quality Baseline

Initial MVP thresholds:

```text
precision@5 >= 0.60
required_source_found@5 = true for golden test cases
archive_notes_retrieved = false unless explicitly requested
obsidian_internal_files_retrieved = false
```

## LLM Output Evaluation Baseline

For each workflow, deterministic validators should check:

```text
Required headings are present.
Sources Used section is present.
Output does not instruct direct edits to existing notes.
Output does not write outside 14 Agent Outputs.
Output respects workflow-specific format.
Output includes cost or risk consideration when required.
```

Use LLM-as-judge only later and only with cost tracking.

## MVP Acceptance Criteria

```text
Evaluation vault exists.
Unit and integration tests can run against it.
Retrieval tests are repeatable.
Workflow output validators exist.
Regression failures are visible in CI.
```

---

## 4. Disaster Recovery Testing Procedure

## Purpose

The vault is protected by GitHub, but the platform itself still has recoverable state: database records, workflow history, cost logs, audit logs, configuration, and cache metadata.

The vector index is rebuildable and must not be treated as the system of record.

## Recovery Objectives

MVP targets:

```text
Recovery Time Objective: 4 hours
Recovery Point Objective: 24 hours
```

## Critical Recovery Assets

```text
Private GitHub vault repository
Application database backup
Environment configuration
Secrets and key references
Deployment pipeline
Workflow audit logs
Cost logs
```

## DR Test Procedure

Run this procedure before production launch and then at least quarterly:

```text
1. Export or verify latest application database backup.
2. Simulate database loss in staging.
3. Restore database from backup.
4. Rebuild backend working copy from GitHub.
5. Rebuild keyword search index.
6. Rebuild vector index if enabled.
7. Verify workflow history is restored.
8. Verify cost logs are restored.
9. Verify audit logs are restored.
10. Verify user login works.
11. Verify vault search works.
12. Verify a workflow can run in staging.
13. Verify no generated PR references are lost.
14. Document recovery duration and issues.
```

## DR Acceptance Criteria

```text
Platform can be restored in staging from backups.
Vault can be rebuilt from GitHub.
Search index can be regenerated.
Vector index can be regenerated.
Workflow and cost history are preserved.
Recovery duration is measured and documented.
```

---

## 5. Observability Stack

## Purpose

The platform must be observable enough to troubleshoot sync failures, workflow failures, LLM cost spikes, authentication issues, GitHub API failures, and deployment problems.

## Default Azure-Oriented Observability Stack

Use this stack if deploying to Azure:

```text
Application monitoring: Azure Application Insights
Platform and container logs: Azure Monitor Logs
Frontend diagnostics: Azure Static Web Apps diagnostics or Application Insights browser telemetry
Database metrics: Azure PostgreSQL metrics
Secrets audit trail: Azure Key Vault diagnostic logs
CI/CD logs: GitHub Actions logs
Structured application logs: JSON logs emitted by backend
```

## Personal / Non-Azure Alternative

If using a lightweight personal hosting provider:

```text
Application logs: Structured JSON logs
Error tracking: Sentry
Uptime checks: Better Stack, UptimeRobot, or provider health checks
Metrics: Provider-native metrics
CI/CD logs: GitHub Actions logs
Database metrics: Managed database provider dashboard
```

## Required Log Events

The backend must log:

```text
auth.login_success
auth.login_failed
auth.logout
vault.sync_started
vault.sync_completed
vault.sync_failed
index.scan_started
index.scan_completed
index.scan_failed
search.query_executed
workflow.started
workflow.retrieval_completed
workflow.llm_started
workflow.llm_failed
workflow.draft_generated
workflow.approved
workflow.rejected
github.branch_created
github.pr_created
github.pr_failed
cost.estimated
cost.budget_warning
rate_limit.exceeded
```

## Logging Rules

```text
Do not log secrets.
Do not log access tokens.
Do not log full sensitive note content.
Log note IDs, paths, hashes, and source references where needed.
Use correlation IDs for workflow runs.
Use structured JSON logs.
```

## Minimum Alerting Rules

```text
Trigger alert on repeated login failures.
Trigger alert on workflow failure rate spike.
Trigger alert on GitHub sync failure.
Trigger alert on budget threshold crossing at 80% and 100%.
Trigger alert on backend 5xx error spike.
Trigger alert on database connectivity failure.
```

## MVP Acceptance Criteria

```text
Logs are structured.
Workflow runs have correlation IDs.
Errors are visible in monitoring.
Cost threshold warnings are visible.
GitHub sync failures are visible.
Deployment logs are available from CI/CD.
```

---

# MVP Non-Goals

The MVP must not include:

```text
Native iOS app
Native Android app
Obsidian plugin
Autonomous multi-agent loops
Auto-editing existing notes
Deleting notes
Renaming notes
Bulk metadata rewriting
Attachment indexing
PDF/image ingestion
SharePoint ingestion
Direct internet research for every query
Continuous background research
Autonomous knowledge updates
Direct commits to main
Team collaboration features
```

---

# Alternatives Considered

## Obsidian Plugin First

Pros:

- Local-first.
- Direct vault access.
- No cloud hosting required.
- Lower infrastructure cost.

Cons:

- Poor fit for phone/browser access.
- Harder to run cloud workflows.
- Harder to enforce centralized auth.
- Harder to use GitHub PR workflow as approval mechanism.
- Harder to host long-running research workflows.

Decision:

```text
Reject plugin-first for MVP.
Consider later as a companion UI.
```

## Existing PKM Tools With AI

Pros:

- Faster to adopt.
- Less custom engineering.
- Built-in AI features may already exist.

Cons:

- Less control over GitHub PR workflow.
- Less control over FDE-specific workflows.
- Less control over cost governance.
- Less control over vault-specific retrieval priority.
- Less control over human-approved knowledge promotion.

Decision:

```text
Reject as primary platform.
Existing tools may be studied for feature inspiration.
```

---

# Number Of Phases

The platform will be implemented in **ten phases**:

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

Phase -1 is included because technical decisions must be resolved before coding.
Phase 0 is included because the vault and repository must be prepared before implementation begins.

---

# Phase 0: Foundation and Guardrails

## Objective

Prepare the vault, GitHub repository, folder boundaries, cost policy, and safety rules.

## Key Work

- Ensure the Obsidian vault is backed up.
- Store the vault in a private GitHub repository.
- Add FDE-specific folders:

```text
10 FDE Playbooks/
11 Architecture Decisions/
12 Solution Patterns/
13 Governance/
14 Agent Outputs/
```

- Define generated note metadata.
- Define write restrictions.
- Define cost limits.
- Define workflow boundaries.
- Verify backup and restore process.
- Validate `.gitignore` rules.
- Confirm `.obsidian/` handling.

## Folder Creation

Folder creation may be manual for initial setup, but a script should be provided later:

```text
scripts/setup_vault_folders.py
```

The script should:

- Create missing FDE folders.
- Avoid deleting or moving existing folders.
- Print a summary of created/skipped folders.

## Backup Verification

Before implementation begins:

```text
1. Confirm vault exists locally.
2. Confirm local backup exists.
3. Confirm private GitHub repo exists.
4. Push latest vault contents to GitHub.
5. Clone repo into a clean temporary directory.
6. Verify notes, folder structure, and templates are present.
7. Confirm ignored files are not pushed.
```

## GitHub Repository Initialization

Required settings:

- Repository must be private.
- Main branch should be protected where practical.
- Agent must not push directly to main.
- Generated content must go through branches and PRs.
- Large datasets and binaries should remain ignored unless explicitly allowed.

## Success Criteria

- GitHub repository is private.
- Vault structure is ready.
- `14 Agent Outputs/` exists.
- Generated content has a known destination.
- No automatic writes are allowed outside `14 Agent Outputs/`.
- Backup and restore check has passed.

---

# Phase 1: Backend Vault Indexing

## Objective

Build the backend foundation that can sync, scan, parse, and search the vault.

## Key Work

- Build FastAPI backend.
- Implement GitHub repo sync or clone.
- Parse Markdown files.
- Extract YAML front matter.
- Extract tags and backlinks.
- Store metadata in the selected application database.
- Build keyword search.
- Add audit logging.
- Add sync status endpoint.
- Add index status endpoint.

## LLM Usage

None.

## Success Criteria

- Backend can index the vault.
- Search returns useful results.
- Metadata extraction works.
- No write operations exist.
- No LLM calls are made.
- `.obsidian/`, attachments, archive, and ignored files are handled according to policy.

---

# Phase 2: Responsive Web UI

## Objective

Build a secured responsive UI that works on desktop and phone.

## Key Work

- Build React UI.
- Add login.
- Build dashboard.
- Build vault search screen.
- Build note preview.
- Build mobile-friendly layout.
- Add workflow launcher placeholders.
- Add basic cost dashboard placeholder.
- Add workflow history placeholder.

## LLM Usage

None.

## Success Criteria

- User can access the platform from phone.
- Login is required.
- Vault search works in the UI.
- Notes render clearly.
- Raw vault files are not exposed.

---

# Phase 3: Internal Knowledge Workflows

## Objective

Add the first three internal LLM workflows using only the vault as context.

## Workflows

```text
1. Grill Me Review
2. Implementation Plan Generator
3. FDE Solution Brief
```

## Key Work

- Add workflow engine.
- Add LLM provider abstraction.
- Add workflow prompts.
- Add retrieval caps.
- Add cost estimation.
- Add draft preview.
- Add source citation display.
- Add workflow status tracking.
- Add failure handling.
- Add approval step.

## LLM Usage

One LLM call per workflow by default.

## Success Criteria

- Each workflow generates useful Markdown.
- Sources are displayed.
- Estimated cost is displayed and logged.
- Output remains draft until approved.
- No existing notes are edited.
- Failed workflows are recoverable or retryable by explicit user action.

---

# Phase 4: GitHub Pull Request Workflow

## Objective

Make GitHub the approval and audit mechanism for generated outputs.

## Key Work

- Create branch per approved draft.
- Commit generated Markdown under `14 Agent Outputs/`.
- Open pull request.
- Add workflow metadata to PR description.
- Add cost estimate to PR description.
- Add source notes to PR description.
- Prevent branch collisions.
- Handle PR creation failure cleanly.

## Success Criteria

- No direct commits to main.
- Pull requests are created successfully.
- PRs can be reviewed from phone.
- Every generated output is traceable.
- Branch names are unique.

---

# Phase 5: Semantic and Hybrid Retrieval

## Objective

Improve retrieval quality using embeddings and hybrid search.

## Key Work

- Add embeddings pipeline.
- Add vector store.
- Add file hash-based embedding cache.
- Add hybrid ranking with keyword + metadata + semantic search.
- Log embedding cost.
- Add retrieval evaluation set.
- Add re-embedding strategy.

## Success Criteria

- Retrieval quality improves.
- Unchanged files are not re-embedded.
- Embedding costs are tracked.
- Results remain explainable.
- Retrieval regression tests pass.

---

# Phase 6: Monthly Knowledge Refresh

## Objective

Add a manually triggered research workflow that compares vault knowledge against current external information.

## Key Work

- Select note, folder, MOC, topic, or project.
- Analyze current vault understanding.
- Search external sources.
- Summarize findings.
- Compare current notes against new information.
- Generate Knowledge Refresh Report.
- Show cost warning before execution.
- Create PR with recommendations.

## Usage Frequency

Monthly or occasional only.

## Success Criteria

- User explicitly triggers the workflow.
- Cost warning appears before execution.
- External sources are captured.
- Existing notes are not automatically updated.
- Recommendations are generated under `14 Agent Outputs/`.

---

# Phase 7: Controlled Note Promotion

## Objective

Allow approved generated outputs to be promoted into higher-value vault folders.

## Promotion Targets

```text
03 Permanent Notes/
10 FDE Playbooks/
11 Architecture Decisions/
12 Solution Patterns/
13 Governance/
```

## Key Work

- Select approved output.
- Choose destination type.
- Apply template.
- Generate proposed promoted note.
- Validate target path.
- Open PR for review.

## Success Criteria

- Promotion is user-initiated.
- Existing notes are not overwritten.
- PR review is mandatory.
- Original generated output remains traceable.

---

# Phase 8: Multi-Agent Orchestration

## Objective

Introduce true multi-agent workflows only after the simpler workflows prove value.

## Possible Agents

```text
Discovery Agent
Architect Agent
Governance Agent
Critic Agent
Documentation Agent
Prompt Agent
Knowledge Curator Agent
```

## Key Work

- Add opt-in multi-agent mode.
- Add cost preview before execution.
- Log every agent step.
- Prevent autonomous vault mutation.
- Add multi-agent evaluation checks.

## Success Criteria

- Multi-agent mode is opt-in.
- Cost is visible before execution.
- Every LLM call is logged.
- No autonomous note mutation is allowed.

---

# Is This A Safe Approach?

Yes, this is a safe approach if the phase boundaries are enforced.

The safety comes from these controls:

1. **Architecture decisions before coding**
   - Hosting, auth, database, vector store, sync, cost, and observability decisions are resolved first.

2. **Read-first implementation**
   - The first backend phase only scans, parses, indexes, and searches.

3. **No LLM in early phases**
   - The system proves it can understand the vault before any model is added.

4. **No destructive writes**
   - The MVP cannot delete, rename, overwrite, or bulk-edit notes.

5. **Generated outputs are isolated**
   - AI-generated content goes only into `14 Agent Outputs/`.

6. **GitHub pull request review**
   - Generated content is reviewed before merge.

7. **Cost controls are explicit**
   - Token budgets, LLM call limits, caching, alerts, and monthly budgets are part of the design.

8. **Research is manual and monthly**
   - Expensive external research workflows are not automatic.

9. **Multi-agent orchestration is last**
   - The highest-cost, highest-complexity capability is deferred until the platform proves value.

The unsafe version of this project would be:

```text
Build all agents immediately
Let the agent edit notes directly
Run research automatically
Skip GitHub review
Skip cost logging
Expose raw vault files
Use LLMs for everything
Skip auth and rate limiting
Skip backup verification
Skip deployment and monitoring planning
```

This plan avoids those mistakes.

---

# Recommended First Implementation Prompt

Use this prompt with the coding agent for the first implementation cycle:

```text
You are implementing Phase -1 documentation support, Phase 0, and Phase 1 only for the FDE Vault Agent Platform.

Do not implement LLM workflows.
Do not implement Knowledge Refresh.
Do not implement multi-agent orchestration.
Do not write to existing vault notes.
Do not create GitHub pull requests yet.
Do not index attachments.
Do not expose raw vault files publicly.
Do not implement custom username/password authentication.

Build only:
1. Project configuration structure.
2. ADR templates for architecture decisions.
3. GitHub repository sync or local repository scanner.
4. Markdown file scanner.
5. YAML front matter parser.
6. Tag extractor.
7. Backlink extractor.
8. Database schema for note metadata, sync events, audit logs, and cost records.
9. Keyword search.
10. FastAPI endpoints for health, sync, status, notes, folders, and search.
11. Audit logging.
12. Unit tests for scanner, parser, metadata extraction, folder rules, and search.
13. A small sample vault fixture for regression testing.

The implementation must preserve the existing vault structure and must not mutate vault files.
```

---

# Final Recommendation

Implement this platform slowly and deliberately.

The corrected build sequence is:

```text
Decide architecture
Prepare vault and repo
Read safely
Index safely
Search safely
Add UI
Add low-cost workflows
Add GitHub PR approval
Add semantic retrieval
Add monthly research
Add controlled promotion
Add multi-agent orchestration last
```

This gives a realistic path from a strong Obsidian vault to a governed, mobile-accessible, AI-assisted FDE knowledge platform without letting scope, cost, operations, or automation risk get out of control.
