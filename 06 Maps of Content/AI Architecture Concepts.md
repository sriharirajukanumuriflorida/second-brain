# AI Architecture Concepts

> Phase 4 of the 24-Week FDE roadmap — where AI engineering becomes an *architected system* an FDE can defend, deploy, secure, and hand off to a customer.
> Goal: production-grade architecture judgment for enterprise AI. Reference patterns, applied worked scenarios, cloud deployment, LLMOps, security, and governance.
> Legend: ✅ built · 🟡 partial · ⬜ planned

## How to use this track
1. Skim the **Slide deck** (`07 Resources Library/AI Architecture/Slides/`) for the overview.
2. Read the topic's **Literature Note** (`02 Literature Notes/AI Architecture/`) for the deep material.
3. Work the **Notebook** (`07 Resources Library/AI Architecture/Notebooks/`) hands-on — it runs offline.
4. Keep the linked **Code Snippet(s)** (`04 Code Snippets/AI Architecture/`) as reusable reference.
5. Distill durable insights into **Permanent Notes** (`03`).
6. Do the note's **Self-Check** before marking a topic done.

## Resource Library
- Slides: `07 Resources Library/AI Architecture/Slides/`
- Notebooks: `07 Resources Library/AI Architecture/Notebooks/`

---

## Week 19 — AI Solution Architecture
> The FDE's daily deliverable: a defensible, one-page architecture for an enterprise AI system.

### Week 19a — Reference Patterns
- ✅ [[02 Literature Notes/AI Architecture/AI Solution Architecture — Reference Patterns]]
  - C4 model · ADRs · hexagonal ports for LLM providers · Simple LLM · RAG · Agent · Multi-agent · Fine-tuned serving · Hybrid · Evaluation-in-the-loop · HITL approval · cross-cutting concerns (prompt/tool/model registry, guardrails, PII/DLP, tracing, cost accounting, semantic cache, fallback modes)
  - Snippets: [[04 Code Snippets/AI Architecture/AI Week 19a Machine Readable ADR Registry]] · [[04 Code Snippets/AI Architecture/AI Week 19a Hexagonal RAG Pipeline Demo]]
  - Permanent: [[03 Permanent Notes/AI Week 19a Reference AI Architectures Catalog]] · [[03 Permanent Notes/AI Week 19a ADR Template for AI Systems]]

### Week 19b — Applied (worked customer scenario)
- ✅ [[02 Literature Notes/AI Architecture/AI Solution Architecture — Applied]]
  - Vague ask → clarified problem · current-state vs future-state · one-page C4 Container diagram · ADR bundle · capacity + cost math · failure-mode analysis · FDE hand-off artifacts
  - Snippets: [[04 Code Snippets/AI Architecture/AI Week 19b One Page Architecture Generator]] · [[04 Code Snippets/AI Architecture/AI Week 19b Capacity and Cost Estimator]]
  - Permanent: [[03 Permanent Notes/AI Week 19b Enterprise AI One-Pager Architecture Template]] · [[03 Permanent Notes/AI Week 19b FDE Discovery to Architecture Playbook]]

---

## Planned (Phase 4 continued)
- ⬜ Week 20 — Cloud Architecture & Deployment (Azure AI / OpenAI, containers, IaC, secrets, environments, CI/CD to cloud)
- ⬜ Week 21 — Security, Governance & Responsible AI (PII/DLP, RBAC/ABAC, prompt injection defenses, audit, compliance, responsible AI principles)
- ⬜ Week 22 — LLMOps, Monitoring, Cost & Reliability (observability, SLOs, drift, evaluation regression, incident handling)

## Roadmap position
- Prerequisite: [[06 Maps of Content/Software Engineering Concepts]] (Phase 1 + Depth Pass) — the engineering foundation this architecture layer sits on.
- Parallel: [[06 Maps of Content/LLM Engineering Concepts]] — the LLM/AI content this track puts into a defensible system.
- Downstream: Week 23 (Customer Discovery & Stakeholder Comms), Week 24 (Capstone FDE Portfolio Project).
