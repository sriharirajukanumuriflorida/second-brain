# Embeddings Turn Meaning into Geometry

## Core Idea
- An embedding is a fixed-length vector that encodes the meaning of text so that semantic similarity becomes geometric proximity: related texts land near each other, unrelated texts land far apart.

## Why It Matters
- Once meaning is a vector, "find similar" becomes "find nearest vectors" — a fast math operation. This is what powers semantic search, RAG, clustering, deduplication, classification, and recommendation.
- Retrieval quality is bounded by how well the embedding preserved the distinctions your queries care about.

## Explanation
- A transformer produces a contextual vector per token; those are pooled (usually mean pooling) into one sentence vector, and the model is trained contrastively so proximity reflects semantics (Sentence-BERT).
- Similarity is measured by cosine (the angle), ignoring magnitude; values run from 1 (identical meaning) to 0 (unrelated) to −1 (opposite).
- Embeddings encode similarity of meaning, NOT factual truth — two confidently wrong sentences can be very similar.

## Examples
- "car" and "automobile" have high cosine similarity despite sharing no characters.
- Semantic search: embed the query, return the corpus chunks whose vectors are nearest.

## Links
- Source literature note: [[02 Literature Notes/LLM Engineering/Embeddings]]
- Related notes: [[03 Permanent Notes/Normalize Embeddings to Use Dot Product as Cosine]]
- Related project:
