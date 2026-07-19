# Late Chunking with Token Embeddings

## Purpose
- Implement "late chunking" (Jina AI pattern) from §2.4(c): embed the whole document with a long-context model that emits token-level embeddings, then mean-pool token embeddings per chunk. Each chunk vector carries full-document context with NO per-chunk LLM call.

## Language
- Python

## Snippet
```python
# pip install "transformers>=4.44" torch numpy
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

# A long-context embedding model that exposes token-level hidden states.
MODEL = "jinaai/jina-embeddings-v3"   # or another long-context embedder
tokenizer = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL, trust_remote_code=True).eval()

def token_embeddings(text, max_length=8192):
    enc = tokenizer(text, return_tensors="pt", truncation=True,
                    max_length=max_length, return_offsets_mapping=True)
    offsets = enc.pop("offset_mapping")[0].tolist()
    with torch.no_grad():
        out = model(**enc)
    # last_hidden_state: [1, num_tokens, dim] -> contextualized per-token vectors
    return out.last_hidden_state[0].numpy(), offsets

def mean_pool(token_vecs, start_tok, end_tok):
    # eq. 2.4c : average the token embeddings spanning the chunk
    span = token_vecs[start_tok:end_tok]
    return span.mean(axis=0)

def late_chunk(text, char_spans):
    """char_spans: list of (char_start, char_end) chunk boundaries from ANY
    chunker (recursive, semantic, structural). Late chunking only changes how
    the VECTOR is produced, not where the text is cut."""
    tok_vecs, offsets = token_embeddings(text)

    def char_to_token(char_idx):
        for t, (a, b) in enumerate(offsets):
            if a <= char_idx < b or (a == b == 0 and t == 0):
                return t
        return len(offsets) - 1

    vectors = []
    for c_start, c_end in char_spans:
        t_start, t_end = char_to_token(c_start), char_to_token(c_end)
        vectors.append(mean_pool(tok_vecs, t_start, max(t_end, t_start + 1)))
    return np.array(vectors)

if __name__ == "__main__":
    text = open("report.txt").read()
    # boundaries can come from your normal chunker; here: naive 800-char blocks
    spans = [(i, min(i + 800, len(text))) for i in range(0, len(text), 800)]
    vecs = late_chunk(text, spans)
    print(f"{len(vecs)} chunk vectors of dim {vecs.shape[1]}, "
          f"each aware of the full document context")
```

## Notes
- **Key inversion vs. normal chunking**: you embed the *whole document first* (so attention spans everything), then pool token vectors per chunk. The chunk text is identical to normal chunking — only the vector is "globally aware."
- Cheaper than contextual retrieval: no LLM call per chunk, just one forward pass over the document (bounded by the model's context length, e.g., 8k tokens).
- Requires a model that (a) has a long context window and (b) exposes token-level `last_hidden_state`. Pure API embedders that return only one vector per input can't do this.
- Documents longer than the model context need "long late chunking" (overlapping windows of token embeddings) — a further extension.
- Combine freely with any boundary strategy (recursive/semantic/structural); late chunking is orthogonal to *where* you cut.

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
- Distilled: [[03 Permanent Notes/Contextual Retrieval Restores Lost Chunk Context]]
- Related: [[04 Code Snippets/LLM/Semantic Chunking From Scratch]]
