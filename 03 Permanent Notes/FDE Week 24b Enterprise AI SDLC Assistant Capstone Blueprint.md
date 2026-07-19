# FDE Week 24b Enterprise AI SDLC Assistant Capstone Blueprint

Reusable blueprint for this class of FDE capstone:

1. **Business claim**: baseline, target, unit cost, target user, and quality threshold in one BLUF sentence.
2. **DiscoveryBrief**: JTBD, stakeholders, SMART criteria, constraints, risks, and explicit Won't list.
3. **Architecture**: C4 Container view, FastAPI/Pydantic API, RAG pipeline, provider port, pgvector, guardrails, human review, eval, observability, prompt registry, config store.
4. **Prompt contracts**: id, purpose, model route, input/output schema, safety rules, changelog, owner, eval artifact, rollback pointer.
5. **Evaluation**: 100-500 golden items, schema checks, groundedness, citation coverage, semantic PBI precision/recall, test-quality rubric, regression verdicts.
6. **Deployment and ops**: `make setup/test/eval/run/deploy`, docker compose, cloud IaC, CI/CD scans, smoke eval, traffic gates, OTel cost/latency logs.
7. **Security and go-live**: OAuth/OIDC, RBAC, PII redaction, injection defenses, audit log, 25-item checklist, conditional go with owners.
8. **Portfolio narrative**: README opening, three-act demo, interview pitch, hard problems, tradeoffs, failure modes, roadmap.

> One-liner: **a capstone is portfolio-ready when a stranger can reproduce the value claim and inspect the evidence.**


Related: [[02 Literature Notes/FDE Delivery/Capstone FDE Portfolio Project — Applied]] · [[04 Code Snippets/FDE Delivery/FDE Week 24b Enterprise AI SDLC Assistant Offline Pipeline]]
