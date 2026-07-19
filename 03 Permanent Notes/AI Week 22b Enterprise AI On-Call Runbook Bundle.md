# AI Week 22b Enterprise AI On-Call Runbook Bundle

Compact runbook bundle for the insurance-underwriter assistant:

- **Groundedness drop**: detect by hourly canary or golden-set regression; verify eval health and release tuple; rollback model or prompt lane; notify customer with impact and mitigation; add failed cases to golden set.
- **Cost spike**: detect by cost/query, prompt tokens, retrieved count, or tenant spend; slice by tenant/feature/prompt/model; throttle or rollback; explain facts to finance/customer owner; add cost regression gate.
- **Latency regression**: detect by `/query` p95; split provider latency from retrieval and Container Apps saturation; rollback model or index, scale, or move hot path to PTU; add latency replay test.
- **Safety flag spike**: tighten refusal/guardrail policy, sample audit records, involve compliance if regulated content is exposed, and refresh safety eval labels.
- **Provider outage**: respect Retry-After, trip circuit breaker, reduce concurrency, enable cached-answer or human-review mode, and open provider case with trace ids.
- **Suspected injection**: preserve Blob audit, block pattern, escalate to security, rotate any exposed secret, add red-team case, and update delimiter/instruction-precedence controls.

> One-liner: **the runbook is not done until it says detect, mitigate, communicate, and correct.**


Related: [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Applied]] · [[04 Code Snippets/AI Architecture/AI Week 22b AI Incident Response Classifier and Runbook Selector]]
