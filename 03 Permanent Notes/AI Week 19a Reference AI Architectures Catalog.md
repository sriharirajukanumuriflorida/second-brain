# AI Week 19a Reference AI Architectures Catalog

Reference architectures an FDE should know cold:

1. **Simple LLM call** — chat-completion service with auth, prompt version, model route, validation, trace, and cost meter. Use for bounded generation; do not use for changing enterprise knowledge without retrieval.
2. **RAG** — ingest, chunk, embed, index, retrieve, rerank, generate, cite. Use when answers need grounding, ACLs, and fresh documents; do not use when there is no trusted corpus or latency budget for retrieval.
3. **Agent** — LLM plus planner, tool registry, memory, guardrails, and trace. Use when the system must choose actions; do not use for deterministic workflows that simple code can own.
4. **Multi-agent / orchestrated workflow** — specialized agents or deterministic steps coordinated around a task. Use for separable review/research/execution roles; do not use when debugging and ownership would become opaque.
5. **Fine-tuned serving** — training loop, eval gate, registry, deployment ring, monitoring, and rollback. Use for stable labeled behavior; do not use as a substitute for missing knowledge or citations.
6. **Hybrid** — RAG + fine-tune + agent. Use only when evals prove each component improves quality, safety, or cost.
7. **Evaluation-in-the-loop** — offline evals, online evals, human review, feedback capture, and dataset curation. Use for continuous improvement and release gates.
8. **Human-in-the-loop approval** — queue, reviewer UI, audit log, SLA, escalation, and policy. Use for high-risk actions and regulated workflows; do not replace it with informal chat approval.

> One-liner: **pick the smallest reference architecture that satisfies grounding, action, risk, and improvement requirements.**


Related: [[02 Literature Notes/AI Architecture/AI Solution Architecture — Reference Patterns]] · [[04 Code Snippets/AI Architecture/AI Week 19a Hexagonal RAG Pipeline Demo]]
