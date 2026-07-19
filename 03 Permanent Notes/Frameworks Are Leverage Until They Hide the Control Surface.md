# Frameworks Are Leverage Until They Hide the Control Surface

LLM frameworks accelerate development by packaging integrations, data connectors, orchestration, state, and optimization. But production systems still need visibility into prompts, retrieved context, tool arguments, retries, costs, traces, and evaluation results. When the framework hides these, debugging becomes harder than building the missing piece directly.

Use frameworks deliberately: raw SDK for simple control, LangChain for broad integrations, LlamaIndex/Haystack for RAG data pipelines, LangGraph for stateful agents, and DSPy for optimized prompt programs. Keep adapter boundaries so you can escape the abstraction.

> One-liner: **buy velocity with frameworks, keep control with boundaries**.


Related: [[02 Literature Notes/LLM Engineering/Framework Ecosystem Literacy]] · [[02 Literature Notes/LLM Engineering/Agent Framework Literacy]]
