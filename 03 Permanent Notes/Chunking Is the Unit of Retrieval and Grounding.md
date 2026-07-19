# Chunking Is the Unit of Retrieval and Grounding

## Core Idea
- In a RAG system, the chunk is simultaneously the unit that gets *retrieved* and the unit the LLM *grounds* its answer on. Its size and boundaries therefore set the ceiling on how accurate the whole system can be.

## Why It Matters
- No downstream component — bigger model, reranker, better prompt — can recover information that chunking fragmented or stripped of context.
- When a RAG system is "inaccurate," chunking is the highest-leverage place to look first, before model or prompt changes.

## Explanation
- Chunks must resolve a tension: small enough to embed cleanly and match a query precisely, large enough to be self-contained and meaningful.
- Too small → the answer is scattered across more chunks than top-k returns (incomplete answers).
- Too large → embedding dilution; one vector represents many ideas weakly and matches nothing sharply.
- Measuring size in tokens (not characters) keeps chunks within embedding limits and makes cost predictable.

## Examples
- A one-sentence chunk "This reduced latency by 40%." is un-retrievable for a query about the specific system, because "this" lost its referent.
- Diagnosing a failing RAG: pull the retrieved chunks for failed queries; fragmentation or lost context is usually visible immediately.

## Links
- Source literature note: [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
- Related notes: [[03 Permanent Notes/Contextual Retrieval Restores Lost Chunk Context]]
- Related project:
