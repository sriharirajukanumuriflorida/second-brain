# Choose a Vector Database by Retrieval Operations Not Brand

Vector database choice should follow retrieval requirements: scale, latency, metadata filters, hybrid search, tenancy, updates/deletes, managed operations, observability, and migration risk. ANN recall matters, but RAG systems fail just as often on filters, stale vectors, poor deletes, or missing hybrid search.

Start from product constraints and run a proof-of-concept on real queries.

> One-liner: **choose for the retrieval operations your product actually needs.**


Related: [[02 Literature Notes/LLM Engineering/Vector Database Landscape]] · [[02 Literature Notes/LLM Engineering/ANN Index Internals]]
