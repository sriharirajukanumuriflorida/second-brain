# Tokens Are the Unit of Cost and Context

## Core Idea
- LLMs process integer token IDs, not text. The token is therefore the atomic unit of context windows, API pricing, and latency — reasoning about LLM cost and limits means reasoning about tokens.

## Why It Matters
- Context-overflow bugs and cost estimates are token-accounting problems; counting characters or words gives wrong answers.
- The same idea costs different amounts in different languages because tokenizers fragment non-English and code into more tokens.

## Explanation
- Cost is linear in token count: input tokens × input price + output tokens × output price, bounded by the context window.
- A tokenizer's compression ratio (characters / tokens) determines how cheap a given text is; higher is better.
- Chat requests carry hidden per-message template overhead, so a naive sum of message lengths underestimates the true token count.
- Rule of thumb ~4 chars ≈ 1 token for English, but this is not a law — verify on your actual data.

## Examples
- Estimating monthly spend = (avg input tokens + avg output tokens per request) × price × request volume.
- A Japanese or code-heavy prompt exhausts the context window faster than an English one of equal "length."

## Links
- Source literature note: [[02 Literature Notes/LLM Engineering/Tokenization]]
- Related notes: [[03 Permanent Notes/Subword Tokenization Balances Vocabulary and Sequence Length]]
- Related project:
