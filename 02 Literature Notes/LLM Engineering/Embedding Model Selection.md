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

---

## 9. Interview Q&A

**Q: Why is the MTEB Retrieval sub-score more relevant for RAG than the overall average?**
A: MTEB isn't one single test — it's a bundle of very different tasks (retrieval, clustering, classification, summarization, and more) all averaged together into one headline number. A model can be excellent at one of these tasks and mediocre at another, and the overall average hides that difference completely.

For a RAG system, the only thing that actually matters is retrieval: given a query, can the model find the right documents? A model might score extremely well on, say, clustering (grouping similar documents together without a specific query) while being only average at retrieval specifically — and if you picked that model based on its strong overall average, you could easily end up with a worse retriever than a model that scored lower overall but higher specifically on retrieval.

So the right habit is to always look at the Retrieval sub-score directly, not the blended average, because that sub-score is measuring the actual skill your RAG system depends on. The average is answering "how good is this model in general," while Retrieval is answering the one question you actually care about: "will this model find the right document for a given query."

*One-liner: MTEB's overall average blends many unrelated tasks together, so a model can top the average while being mediocre at retrieval specifically — for RAG, always compare models on the Retrieval sub-score directly, since that's the one skill your system actually depends on.*

**Q: Give the formula for index size, and use it: 3 million chunks, 1024 dimensions, stored as int8.**
A: The formula is: number of chunks times dimensions times bytes per number. The "bytes per number" part depends on your storage precision — a regular float32 number takes 4 bytes, but int8 quantization stores each number in just 1 byte instead, trading a little precision for a lot less space.

Plugging in the numbers: `3,000,000 chunks × 1024 dimensions × 1 byte (int8) = 3,072,000,000 bytes`. Converting that to gigabytes (dividing by roughly 1 billion) gives about 3.07 GB.

Worth noticing: if this had been stored as float32 instead of int8, it would have been 4 times larger — about 12.3 GB. That's the entire point of int8 quantization: you get the same number of vectors, same dimensions, but a 4x smaller footprint, in exchange for a small amount of precision loss per number. This is exactly the kind of math you'd use to tell a client "we can fit this index on a single commodity server with quantization, instead of needing much more expensive memory."

*One-liner: index size is chunks × dimensions × bytes-per-number — with 3M chunks at 1024 dims in int8 (1 byte each), that's about 3.07 GB, a full 4x smaller than storing the same vectors as float32.*

**Q: When does self-hosting an open embedding model beat using an API?**
A: This comes down to a tradeoff between fixed cost and variable cost, plus two non-cost factors: privacy and operational effort.

An API charges you per token, every single time you embed something — so cost scales directly with how much you're embedding. Self-hosting an open model instead means you pay for your own GPU/server infrastructure, which is roughly a fixed monthly cost no matter how much you actually embed with it (within its capacity). At low volume, the API usually wins, because you're not paying for idle infrastructure you don't need. But as embedding volume grows large enough, the ongoing per-token API cost can end up exceeding what a fixed-cost server would have cost for the same workload — at that point, self-hosting becomes the cheaper option.

Beyond pure cost, there are two other situations that push toward self-hosting regardless of volume. First: privacy and regulatory constraints — some clients (financial, healthcare, government) are not allowed to send their data to an external API provider at all, full stop, which eliminates the API option entirely no matter how convenient it would be. Second: needing a fixed, predictable cost rather than a variable one — a business might prefer knowing exactly what they're paying each month rather than having costs scale unpredictably with usage.

The tradeoff, of course, is that self-hosting means you now own the operational burden — you have to manage the GPU infrastructure, keep it running reliably, and handle scaling it yourself, instead of the API provider doing all of that for you.

*One-liner: APIs charge per token and need zero infrastructure, which wins at low volume — self-hosting has a fixed infrastructure cost that can beat API pricing at high volume, and becomes necessary regardless of volume when data can't leave your own environment for privacy or regulatory reasons.*

**Q: What has to happen to the corpus if you switch embedding models, and why is that costly?**
A: You have to re-embed your entire corpus from scratch — every single document has to be run through the new model again, generating entirely new vectors to replace the old ones.

Here's why there's no shortcut: as covered in the Embeddings topic, different embedding models place text into completely different, incompatible vector spaces. The old vectors, generated by the old model, have no meaningful relationship to vectors from the new model — you can't "translate" or "convert" them, since the new model doesn't have any special way to adjust an old model's output into its own space. The only correct option is throwing away all the old vectors and generating fresh ones from the new model, for every document.

