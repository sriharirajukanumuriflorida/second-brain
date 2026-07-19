# Reciprocal Rank Fusion Avoids Score Calibration Problems

Dense and BM25 scores live on different scales, so averaging them is brittle. Reciprocal Rank Fusion combines lists by rank position: documents get credit for appearing near the top of any retriever. This makes hybrid retrieval simple, robust, and explainable.

RRF is not magic; it still depends on candidate recall. But it is often the best first fusion method before cross-encoder reranking.

> One-liner: **when scores are incomparable, fuse ranks instead.**


Related: [[02 Literature Notes/LLM Engineering/Advanced Retrieval]]
