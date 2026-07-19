# Embedding Model Selection

> Topic package — Domain 1 (Data Representation) · Roadmap Week 09.
> Depth goal: choose the right embedding model for a workload using evidence (MTEB + your own eval), balancing quality, dimensionality, cost, latency, and constraints.

## Source
- Track: LLM Engineering (self-directed, FDE roadmap)
- Slide deck: `07 Resources Library/LLM Engineering/Slides/Lesson_04_Embedding_Model_Selection.pptx`
- Hands-on notebook: `07 Resources Library/LLM Engineering/Notebooks/04_Embedding_Model_Selection.ipynb` (runs offline)
- Reference reading: MTEB (Muennighoff et al., arXiv:2210.07316) — 56 datasets, 8 tasks, 112 languages; MTEB leaderboard; OpenAI/Cohere/Voyage/Jina/BGE/E5 model cards
- Builds on: [[02 Literature Notes/LLM Engineering/Embeddings]]
- Date: 2026-07-18

---

## 1. Mental Model

There is no single "best" embedding model — only the best model **for a workload**. Selection is a **multi-objective decision**: retrieval quality, dimensionality (storage/latency), max input length, language coverage, domain fit, hosting model (API vs self-host), cost, and privacy constraints. The skill is turning "which model?" into a scored comparison on *your* data.

**MTEB** (Massive Text Embedding Benchmark) is the industry starting point: 56 datasets across 8 task types (retrieval, reranking, clustering, classification, STS, summarization, pair-classification, bitext mining), spanning up to 112 languages. Use it to build a shortlist — but never as the final word, because your domain and queries differ from the benchmark.

> Key intuition: **MTEB narrows the field; your own retrieval eval picks the winner.** The leaderboard tells you which models are plausible; a 50-question recall@k test on the client's corpus tells you which one actually works here.

---

## 2. How It Actually Works

### 2.1 The decision axes (what you're trading)
- **Retrieval quality** — the MTEB *Retrieval* sub-score matters far more than the headline average for RAG. A great clustering model can be a mediocre retriever.
- **Dimensionality** — drives index size (`N × dims × bytes`) and query latency. Matryoshka models let you truncate to trade quality for cost.
- **Max sequence length** — can the model ingest your chunk size? Long-context embedders (8k+) reduce fragmentation and enable late chunking.
- **Language & domain** — multilingual vs English-only; general vs domain-tuned (code, legal, biomedical). Domain fit often beats leaderboard rank.
- **Hosting** — API (OpenAI, Cohere, Voyage) = zero ops, per-token cost, data leaves your boundary; self-host (BGE, E5, GTE, Nomic, Jina open) = infra + GPU, but private and fixed-cost.
- **Cost model** — API: $/1M tokens at ingestion + per query. Self-host: GPU/CPU amortized. At high volume self-host often wins; at low volume API wins.

### 2.2 The two families you'll compare
- **Proprietary API**: `text-embedding-3-small/large` (OpenAI, Matryoshka), Cohere `embed-v3` (has a compression-friendly int8/binary mode), Voyage, Jina. Strong, zero-ops, but recurring cost + data egress.
- **Open weights**: BGE, E5 / multilingual-e5, GTE, Nomic-embed, Jina-embeddings. Competitive quality, self-hostable, free at inference, but you own the serving.

### 2.3 Quantization & compression (a real lever)
Vectors don't have to be float32. **int8** quantization (1 byte/dim) cuts index size 4×; **binary** embeddings (1 bit/dim) cut it 32× with a rescoring step to recover quality. Cohere and others train models specifically to survive this. This turns "we can't afford the index" into "we can."

### 2.4 The math of the tradeoff
Index size and monthly cost are explicit:

$$\text{index bytes} = N_{\text{chunks}} \times d \times b, \quad b = \{4\text{ (f32)}, 1\text{ (int8)}, 0.125\text{ (binary)}\}$$

$$\text{ingest cost} \approx \frac{N_{\text{chunks}} \times \bar{t}_{\text{chunk}}}{10^6} \times p_{\text{embed}}$$

where `d` = dims, `\bar{t}` = avg tokens/chunk, `p` = $/1M tokens. Halving `d` (Matryoshka) or moving f32→int8 are direct, quantifiable savings you present to a client.

### 2.5 The selection procedure (do this, not vibes)
1. Constraints filter: language, max length, privacy (API allowed?), budget → candidate list.
2. MTEB shortlist: rank candidates by the *Retrieval* score for your language.
3. Build a **golden set**: 30–100 real queries with known-relevant docs from the client corpus.
4. Evaluate each candidate: recall@k, MRR/NDCG, plus latency and $/1M.
5. Pick on the quality–cost Pareto frontier; document the tradeoff.

