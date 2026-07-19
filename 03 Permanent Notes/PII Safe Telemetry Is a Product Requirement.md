# PII Safe Telemetry Is a Product Requirement

LLM telemetry often contains the most sensitive data in the system: user messages, retrieved documents, completions, tool arguments, and exception context. Observability must therefore be designed with redaction, sampling, retention, and access control from the start. Store structured metadata always; store raw payloads only when sampled, redacted, and justified.

> One-liner: **debuggability without a shadow data leak** is the standard for LLM monitoring.


Related: [[02 Literature Notes/LLM Engineering/Observability and Monitoring]] · [[02 Literature Notes/LLM Engineering/LLM Security]]
