# Secure the AI Workflow Not Just the Prompt

LLM security is a layered control system around the full workflow: user input, data classification, retrieval, model call, tools, output, logs, and governance evidence. A prompt-level rule cannot compensate for private data entering context, unauthorized documents being retrieved, or tool calls executing without permission.

The practical pattern is defense in depth: minimize PII before prompts, enforce RBAC/tenant filters before RAG, constrain tool permissions, filter for leakage, log security decisions, and map controls to OWASP, NIST AI RMF, SOC2/GDPR, and EU AI Act obligations.

> One-liner: **secure every boundary the model crosses** — data in, context retrieved, tools called, output released, evidence retained.


Related: [[02 Literature Notes/LLM Engineering/AI Security and Governance]]
