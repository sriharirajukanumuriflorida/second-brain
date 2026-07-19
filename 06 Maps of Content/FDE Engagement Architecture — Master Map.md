# FDE Engagement Architecture — Master Map

> The cross-cutting synthesis map for the full 24-week FDE roadmap.
> Every other MOC is organized *by phase*. This one is organized *by how a real Forward Deployed Engineer engagement actually flows* — so you can trace a single customer problem from first conversation to shipped, secured, operated, and defended AI system.
> Use this as your **review + interview-prep** entry point.

## The four tracks this map ties together
- [[06 Maps of Content/Software Engineering Concepts]] — the engineering foundation (Phase 1 + Depth Pass)
- [[06 Maps of Content/LLM Engineering Concepts]] — the LLM/AI building blocks
- [[06 Maps of Content/AI Architecture Concepts]] — architecture, deploy, ops, security (Phase 4)
- [[06 Maps of Content/FDE Delivery Concepts]] — the human/delivery craft + capstone (Phase 5)

---

## The engagement flow (how the weeks actually connect)

An FDE engagement does **not** run in week-number order. It runs in *value-delivery* order. Here is the real sequence, with the week that teaches each move:

1. **Listen & scope** → *W23 Discovery* — turn a vague ask into a defensible problem statement, scope an MVP (3 options, never 5), get budget approved.
   - [[02 Literature Notes/FDE Delivery/Customer Discovery & Stakeholder Communication — Reference Patterns]]
   - [[02 Literature Notes/FDE Delivery/Customer Discovery & Stakeholder Communication — Applied]]
2. **Architect** → *W19 AI Solution Architecture* — produce the one-page, defensible architecture (C4 + ADRs) for the scoped problem.
   - [[02 Literature Notes/AI Architecture/AI Solution Architecture — Reference Patterns]]
   - [[02 Literature Notes/AI Architecture/AI Solution Architecture — Applied]]
3. **Deploy** → *W20 Cloud Architecture & Deployment* — take the diagram to a running Azure system with IaC, identity, and prompt+model+index release discipline.
   - [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Reference Patterns]]
   - [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Applied]]
4. **Secure & get approval to go live** → *W21 Security, Governance & Responsible AI* — pass the Security Review Board with the go-live checklist.
   - [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Reference Patterns]]
   - [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Applied]]
5. **Operate & prove value** → *W22 LLMOps, Monitoring, Cost & Reliability* — run it against an SLO contract, handle incidents, report to the customer.
   - [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Reference Patterns]]
   - [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Applied]]
6. **Prove you can repeat it** → *W24 Capstone* — the portfolio artifact that shows the whole arc on a fresh problem.
   - [[02 Literature Notes/FDE Delivery/Capstone FDE Portfolio Project — Reference Patterns]]
   - [[02 Literature Notes/FDE Delivery/Capstone FDE Portfolio Project — Applied]]

Underneath all six steps sits the **engineering foundation** — the discipline that keeps the system correct, scalable, and maintainable:
- [[02 Literature Notes/Software Engineering/System Design Fundamentals]]
- [[02 Literature Notes/Software Engineering/Applied Data Structures for Backend and AI]]
- (+ the Depth Pass: Production Delivery Engineering, Distributed Systems Reality, Production API Patterns — see [[06 Maps of Content/Software Engineering Concepts]])

---

## The two worked scenarios (follow one problem end-to-end)

### Scenario A — Insurance Underwriter Assistant (W19b → W23b, one continuous story)
The same customer runs through five packages. Read them in engagement order to see one problem evolve:
1. Discovery & scoping → [[02 Literature Notes/FDE Delivery/Customer Discovery & Stakeholder Communication — Applied]] (4h→90min time-to-quote, "no third-party data leakage", $780k/6mo approved)
2. Architecture → [[02 Literature Notes/AI Architecture/AI Solution Architecture — Applied]]
3. Azure deployment → [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Applied]]
4. Security Review Board → [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Applied]]
5. Operate to the SLO contract → [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Applied]] (99.5% avail, p95 ≤ 6s, grounded ≥ 92%, cost ≤ $0.08/query)

### Scenario B — Enterprise AI SDLC Assistant (W24 capstone, fresh problem)
Proves the pattern repeats on a brand-new problem:
- [[02 Literature Notes/FDE Delivery/Capstone FDE Portfolio Project — Applied]]

---

## Cross-cutting concepts (show up in more than one week)
- **prompt + model + index versioning tuple** — introduced W20, enforced in W21 (approval) and W22 (rollback/drift).
- **Evaluation-in-the-loop / eval regression gate** — architecture (W19), CI (W20), ops gate (W22), capstone proof artifact (W24).
- **Groundedness / faithfulness** — an SLO in W22, a security control in W21, a value claim in W23/W24.
- **Cost math (PTU vs Standard, per-query cost)** — deployment (W20), SLO budget (W22), the number that wins/loses the deal (W23).
- **Data boundary / PII-DLP / right-to-erasure** — the "no third-party leakage" constraint from W23 that shapes W20 topology and W21 controls.

---

## Interview / review path (fast recall drill)
Given a blank whiteboard and "design an enterprise AI system," you should be able to walk:
1. Clarify the *real* job-to-be-done and the one metric that matters (W23).
2. Draw the C4 container diagram + name 3 ADRs you'd write (W19).
3. Place it on a cloud with identity, secrets, and a release strategy (W20).
4. Name the top 3 OWASP-LLM risks and your controls + the go-live gate (W21).
5. State the SLO contract and how you'd detect drift + your incident runbook (W22).
6. Summarize the business value in one BLUF sentence (W23) and show the eval regression that proves quality (W24).

---

## Roadmap position
This is the top-level synthesis node. From here, drill into any phase MOC above, or jump straight to a scenario. Home: [[06 Maps of Content/AIML Courses]].
