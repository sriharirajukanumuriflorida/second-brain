# Contextual Retrieval Restores Lost Chunk Context

## Core Idea
- Chunking strips a passage of the surrounding document context that made it meaningful. Contextual retrieval repairs this by using an LLM to prepend a short, document-aware context sentence to each chunk *before embedding it*.

## Why It Matters
- It sharply improves retrieval on chunks that are ambiguous in isolation (pronouns, references, section-dependent meaning) — common in financial, legal, and technical documents.
- It is often higher-ROI than upgrading the embedding model or adding a reranker.

## Explanation
- For each chunk, an LLM sees the whole document plus the chunk and writes 1–2 sentences situating it ("This is from the 2023 10-K Risk Factors section, on supply-chain exposure...").
- That context is prepended to the chunk, and the combined text is embedded and stored.
- The cost is one LLM call per chunk at ingestion time — paid once, amortized across all future queries. Prompt caching on the repeated document prefix keeps it affordable.
- Anthropic's published pattern pairs it with BM25 (hybrid search) for best recall.

## Examples
- A bare chunk "This cut costs by 40%." becomes "[From the 2023 annual report, discussing the new supplier contract:] This cut costs by 40%." — now retrievable for cost/supply-chain queries.

## Links
- Source literature note: [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
- Related notes: [[03 Permanent Notes/Chunking Is the Unit of Retrieval and Grounding]]
- Related project:
