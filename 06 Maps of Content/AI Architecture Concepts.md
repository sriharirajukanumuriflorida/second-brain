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

## Week 20 — Cloud Architecture & Deployment
> Taking the W19 architecture from diagram to defensible, deployable Azure system.

### Week 20a — Reference Patterns
- ✅ [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Reference Patterns]]
  - Azure AI Foundry / OpenAI · Bedrock · Vertex · PTU vs Standard · Container Apps vs AKS vs App Service · Dockerfile discipline · K8s primitives · Bicep vs Terraform · workload identity · Key Vault · GitHub Actions · blue/green · canary · prompt+model+index versioning tuple
  - Snippets: [[04 Code Snippets/AI Architecture/AI Week 20a Cloud Deployment Manifest Validator]] · [[04 Code Snippets/AI Architecture/AI Week 20a Canary Release Evaluator]]
  - Permanent: [[03 Permanent Notes/AI Week 20a Cloud AI Platform Decision Guide]] · [[03 Permanent Notes/AI Week 20a Container and Kubernetes Cheat Sheet for AI Services]]

### Week 20b — Applied (deploy the W19 architecture)
- ✅ [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Applied]]
  - Insurance-underwriter scenario deployed on Azure: Container Apps + Azure OpenAI (private endpoint) + pgvector on Postgres Flexible + Blob audit + Key Vault + Entra ID + App Insights · Bicep IaC · CMK & data-boundary controls · monthly cost math at Baseline / Growth / Enterprise scale · independent rollback per prompt/model/index axis · GitHub Actions release pipeline · 2am rollback drill
  - Snippets: [[04 Code Snippets/AI Architecture/AI Week 20b Azure Deployment Topology Cost Estimator]] · [[04 Code Snippets/AI Architecture/AI Week 20b Prompt Model Index Release Orchestrator]]
  - Permanent: [[03 Permanent Notes/AI Week 20b Azure Enterprise AI Deployment Reference]] · [[03 Permanent Notes/AI Week 20b Prompt Model Index Release Discipline]]

---

## Week 22 — LLMOps, Monitoring, Cost & Reliability
> Running the deployed system in production: SLOs, observability, drift, cost, and incident response.

### Week 22a — Reference Patterns
- ✅ [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Reference Patterns]]
  - LLMOps loop vs classical SRE · OTel spans + AI-specific attributes · LangSmith/LangFuse/Arize · AI-native SLOs (groundedness, faithfulness, refusal, cost/req) · TPM/RPM/PTU management · semantic cache · dual-provider fallback · drift detection · eval regression gate
  - Snippets: [[04 Code Snippets/AI Architecture/AI Week 22a LLM Request Tracer With Cost Accounting]] · [[04 Code Snippets/AI Architecture/AI Week 22a SLO and Cost Budget Guard]]
  - Permanent: [[03 Permanent Notes/AI Week 22a LLM Observability Attribute Reference]] · [[03 Permanent Notes/AI Week 22a AI SLO Design Guide]]

### Week 22b — Applied (operate the W20 deployment)
- ✅ [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Applied]]
  - Insurance-underwriter SLO contract (99.5% avail, p95 ≤ 6s, grounded ≥ 92%, cost ≤ $0.08/query) · instrumentation on the Azure topology · PTU-vs-Standard break-even math at 200 users · drift sources (query/corpus/silent model) with detection · 3 real incidents (2am groundedness drop, cost spike, prompt injection) with on-call runbooks · weekly customer report format
  - Snippets: [[04 Code Snippets/AI Architecture/AI Week 22b Underwriter SLO Dashboard Evaluator]] · [[04 Code Snippets/AI Architecture/AI Week 22b AI Incident Response Classifier and Runbook Selector]]
  - Permanent: [[03 Permanent Notes/AI Week 22b Customer SLO Contract for Enterprise AI]] · [[03 Permanent Notes/AI Week 22b Enterprise AI On-Call Runbook Bundle]]

---

## Week 21 — Security, Governance & Responsible AI
> The layer that decides whether AI goes live: threat modeling, PII/DLP, prompt injection defenses, governance, and the enterprise Security Review Board.

### Week 21a — Reference Patterns
- ✅ [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Reference Patterns]]
  - OWASP LLM Top 10 + STRIDE for AI · trust zones · PII/DLP + right-to-erasure · AuthN/AuthZ with retrieval-time ACL enforcement · direct + indirect prompt injection defenses (layered) · Responsible AI (NIST AI RMF, Microsoft RAI, EU AI Act Article 6) · model cards + data cards
  - Snippets: [[04 Code Snippets/AI Architecture/AI Week 21a PII Redaction Pipeline With Policy Classes]] · [[04 Code Snippets/AI Architecture/AI Week 21a Prompt Injection Defense Pipeline]]
  - Permanent: [[03 Permanent Notes/AI Week 21a OWASP LLM Top 10 Engineering Controls Map]] · [[03 Permanent Notes/AI Week 21a Enterprise AI Governance and Responsible AI Framework]]

### Week 21b — Applied (getting the W20 system through SRB)
- ✅ [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Applied]]
  - Full Security Review Board submission for the insurance-underwriter system · end-to-end data-flow controls on the Azure topology · redact-before-embed + right-to-erasure workflow · model risk management (SR 11-7 style) · prompt+tool approval workflows · EU AI Act positioning · red-team + 25-item go-live checklist
  - Snippets: [[04 Code Snippets/AI Architecture/AI Week 21b Enterprise AI Security Review Submission Generator]] · [[04 Code Snippets/AI Architecture/AI Week 21b Enterprise AI Go Live Checklist Evaluator]]
  - Permanent: [[03 Permanent Notes/AI Week 21b Enterprise AI Security Review Submission Template]] · [[03 Permanent Notes/AI Week 21b Enterprise AI Go-Live Checklist]]

---

## Phase 4 Status
Phase 4 is ✅ complete — architecture (W19), deployment (W20), LLMOps (W22), and security/governance (W21). Next: Phase 5 (Weeks 23–24).

## Roadmap position
- Prerequisite: [[06 Maps of Content/Software Engineering Concepts]] (Phase 1 + Depth Pass) — the engineering foundation this architecture layer sits on.
- Parallel: [[06 Maps of Content/LLM Engineering Concepts]] — the LLM/AI content this track puts into a defensible system.
- Downstream: Week 23 (Customer Discovery & Stakeholder Comms), Week 24 (Capstone FDE Portfolio Project).
