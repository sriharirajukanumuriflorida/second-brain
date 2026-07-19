# AI Week 21a Enterprise AI Governance and Responsible AI Framework

Responsible AI principles become production controls:

| Principle | Engineering control |
|---|---|
| Fairness | stratified evals by segment, bias/error slices, approval before high-impact use, monitored drift |
| Reliability & Safety | golden datasets, refusal paths, eval gates, rollback, adversarial tests, HITL for risky actions |
| Privacy & Security | PII/DLP, least privilege, ACL-safe retrieval, redacted traces, provider retention controls, threat modeling |
| Inclusiveness | accessibility tests, multilingual coverage, UX fallbacks, SME review for impacted groups |
| Transparency | citations, model cards, data cards, user disclosures, limitations in product copy |
| Accountability | named owners, prompt/model/index registry approvals, immutable audit log, incident runbooks |

Minimum artifacts for enterprise review:
1. **Model card**: intended use, model/provider/version, limitations, eval results, known risks, monitoring plan, owner.
2. **Data card**: sources, consent/purpose, PII classes, retention, deletion workflow, quality issues, allowed uses.
3. **Prompt registry**: version, diff, approver, eval result, rollback target, tenant rollout ring.
4. **Tool registry**: schema, owner, required scopes, side effects, HITL threshold, audit attributes.
5. **High-risk workflow approval**: EU AI Act Article 6 assessment, SR 11-7-style validation, legal/security sign-off, post-launch monitoring.

> One-liner: **RAI is credible when every principle has an operational control and every high-risk decision leaves evidence.**


Related: [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Reference Patterns]] · [[04 Code Snippets/AI Architecture/AI Week 21a Prompt Injection Defense Pipeline]]
