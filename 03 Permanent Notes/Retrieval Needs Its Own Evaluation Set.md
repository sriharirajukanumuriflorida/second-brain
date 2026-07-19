# Retrieval Needs Its Own Evaluation Set

RAG final-answer evals hide whether failures came from search or generation. Retrieval needs a labeled set of realistic queries with relevant chunk/document IDs and metrics such as hit rate, recall@k, precision@k, MRR, and NDCG.

If evidence is absent from the retrieved context, generation cannot be reliably grounded. Evaluate retrieval first, then evaluate synthesis.

> One-liner: **no retrieved evidence means no grounded answer.**


Related: [[02 Literature Notes/LLM Engineering/Retrieval Evaluation]] · [[02 Literature Notes/LLM Engineering/RAG Pipeline Fundamentals]]
