# Inspecting a Tokenizer with tiktoken

## Purpose
- See exactly how text becomes token IDs and back: encode/decode round-trips, per-piece breakdown, special tokens, and compression ratio across languages/content. The fastest way to build tokenizer intuition.

## Language
- Python

## Snippet
```python
# pip install tiktoken
import tiktoken

enc = tiktoken.get_encoding("o200k_base")   # gpt-4o / gpt-4.1 family
# For a specific model:  enc = tiktoken.encoding_for_model("gpt-4o-mini")

def show(text):
    ids = enc.encode(text)
    pieces = [enc.decode([i]) for i in ids]
    ratio = len(text) / max(len(ids), 1)
    print(f"text     : {text!r}")
    print(f"tokens   : {len(ids)}  (compression {ratio:.2f} chars/token)")
    print(f"ids      : {ids}")
    print(f"pieces   : {pieces}")
    assert enc.decode(ids) == text, "round-trip must be exact"
    print("round-trip OK\n")

for t in [
    "Tokenization drives cost.",
    "internationalization",           # one 'word' -> several subwords
    " token",                          # leading space is part of the token!
    "1234567890",                      # numbers fragment
    "https://example.com/path?q=1",   # URLs fragment
    "東京へようこそ",                    # non-English costs more tokens/idea
    "def add(a, b):\n    return a + b",# code / whitespace
]:
    show(t)
```

## Notes
- `enc.decode([i])` reveals the literal string each token maps to — the best way to *see* subword boundaries.
- Leading spaces matter: `" token"` and `"token"` are different IDs; this affects few-shot formatting and stop sequences.
- Compression ratio (chars/token) drops for non-English and code — the concrete reason those workloads cost more.
- Always match the encoding to the model you actually call (`o200k_base` for gpt-4o/4.1; `cl100k_base` for gpt-4/3.5 and text-embedding-3).
- The round-trip `assert` demonstrates tokenization is lossless and deterministic.

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Tokenization]]
- Related: [[04 Code Snippets/LLM/Token Counting and Cost Estimation]]
