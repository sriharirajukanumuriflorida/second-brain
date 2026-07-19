# AI Week 21a OWASP LLM Top 10 Engineering Controls Map

Use this as a security-review checklist.

| OWASP tag | Threat | Engineering controls |
|---|---|---|
| LLM01 | Prompt Injection | instruction hierarchy, delimiter sandboxing, retrieved-content sanitation, PromptGuard/LlamaGuard classifiers, canaries, rate limits, HITL for risky actions |
| LLM02 | Insecure Output Handling | Pydantic/JSON Schema validation, HTML sanitization, no unsandboxed code/SQL/tool execution, safe-content filters |
| LLM03 | Training Data Poisoning | signed datasets, data lineage, review gates, outlier detection, eval regression tests, trusted fine-tune sources |
| LLM04 | Model Denial of Service | max context, max output tokens, agent step budgets, quota budgets, circuit breakers, per-user rate limits |
| LLM05 | Supply Chain | vetted weights/tokenizers/embedding models, SBOM, dependency scanning, model provenance, signed artifacts |
| LLM06 | Sensitive Information Disclosure | PII/DLP redaction, secrets outside prompts, redacted traces, provider retention controls, ACL-safe retrieval |
| LLM07 | Insecure Plugin Design | tool registry, exact schemas, least-privilege scopes, validation, dry-run, per-tool policy checks |
| LLM08 | Excessive Agency | narrow tools, delegation tokens, max actions, HITL approval, compensation/rollback paths |
| LLM09 | Overreliance | citations, confidence/refusal UX, human review, evals, warning labels, domain-specific limitations |
| LLM10 | Model Theft | auth, throttling, anomaly detection, watermark/canary probes, prompt hardening, anti-scraping controls |

Cross-map to STRIDE for the SRB: spoofing is identity/tool impersonation; tampering is prompt injection, poisoning, and supply-chain compromise; repudiation is missing audit; information disclosure is PII/system-prompt leakage; DoS is quota/context exhaustion; elevation is tool overreach.

> One-liner: **every LLM threat needs a named control, an owner, and evidence in logs or release gates.**


Related: [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Reference Patterns]] · [[04 Code Snippets/AI Architecture/AI Week 21a PII Redaction Pipeline With Policy Classes]]
