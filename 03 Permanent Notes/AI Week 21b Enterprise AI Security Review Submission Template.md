# AI Week 21b Enterprise AI Security Review Submission Template

Reusable SRB packet structure for enterprise AI:

1. **System context**: business owner, technical owner, intended users, intended use, prohibited uses, deployed topology, data residency, human-oversight boundary.
2. **Data classification**: public/internal/confidential/PII/sensitive fields; examples; control for each field; retention and erasure rules.
3. **Threat model**: STRIDE plus OWASP LLM Top 10 mapped to this exact architecture, including prompt injection, insecure output handling, poisoning, DoS, supply chain, disclosure, tool abuse, excessive agency, overreliance, and model theft.
4. **Trust boundaries**: browser, edge, private app origin, managed identity, retrieval, prompt, model output, audit, telemetry, and tool calls.
5. **Control matrix**: threat → control → owner → evidence link → status. No owner or evidence means no go-live claim.
6. **Residual risks**: exposure, compensating controls, approver, expiry, and review cadence.
7. **Monitoring and incident commitments**: SLOs, eval canaries, safety alerts, audit schema, rollback lanes, DPO/CISO escalation.

> One-liner: **the SRB submission is the production security contract for AI.**


Related: [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Applied]] · [[04 Code Snippets/AI Architecture/AI Week 21b Enterprise AI Security Review Submission Generator]]
