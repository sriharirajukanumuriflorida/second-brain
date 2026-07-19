# Production Retrieval Is a Recall Precision Diversity Funnel

A mature RAG retriever is a funnel. Start broad and cheap for **recall** (dense + lexical candidates), fuse robustly (often RRF), spend expensive models on **precision** (cross-encoder reranking), then select a **diverse** final context (MMR) so the LLM sees complementary evidence.

Dense search alone is a baseline, not an architecture. Exact tokens, metadata filters, rerankers, and diversity controls are what make retrieval production-grade.

> One-liner: **retrieve broadly, rerank carefully, pack diversely.**


Related: [[02 Literature Notes/LLM Engineering/Advanced Retrieval]] · [[02 Literature Notes/LLM Engineering/Vector Search]]
