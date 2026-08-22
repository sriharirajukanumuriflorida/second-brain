# ADR-009: Cost Governance Strategy

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform uses LLMs, embeddings, and external APIs which incur costs. Without cost controls, runaway LLM usage, excessive embedding operations, or frequent research workflows could lead to unexpected expenses. Cost governance must be part of the architecture from day one.

## Decision
**Cost Categories to Track:**
- LLM token cost
- Embedding cost
- External search/API cost
- GitHub API usage (where applicable)
- Hosting cost
- Database cost
- Storage cost
- Monitoring/logging cost
- Bandwidth cost
- Secret management cost

**Budget Enforcement:**
- Monthly total budget
- Monthly LLM budget
- Monthly embedding budget
- Monthly research workflow budget
- Per-workflow max estimated cost
- Warnings at 50%, 80%, and 100%
- Block high-cost workflows after budget exceeded unless admin override enabled

**Cost Attribution:**
Even for single-user MVP, store cost records with:
```text
user_id
workflow_id
repo_id
organization_id (nullable)
model
provider
input_tokens
output_tokens
estimated_cost
actual_cost (if available)
created_at
```

**Workflow Cost Classification:**
- Low-Cost Internal Workflows: Grill Me Review, Implementation Plan Generator, FDE Solution Brief, Vault search, Note summarization (one LLM call by default)
- Higher-Cost Research Workflows: Monthly Knowledge Refresh, Technology Radar, Research Gap Analysis (manually triggered, cost confirmation required, occasional only)

**Rate Limits (Cost Control):**
- Search: 60/minute
- Note preview: 120/minute
- Vault sync: 5/hour
- Internal workflow: 10/hour
- High-context workflow: 3/24 hours
- Knowledge refresh: 2/30 days
- Failed login: 5/15 minutes

## Alternatives Considered

### No Cost Controls
- **Pros:** Simpler implementation
- **Cons:** Unpredictable costs, potential runaway expenses, rejected per requirements

### Cost Controls Only at End of Month
- **Pros:** Simpler implementation
- **Cons:** No real-time protection, surprise bills, rejected

### Per-Request Cost Only (No Budgets)
- **Pros:** Granular tracking
- **Cons:** No aggregate budget enforcement, rejected

## Consequences
- Cost tracking is mandatory for all LLM and embedding operations
- Budget enforcement blocks high-cost workflows when exceeded
- Rate limits prevent runaway usage
- Admin override available for emergency situations
- Cost attribution enables future multi-user cost allocation
- Warnings provide visibility before blocking

## Cost Impact
- Budget enforcement prevents unexpected expenses
- Rate limits reduce risk of runaway costs
- Cost tracking enables optimization
- Admin override provides emergency flexibility
- Budgets can be adjusted based on actual usage patterns

## Security Impact
- Cost tracking does not expose sensitive content
- Budget enforcement is a safety mechanism
- Admin override events are audit logged
- Cost records do not contain vault content

## Operational Impact
- Cost governance requires monitoring and alerting
- Budget adjustments require coordination
- Cost tracking enables capacity planning
- Rate limits may affect user experience if too restrictive
- Cost data supports business case for platform value

## Follow-Up Actions
- [x] Define initial budget values ($10 total, $7 LLM, $2 embedding, $1 research)
- [ ] Implement cost tracking for all LLM calls
- [ ] Implement cost tracking for embedding operations
- [ ] Implement budget enforcement logic
- [ ] Implement rate limiting per workflow type
- [ ] Implement cost warning alerts (50%, 80%, 100%)
- [ ] Implement admin override with audit logging
- [ ] Create cost dashboard for visibility
