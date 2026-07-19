# AI Week 21b Enterprise AI Go-Live Checklist

Copy-paste checklist for enterprise AI launch:

| Category | Required evidence |
|---|---|
| Data | classification approved; redact-before-embed; prompt PII scan; GDPR Article 17 workflow tested |
| Identity | Entra groups mapped; managed identity least privilege; no secrets in image/CI |
| Network | Front Door WAF/TLS; Private Endpoints/DNS; no public egress; Postgres RLS by ABAC |
| Audit/retention | Blob WORM + CMK; redacted OTel; prompt/model/index/tool versions in audit; retention decision recorded |
| Versioning | prompt/model/index versioning and rollback drill |
| Eval/ops | golden eval green; drift/safety/cost alerts; incident runbooks approved |
| Governance | DPIA/AI risk assessment; model card; data card; prompt registry approval; tool catalog + HITL thresholds |
| Red team | direct/indirect injection, tool abuse, RLS bypass, PII exfiltration, traditional pen-test clean |
| DR/customer | backup restore, on-call staffed, customer SLO contract signed |

Traffic moves to 100% only when every blocking item is green. Amber nonblocking items require owner, due date, risk acceptance, and monitoring.

> One-liner: **go-live is a checklist-backed risk decision, not an optimistic deployment.**


Related: [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Applied]] · [[04 Code Snippets/AI Architecture/AI Week 21b Enterprise AI Go Live Checklist Evaluator]]
