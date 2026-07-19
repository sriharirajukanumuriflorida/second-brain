# The Model Proposes Tool Calls Policy Disposes

LLM agents should not directly execute tool calls just because the model emitted them. Treat a tool call as a proposal that deterministic policy must authorize using user role, tool allowlist, argument validation, business rules, confirmation requirements, and audit logging. This prevents prompt injection from escalating into real-world side effects.

> One-liner: **tool use is a permissioned API boundary, not a model privilege**.


Related: [[02 Literature Notes/LLM Engineering/Guardrails and Prompt Injection]] · [[02 Literature Notes/LLM Engineering/Tool Use and Function Calling]]