This is costly in two concrete ways. First, there's a real, direct dollar cost: if you're using a paid API, re-embedding a large corpus (potentially millions of documents) means paying the per-token ingestion cost all over again, for content you'd already paid to embed once before. Second, there's operational cost: for a large corpus, this re-embedding process can take significant time to run, and depending on how your system is built, you may need to manage a cutover carefully (keeping the old index running until the new one is fully ready) rather than having any downtime in search availability.

This is exactly why embedding model choice should be treated as a semi-permanent decision, not something to casually swap later — switching isn't like changing a configuration setting, it's closer to rebuilding a significant piece of your data infrastructure.

*One-liner: switching embedding models means re-embedding your entire corpus from scratch, since vectors from different models aren't compatible or convertible — this costs real money (re-paying ingestion costs) and real time, which is why model choice should be treated as a semi-permanent decision, not something to change casually.*

**Q: What is Matryoshka truncation, and how does it interact with quantization?**
A: Matryoshka truncation (covered in the Embeddings topic) is the ability to chop a long embedding vector down to just its first N numbers and still get a usable, if slightly lower-quality, embedding — because the model was specifically trained so that earlier dimensions carry the most essential meaning, with later ones adding progressively finer detail on top.

Quantization is a separate, independent lever: instead of changing *how many* numbers you keep, it changes *how much space each number takes* — storing each number in fewer bits (int8 uses 1 byte instead of 4, binary uses just 1 bit) instead of the full-precision float32.

Here's why they interact well together rather than competing: truncation shrinks the vector by removing dimensions, while quantization shrinks it by making each remaining dimension cheaper to store — these are two different axes of the same overall "how big is this vector" problem, and you can apply both at once. Take a 1536-dimension float32 embedding (6,144 bytes). Truncate it with Matryoshka down to 256 dimensions, and you're down to 1,024 bytes just from truncation. Now also quantize those 256 remaining dimensions to int8, and you're down to 256 bytes total — a combined 24x reduction in size from the original, achieved by stacking two independent savings levers rather than relying on either one alone to do all the work.

*One-liner: Matryoshka truncation reduces how many dimensions you keep, while quantization reduces how much space each remaining dimension takes — they're independent levers that stack together, so you can combine both (e.g. truncate to 256 dims, then store those as int8) for a much bigger combined size reduction than either one alone.*

**Q: Outline the 5-step procedure for selecting an embedding model, from constraints to final pick.**
A: The procedure is designed to avoid picking a model based on hype or a leaderboard screenshot — it narrows the field with hard constraints first, then settles the final decision with real evidence from your own data.

Step 1: filter by hard constraints. Some things aren't negotiable — what languages do you need to support, what's the longest chunk you'll need to embed, can data legally leave your environment to use an API, and what's the budget. These constraints immediately eliminate any model that simply can't meet them, before you even start comparing quality.

Step 2: build a shortlist using MTEB, specifically the Retrieval sub-score for your target language(s) — not the overall average. This narrows a huge field of possible models down to a handful of serious contenders worth testing directly.

Step 3: build a golden set — somewhere between 30 and 100 real queries from your actual use case, each with the documents that should be considered genuinely relevant already labeled. This is the data your evaluation will actually run on, and it needs to reflect your real workload, not a generic benchmark.

Step 4: run each shortlisted candidate against that golden set and measure real retrieval metrics — recall@k (did it find the right document at all, within the top k results) and MRR or NDCG (did it rank the right document near the top) — along with practical factors like latency and cost per million tokens.

Step 5: make the final pick by weighing quality against cost together, rather than picking the single highest-quality option regardless of price — and write down the reasoning, since this decision is expensive to reverse later (see the re-embedding cost question above).

*One-liner: filter candidates by hard constraints (language, length, privacy, budget), shortlist with MTEB's Retrieval score, build a 30-100 query golden set from your own data, measure recall@k/MRR plus cost and latency on that golden set, then pick based on the quality-cost tradeoff and document why.*

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Comparing Embedding Models on a Golden Set]]
- Distilled: [[03 Permanent Notes/Pick Embedding Models by Retrieval Eval Not Leaderboard]]
- Upstream: [[02 Literature Notes/LLM Engineering/Embeddings]] · Related: [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
