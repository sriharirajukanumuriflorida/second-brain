# Recall MRR and Precision Diagnose Different Retrieval Failures

Retrieval metrics answer different debugging questions. **Recall@k** asks whether relevant evidence is found at all. **MRR** asks whether the first relevant result appears early. **Precision@k** asks how noisy the final context is. **NDCG** handles graded relevance and rank quality.

Use them diagnostically: low recall -> candidate generation/chunking; low MRR -> reranking; low precision -> filtering/final-k.

> One-liner: **recall finds missing evidence, MRR fixes ordering, precision controls context noise.**


Related: [[02 Literature Notes/LLM Engineering/Retrieval Evaluation]]
