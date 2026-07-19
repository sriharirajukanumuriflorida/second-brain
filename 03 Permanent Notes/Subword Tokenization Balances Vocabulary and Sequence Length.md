# Subword Tokenization Balances Vocabulary and Sequence Length

## Core Idea
- Subword tokenization (BPE, WordPiece, Unigram) is the compromise between word-level and character-level: frequent words become single tokens, rare words split into meaningful pieces, and byte fallback guarantees any string is representable.

## Why It Matters
- It gives a fixed, modest vocabulary (~30k–200k) that covers all possible input, avoiding both the out-of-vocabulary problem of word tokenizers and the excessive sequence length of character tokenizers.
- Byte-level BPE has zero out-of-vocabulary tokens — emojis, typos, code, and unseen languages are all encodable.

## Explanation
- BPE is learned by repeatedly merging the most frequent adjacent symbol pair, producing an ordered list of merge rules applied greedily at encode time.
- WordPiece merges by likelihood gain (BERT); Unigram/SentencePiece starts large and prunes probabilistically (T5, multilingual).
- Because characters are hidden inside merged tokens, models cannot reliably do character-level tasks (reversing strings, counting letters) or long arithmetic.

## Examples
- "tokenization" → `token` + `ization`; a rare surname → several byte-level pieces.
- "internationalization" tokenizes into a handful of subword units rather than one giant vocabulary entry.

## Links
- Source literature note: [[02 Literature Notes/LLM Engineering/Tokenization]]
- Related notes: [[03 Permanent Notes/Tokens Are the Unit of Cost and Context]]
- Related project:
