# Generated Note Metadata Template

## Status
Active

## Purpose
Define the required front matter metadata for all AI-generated notes in the FDE Vault Agent Platform.

## Required Metadata

Every generated artifact must include the following YAML front matter:

```yaml
---
type: agent-output
workflow: grill-me-review
status: draft
source_notes: []
created: 2026-07-24T20:00:00Z
model: claude-3-5-sonnet-20241022
llm_calls: 1
estimated_input_tokens: 8000
estimated_output_tokens: 2500
estimated_cost_usd: 0.05
approval_status: pending
tags:
  - fde-agent
  - generated
---
```

## Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Must be `agent-output` |
| `workflow` | string | Yes | Workflow type (e.g., `grill-me-review`, `implementation-plan`, `solution-brief`, `knowledge-refresh`) |
| `status` | string | Yes | Must be `draft` until approved |
| `source_notes` | array | Yes | List of source note IDs/paths used in generation |
| `created` | datetime | Yes | ISO 8601 timestamp of generation |
| `model` | string | Yes | LLM model used for generation |
| `llm_calls` | integer | Yes | Number of LLM calls made |
| `estimated_input_tokens` | integer | Yes | Estimated input tokens |
| `estimated_output_tokens` | integer | Yes | Estimated output tokens |
| `estimated_cost_usd` | decimal | Yes | Estimated cost in USD |
| `approval_status` | string | Yes | Must be `pending` until PR review |
| `tags` | array | Yes | Must include `fde-agent` and `generated` |

## Workflow-Specific Values

### Grill Me Review
```yaml
workflow: grill-me-review
```

### Implementation Plan
```yaml
workflow: implementation-plan
```

### FDE Solution Brief
```yaml
workflow: solution-brief
```

### Knowledge Refresh
```yaml
workflow: knowledge-refresh
```

## Status Transitions

```text
draft → approved → promoted
draft → rejected
```

## Phase 0 Status

- ✅ Metadata template documented
- ⏳ Backend validation to be implemented in Phase 1
- ⏳ Workflow engine to enforce metadata in Phase 3
