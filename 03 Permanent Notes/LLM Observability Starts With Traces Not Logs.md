# LLM Observability Starts With Traces Not Logs

Production LLM systems are causal graphs: retrieval feeds prompt assembly, prompts feed model calls, models call tools, tools change later prompts, and validators decide whether output ships. A single log line cannot explain that chain. The basic unit of observability is a **trace** with spans for retrieval, prompt rendering, model calls, tools, parsers, and guardrails.

Each span should carry structured metadata: prompt version, model/provider, token counts, latency, cost, status, retry count, retrieved doc ids, and redacted payload samples.

> One-liner: **trace the chain of evidence** — otherwise you are debugging a probabilistic system from shadows.


Related: [[02 Literature Notes/LLM Engineering/Observability and Monitoring]] · [[02 Literature Notes/LLM Engineering/RAG Evaluation]]
