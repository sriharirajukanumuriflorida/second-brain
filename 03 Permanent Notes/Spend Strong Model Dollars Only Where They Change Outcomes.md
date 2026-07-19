# Spend Strong Model Dollars Only Where They Change Outcomes

The core cost principle in LLM systems is selective escalation. Easy tasks, repeated questions, and low-risk transformations should not consume frontier-model budget. Use exact/semantic caches to avoid duplicate work, small models for routine traffic, and confidence-gated cascades for hard cases. Strong models should be purchased when they improve correctness, safety, or business value — not by default.

This requires a ledger: cost per request, route, prompt version, tenant, and feature.

> One-liner: **buy intelligence incrementally** — cache first, route cheap, escalate only on evidence.


Related: [[02 Literature Notes/LLM Engineering/Cost Architecture]] · [[02 Literature Notes/LLM Engineering/Reasoning Models]]
