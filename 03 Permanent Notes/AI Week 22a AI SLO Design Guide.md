# AI Week 22a AI SLO Design Guide

Design AI SLOs in layers:

1. **Service SLOs**: availability 99.5-99.9%, p95 latency by route, p99 latency for tail-risk workflows, 5xx rate, provider 429/5xx rate, queue age, and saturation.
2. **AI quality SLOs**: groundedness ≥ 0.88, faithfulness ≥ 0.90, hallucination rate < 2%, refusal correctness ≥ 0.95, unsafe completion rate < 0.1%, tool-call success ≥ 0.97, citation coverage ≥ 0.95 where citations are required.
3. **Cost SLOs**: cost/request ≤ product threshold, cost/tenant/month within cap, token growth tracked by prompt version and feature, PTU utilization above the committed target.
4. **Error budget sizing**: assign budget to both service failure and quality failure. A three-point groundedness drop on a core workflow can burn more budget than a brief p95 latency miss.
5. **Golden set freshness**: include top production questions, high-risk workflows, adversarial prompts, incident examples, and changed-corpus samples. Refresh with SME review so labels do not rot.
6. **Alerting**: alert on rolling windows, statistically meaningful trend shifts, and canary-vs-baseline deltas; LLM quality is noisy at the single-request level.

> One-liner: **an AI SLO is an agreement about answer quality, safety, latency, and cost — measured against data you keep alive.**


Related: [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Reference Patterns]] · [[04 Code Snippets/AI Architecture/AI Week 22a SLO and Cost Budget Guard]]
