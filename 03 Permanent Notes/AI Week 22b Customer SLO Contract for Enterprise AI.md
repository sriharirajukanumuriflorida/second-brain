# AI Week 22b Customer SLO Contract for Enterprise AI

Reusable customer SLO contract for operated enterprise AI:

1. **Service**: availability, p95/p99 latency, provider errors, and tool-call success.
2. **AI quality**: groundedness on a customer golden set, hallucination rate, refusal rate, citation coverage, and safety flags.
3. **Cost**: cost per answered question, daily/user budget, tenant/month budget, prompt-version token deltas, cache hit rate, and eval traffic overhead.
4. **Error budget**: define how uptime, quality, safety, and cost failures burn budget; freeze risky feature releases when budget is exhausted.
5. **Monthly report**: SLO table, error-budget remaining, top incidents, release tuple changes, cost by tenant/feature/prompt, drift findings, and corrective actions added to evals.

Sample underwriting targets: availability ≥ 99.5%, p95 answer latency ≤ 6s, groundedness ≥ 92%, refusal rate ≤ 8%, hallucination rate ≤ 1%, cost/answered question ≤ $0.08, tool-call success ≥ 98%.

> One-liner: **an enterprise AI SLO is a negotiated trust contract across uptime, answer quality, safety, and unit cost.**


Related: [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Applied]] · [[04 Code Snippets/AI Architecture/AI Week 22b Underwriter SLO Dashboard Evaluator]]
