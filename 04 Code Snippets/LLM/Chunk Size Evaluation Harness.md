# Chunk Size Evaluation Harness

## Purpose
- Choose chunk size/overlap/strategy with evidence, not intuition. Sweeps configurations, builds a tiny vector index for each, and measures retrieval quality (recall@k and MRR) against a labeled question set. This is the FDE deliverable that justifies a chunking config.

## Language
- Python

## Snippet
```python
# pip install numpy openai langchain-text-splitters tiktoken
import numpy as np
from openai import OpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

client = OpenAI()

def embed(texts, model="text-embedding-3-small"):
    resp = client.embeddings.create(model=model, input=texts)
    return np.array([d.embedding for d in resp.data])

def build_index(text, chunk_size, overlap):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="o200k_base", chunk_size=chunk_size, chunk_overlap=overlap
    )
    chunks = [c.page_content for c in splitter.create_documents([text])]
    return chunks, embed(chunks)

def retrieve(query_vec, chunk_vecs, k):
    # cosine similarity; vectors from text-embedding-3 are ~unit length
    sims = chunk_vecs @ query_vec / (
        np.linalg.norm(chunk_vecs, axis=1) * np.linalg.norm(query_vec) + 1e-9)
    return np.argsort(-sims)[:k]

def evaluate(text, qa, configs, k=5):
    """qa: list of {"question": str, "answer_substring": str} — the gold signal
    is whether a retrieved chunk actually CONTAINS the answer text."""
    results = []
    for cs, ov in configs:
        chunks, cvecs = build_index(text, cs, ov)
        qvecs = embed([q["question"] for q in qa])
        hits, rr = 0, []
        for q, qv in zip(qa, qvecs):
            top = retrieve(qv, cvecs, k)
            ranks = [r for r, idx in enumerate(top, 1)
                     if q["answer_substring"].lower() in chunks[idx].lower()]
            if ranks:
                hits += 1
                rr.append(1.0 / ranks[0])   # reciprocal rank of first hit
            else:
                rr.append(0.0)
        results.append({
            "chunk_size": cs, "overlap": ov, "n_chunks": len(chunks),
            f"recall@{k}": round(hits / len(qa), 3),
            "MRR": round(float(np.mean(rr)), 3),
        })
    return sorted(results, key=lambda r: (-r[f"recall@{k}"], -r["MRR"]))

if __name__ == "__main__":
    text = open("report.txt").read()
    qa = [
        {"question": "How much did the supplier contract cut costs?",
         "answer_substring": "cut costs by 40%"},
        # ... 20-50 labeled questions give a stable signal
    ]
    configs = [(256, 25), (400, 60), (500, 75), (800, 120), (1200, 0)]
    for row in evaluate(text, qa, configs, k=5):
        print(row)
```

## Notes
- **The gold signal is substring containment**: did any retrieved chunk actually contain the answer text? Cheap, objective, and enough to rank configs. For nuanced answers, upgrade the judge to an LLM-as-a-judge groundedness check.
- **recall@k** = fraction of questions whose answer appeared in the top-k chunks (does retrieval even surface the answer?). **MRR** = how highly it ranked (quality of ordering). Track both.
- Build the labeled `qa` set once (20–50 real questions) — it becomes your regression suite for *every* future retrieval change, not just chunking.
- Expect a non-monotonic curve: recall usually peaks at a middle size and falls off for both tiny (fragmentation) and huge (dilution, §2.4d) chunks. The peak is your config.
- Swap `build_index` to call semantic / late chunking to compare strategies on the same questions and index size.

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
- Related: [[04 Code Snippets/LLM/Recursive and Token-Aware Chunking]], [[04 Code Snippets/LLM/Semantic Chunking From Scratch]]
- Forward link: Retrieval Evaluation (recall@k, MRR, NDCG) — to be added
