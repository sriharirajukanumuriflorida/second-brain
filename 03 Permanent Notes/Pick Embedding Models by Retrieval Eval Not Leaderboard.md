# Pick Embedding Models by Retrieval Eval Not Leaderboard

## Core Idea
- There is no universally best embedding model — only the best model for a workload. Use MTEB to build a shortlist, then pick the winner with a retrieval evaluation (recall@k / MRR) on your own golden set from the real corpus.

## Why It Matters
- Benchmark rankings are measured on datasets that differ from your domain and queries; a leaderboard champion can under-retrieve on your data.
- Model choice is semi-permanent: switching means re-embedding the entire corpus, so getting it right with evidence avoids expensive rework.

## Explanation
- Selection is multi-objective: retrieval quality (the MTEB Retrieval sub-score, not the average), dimensionality (storage/latency), max input length, language/domain fit, hosting (API vs self-host), cost, and privacy.
- Procedure: constraints filter → MTEB shortlist → build a 30–100 query golden set → score candidates on recall@k, MRR, latency, and $/1M → pick on the quality–cost Pareto frontier.
- Dimensionality and quantization (int8/binary, Matryoshka truncation) are chosen jointly with the model as one quality/cost decision.

## Examples
- A model topping the MTEB average but weak on Retrieval is a poor RAG choice.
- Presenting a client an index-size + cost table per candidate reframes the choice as a business decision.

## Links
- Source literature note: [[02 Literature Notes/LLM Engineering/Embedding Model Selection]]
- Related notes: [[03 Permanent Notes/Embeddings Turn Meaning into Geometry]]
- Related project:
