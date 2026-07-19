# AI Week 22a LLM Observability Attribute Reference

Canonical OpenTelemetry attributes for an LLM/RAG request:

| Attribute | Type | Purpose | Sensitivity |
|---|---:|---|---|
| `tenant.id` | string | tenant correlation, budgets, blast-radius analysis | internal identifier; hash if needed |
| `user.hash` | string | user-level debugging without raw identity | hashed/pseudonymous |
| `feature.name` | string | chargeback and product analytics | low |
| `ai.prompt_hash` | string | identify prompt body without logging it | low if one-way hash |
| `ai.prompt_version` | string | rollback and release analysis | low |
| `ai.model_deployment` | string | route, quota, latency, and cost correlation | low |
| `ai.embedding_model` | string | retrieval drift and index compatibility | low |
| `ai.index_version` | string | retrieval rollback and drift analysis | low |
| `ai.retrieved_doc_ids` | string/list | citation debugging and ACL verification | medium; avoid titles/snippets |
| `ai.tokens.prompt` / `ai.tokens.completion` | int | cost and budget accounting | low |
| `ai.cost_usd` | float | request, tenant, and feature spend | low/financial |
| `ai.groundedness_score` | float | quality SLO and release gate | low |
| `ai.safety_flags` | string/list | safety incident triage | medium; no raw PII |
| `ai.cache.hit` | bool | semantic-cache effectiveness and risk review | low |

Sampling rule: 100% for errors, eval failures, safety flags, PII blocks, provider fallbacks, and high-cost outliers; sampled healthy traces only after PII removal.

> One-liner: **trace the behavior contract, not just the HTTP request.**


Related: [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Reference Patterns]] · [[04 Code Snippets/AI Architecture/AI Week 22a LLM Request Tracer With Cost Accounting]]
