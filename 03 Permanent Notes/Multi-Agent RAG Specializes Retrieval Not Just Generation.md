# Multi-Agent RAG Specializes Retrieval Not Just Generation

**Multi-agent RAG splits retrieval itself across source-specialized agents, with a separate synthesis agent combining their findings — it earns its cost only when sources are genuinely heterogeneous enough that one retrieval agent couldn't serve them all well.** The synthesis agent must surface conflicting evidence between retrieval agents explicitly, never silently prefer one.

> One-liner: more sources alone doesn't justify multi-agent RAG — genuine heterogeneity in schema, query style, or evidence-grading rules per source does.

Related: [[02 Literature Notes/LLM Engineering/Agentic RAG]] · [[02 Literature Notes/LLM Engineering/Multi-Agent Orchestration]] · [[02 Literature Notes/LLM Engineering/Agentic Workflow Patterns]]