---

## 3. Implementation

Assumed stack (pin): `mteb`, `sentence-transformers>=3.0`, `numpy`, optional `openai>=1.40`. Snippet:
- [[04 Code Snippets/LLM/Comparing Embedding Models on a Golden Set]]

### 3.1 Score candidates on your own golden set
```python
import numpy as np

def recall_mrr(model_embed, queries, corpus, gold, k=5):
    C = model_embed(corpus)                      # [N, d], normalized
    Q = model_embed([q for q, _ in queries])     # [Q, d], normalized
    hits, rr = 0, []
    for (q, _), qv in zip(queries, Q):
        order = np.argsort(-(C @ qv))[:k]
        rel = gold[q]                            # set of relevant corpus indices
        ranks = [r for r, idx in enumerate(order, 1) if idx in rel]
        if ranks: hits += 1; rr.append(1/ranks[0])
        else: rr.append(0.0)
    return {"recall@k": hits/len(queries), "MRR": float(np.mean(rr))}
```

### 3.2 Estimate the cost/size of each choice
```python
def index_cost(n_chunks, dims, bytes_per_dim=4, avg_tokens=400, price_per_m=0.02):
    size_gb = n_chunks * dims * bytes_per_dim / 1e9
    ingest_usd = n_chunks * avg_tokens / 1e6 * price_per_m
    return {"index_GB": round(size_gb, 2), "ingest_USD": round(ingest_usd, 2)}
```

---

## 4. Design Decisions & Tradeoffs

| Situation | Lean toward |
|---|---|
| Low volume, want zero ops | API (text-embedding-3-small, Cohere embed-v3) |
| High volume / privacy / fixed cost | Self-host open model (BGE, E5, GTE) |
| Multilingual corpus | multilingual-e5, BGE-m3, Cohere multilingual |
| Long documents / late chunking | Long-context embedder (Jina v3, nomic 8k) |
| Storage-constrained at scale | Matryoshka truncation + int8/binary quantization |
| Domain-specific (code/legal/bio) | Domain-tuned model, verified on your eval |
| Need best quality, cost secondary | text-embedding-3-large / top MTEB retrieval model |

Rule: **decide dimensionality and quantization together with the model** — they are one joint choice about the quality/cost point.

---

## 5. Failure Modes & Gotchas

- **Choosing by MTEB average, not the Retrieval sub-score** → a clustering champion that under-retrieves.
- **Trusting the leaderboard on your domain** → benchmark ≠ your queries; always run a local eval.
- **Ignoring max sequence length** → chunks silently truncated at embed time (tie to Tokenization/Chunking).
- **Forgetting re-embedding cost of switching** → changing models means re-embedding the *entire* corpus; treat model choice as semi-permanent.
- **API data egress in regulated settings** → some clients can't send data to a hosted embedder; check before shortlisting.
- **Comparing models at different dims/normalization** → unfair; hold the eval protocol fixed.
- **Overfitting to a tiny golden set** → 30–100 queries minimum; too few and noise picks the "winner."

---

## 6. FDE Angle

- "Which embedding model should we use?" is a question you'll get on nearly every engagement — answer it with a **scored comparison on their data**, not a leaderboard screenshot. That is the credibility move.
- Bring the **cost/size math**: show index GB and monthly ingest/query cost per candidate; it reframes the choice as business, not just ML.
- Flag **privacy/hosting** early — it can eliminate API models entirely and change the whole architecture.
- Deliverable: a one-page **embedding model selection memo** — shortlist, recall@k/MRR on the golden set, cost table, recommendation + rationale.

---

## 7. Self-Check

1. Why is the MTEB Retrieval sub-score more relevant for RAG than the average?
2. Give the formula for index size and use it: 3M chunks, 1024 dims, int8.
3. When does self-hosting an open model beat an API embedder?
4. What must happen to the corpus if you switch embedding models, and why is that costly?
5. What is Matryoshka truncation and how does it interact with quantization?
6. Outline the 5-step selection procedure from constraints to final pick.

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Comparing Embedding Models on a Golden Set]]
- Distilled: [[03 Permanent Notes/Pick Embedding Models by Retrieval Eval Not Leaderboard]]
- Upstream: [[02 Literature Notes/LLM Engineering/Embeddings]] · Related: [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
