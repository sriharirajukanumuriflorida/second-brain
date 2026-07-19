# AI Week 19a ADR Template for AI Systems

Use this ADR shape for AI architecture decisions:

- **Title**: one decision in active voice, e.g. 'Choose pgvector for MVP vector search'.
- **Status**: proposed, accepted, superseded, or deprecated.
- **Context**: customer constraints, scale, data residency, security, cost, team ownership, eval results, and deadlines.
- **Decision**: the option chosen and the boundary it applies to.
- **Consequences**: benefits, risks, operational obligations, metrics to watch, and revisit triggers.
- **Alternatives**: serious options rejected and why.

Good AI ADRs name real choices: Azure OpenAI vs Bedrock vs Vertex; RAG vs fine-tune; pgvector vs Pinecone vs Qdrant; LangChain vs LlamaIndex vs bespoke ports; REST vs streaming SSE; modular monolith vs microservices. They also document model-safety and operations consequences: PII boundary, evaluation gate, fallback behavior, audit trail, cost budget, and owner.

> One-liner: **if a future incident reviewer cannot tell why the AI system was built this way, the architecture decision was not recorded.**


Related: [[02 Literature Notes/AI Architecture/AI Solution Architecture — Reference Patterns]] · [[04 Code Snippets/AI Architecture/AI Week 19a Machine Readable ADR Registry]]
