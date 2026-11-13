# Embeddings

> Topic package — Domain 1 (Data Representation) · Roadmap Week 09.
> Depth goal: understand what an embedding *is*, the geometry of similarity, and how to generate, normalize, and use embeddings in real retrieval.

## Source
- Track: LLM Engineering (self-directed, FDE roadmap)
- Slide deck: `07 Resources Library/LLM Engineering/Slides/Lesson_03_Embeddings.pptx`
- Hands-on notebook: `07 Resources Library/LLM Engineering/Notebooks/03_Embeddings.ipynb` (runs offline)
- Reference reading: OpenAI text-embedding-3 docs; Sentence-BERT (Reimers & Gurevych, arXiv:1908.10084); MTEB (Muennighoff et al., arXiv:2210.07316); Cohere/Jina embedding docs
- Builds on: [[02 Literature Notes/LLM Engineering/Tokenization]], [[02 Literature Notes/Courses/Deep Learning - Lesson 12 Transformer Models for NLP]]
- Date: 2026-07-18

---

## 1. Mental Model

An **embedding** is a fixed-length vector of floats that encodes the *meaning* of a piece of text, so that **semantic similarity becomes geometric proximity**. Texts about the same thing land near each other in the vector space; unrelated texts land far apart.

This is the trick that makes semantic search, RAG, clustering, classification, deduplication, and recommendation possible: once meaning is a vector, "find similar" becomes "find nearest vectors" — a math operation, not a keyword match.

Contrast with tokenization: tokenization turns text into *IDs* (a lossless, syntactic encoding). Embeddings turn text into *meaning* (a lossy, semantic encoding). Token IDs index a lookup table; embeddings place text in a continuous space where distance = dissimilarity.

> Key intuition: **an embedding model is a "meaning compressor."** It squeezes a whole passage into (say) 1536 numbers such that the geometry of those numbers reflects semantics. Retrieval quality is bounded by how well that compression preserved the distinctions your queries care about.

---

## 2. How It Actually Works

### 2.1 From tokens to one vector
1. Text is tokenized into token IDs (previous topic).
2. A transformer encoder produces a contextual vector per token.
3. Those token vectors are **pooled** into one fixed-length sentence vector — typically **mean pooling** over tokens, or using a special `[CLS]`/last-token vector.
4. The model is *trained* (contrastive learning: pull related pairs together, push unrelated apart) so the pooled vector captures semantics. This is what Sentence-BERT introduced over raw BERT.

### 2.2 The geometry of similarity
The standard similarity is **cosine similarity** — the angle between vectors, ignoring magnitude:

$$\cos(\mathbf{a}, \mathbf{b}) = \frac{\mathbf{a} \cdot \mathbf{b}}{\lVert \mathbf{a} \rVert \, \lVert \mathbf{b} \rVert} \in [-1, 1]$$

- **1** = same direction (semantically identical), **0** = orthogonal (unrelated), **−1** = opposite.
- **Normalization**: if you L2-normalize every vector to unit length ($\lVert \mathbf{v} \rVert = 1$), then cosine similarity **equals the dot product**, and Euclidean distance becomes a monotonic function of cosine. This is why production systems normalize once at ingestion — dot product is faster and equivalent.

$$\text{if } \lVert \mathbf{a} \rVert = \lVert \mathbf{b} \rVert = 1: \quad \cos(\mathbf{a},\mathbf{b}) = \mathbf{a}\cdot\mathbf{b}, \quad \lVert \mathbf{a}-\mathbf{b}\rVert^2 = 2 - 2(\mathbf{a}\cdot\mathbf{b})$$

### 2.3 Dense vs sparse
- **Dense** (what "embedding" usually means): every dimension has a value; captures *semantic* similarity ("car" ≈ "automobile"). Great at meaning, weak at exact terms.
- **Sparse** (BM25 / SPLADE): mostly zeros, one weight per vocabulary term; captures *lexical* similarity (exact words, IDs, codes). Great at precise terms, blind to synonyms.
- **Hybrid** search combines both — dense for meaning, sparse for exact matches (error codes, names). (Covered under Advanced Retrieval; Anthropic's contextual retrieval pairs contextual embeddings with contextual BM25.)

### 2.4 Multi-vector and dimensionality
- **Single-vector** (bi-encoder): one vector per text — fast, scalable, the default.
- **Multi-vector** (ColBERT): one vector *per token*, scored by late interaction — higher quality, more storage/compute.
- **Matryoshka embeddings**: trained so you can *truncate* the vector (e.g., 1536 → 256 dims) and still retain most quality — a built-in quality/cost/storage dial. `text-embedding-3` supports this via a `dimensions` parameter.

### 2.5 Symmetric vs asymmetric
Some tasks are **symmetric** (sentence ↔ sentence similarity); retrieval is **asymmetric** (a short *query* vs a long *document*). Good retrieval models are trained for the asymmetric case, sometimes with **instruction prefixes** ("query: ..." / "passage: ...") — using the wrong prefix silently hurts recall.

---

## 3. Implementation

Assumed stack (pin): `openai>=1.40` (API) or `sentence-transformers>=3.0` (local), `numpy`. Snippets:
- [[04 Code Snippets/LLM/Generating and Comparing Embeddings]]
- [[04 Code Snippets/LLM/Semantic Search Over a Corpus]]

### 3.1 Generate + normalize
```python
from openai import OpenAI
import numpy as np
client = OpenAI()

def embed(texts, model="text-embedding-3-small", dims=None):
    kw = {"dimensions": dims} if dims else {}
    r = client.embeddings.create(model=model, input=texts, **kw)
    v = np.array([d.embedding for d in r.data])
    return v / np.linalg.norm(v, axis=1, keepdims=True)   # L2-normalize
```

### 3.2 Similarity = dot product (after normalization)
```python
def cosine(a, b):                      # normalized -> just the dot product
    return float(a @ b)

q = embed(["how to reset my password"])[0]
docs = embed(["password recovery steps", "shipping policy", "reset your login"])
scores = docs @ q                      # one dot product per doc
```

### 3.3 Local, no-API alternative
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")   # 384-dim, fast, offline
vecs = model.encode(["hello world", "greetings earth"], normalize_embeddings=True)
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Which model** | Pick by task + language + budget, guided by MTEB — not by hype. (See Embedding Model Selection topic.) |
| **Dimensionality** | Higher dims ≈ marginally better quality, more storage/latency. With Matryoshka models, truncate to trade quality for cost deliberately. |
| **Normalize?** | Almost always L2-normalize once at ingestion → use dot product (faster, equals cosine). |
| **Dense vs hybrid** | Dense alone misses exact terms (codes, names). Add sparse/BM25 for enterprise corpora with identifiers. |
| **Query/passage prefixes** | If the model expects instruction prefixes, use them consistently for queries vs documents. |
| **Consistency** | The *same* model + version must embed both corpus and queries. Changing models = re-embed everything. |

---

## 5. Failure Modes & Gotchas

- **Mixing models/versions** across corpus and query → vectors live in different spaces; similarity is meaningless. Re-embed on any model change.
- **Not normalizing** but using dot product → magnitude leaks in; longer texts get artificially higher scores.
- **Wrong query/passage prefix** (asymmetric models) → silent recall drop with no error.
- **Expecting exact-match retrieval from dense vectors** → "Error TS-999" won't reliably match; you need sparse/BM25 for identifiers.
- **Embedding overly long chunks** → dilution (see Chunking); the vector averages away the answer.
- **Assuming cosine encodes truth/quality** → it encodes *similarity of meaning*, not factuality; two confidently-wrong sentences can be very similar.
- **Cross-lingual assumptions** → only multilingual models place translations near each other; monolingual ones don't.

---

## 6. FDE Angle

- Embeddings are the substrate of every RAG/semantic-search deliverable; being fluent in cosine/normalization/dims lets you debug retrieval quality precisely.
- **Cost/storage math**: N documents × dims × 4 bytes = index size; dims and model choice are real infrastructure cost levers a client will ask about.
- When retrieval "misses obvious matches," the cause is usually dense-only search on exact terms → recommend hybrid. This is a common, high-credibility fix.
- Deliverable: a small **semantic-search prototype** over the client's docs proves value in a day and exposes the data-quality issues early.

---

## 7. Self-Check

1. Explain, geometrically, what cosine similarity of 0.9 vs 0.1 means.
2. Why does L2-normalizing let you replace cosine with a dot product? Show the algebra.
3. When will dense embeddings fail and sparse/BM25 succeed? Give a concrete query.
4. What breaks if you embed your corpus with model A and queries with model B?
5. What is a Matryoshka embedding and what dial does it give you?
6. Estimate the index size for 2M chunks at 1536 dims (float32).

---

## 9. Interview Q&A

**Q: Explain, geometrically, what a cosine similarity of 0.9 vs 0.1 means.**
A: Cosine similarity measures the *angle* between two vectors, not their size — it's answering "do these two things point in roughly the same direction in this meaning-space," completely ignoring how long either vector happens to be.

A cosine similarity of 0.9 means the angle between the two vectors is small — they're pointing in almost the same direction. In practical terms, this means the two pieces of text are about very similar things — "how do I reset my password" and "password recovery steps" would likely land somewhere around here, since they're really asking about the same underlying topic even though the wording is different.

A cosine similarity of 0.1 means the angle between the vectors is close to 90 degrees — the two vectors are nearly perpendicular, which in this geometric sense means "basically unrelated." Not opposite, just unconnected — like the difference between a question about password resets and a question about shipping policies. They don't point in opposing directions (that would be closer to -1), they just don't point toward each other at all.

The key habit here is remembering cosine similarity is purely about direction/angle, never about magnitude. Two vectors pointing the exact same way but one being much "longer" than the other would still get a cosine similarity of 1 — length is deliberately ignored, because length isn't part of what makes two meanings similar.

*One-liner: cosine similarity measures the angle between two vectors — near 1 means they point in nearly the same direction (very similar meaning), near 0 means they're roughly perpendicular (unrelated), and it deliberately ignores vector length entirely.*

**Q: Why does L2-normalizing let you replace cosine similarity with a plain dot product? Show the math.**
A: Start with the actual formula for cosine similarity: it's the dot product of two vectors, divided by the product of their two lengths (magnitudes). That division by the lengths is specifically there to cancel out the effect of vector size, so that only the angle matters, not how "long" either vector is.

Now here's the trick: if you take every vector and rescale it ahead of time so its length is always exactly 1 — this is what "L2-normalizing" means — then the division step in the cosine formula becomes dividing by 1 times 1, which is just dividing by 1. Dividing by 1 does nothing. So once every vector already has length 1, the cosine similarity formula collapses down to just the dot product on its own — the division was only ever needed to cancel out magnitude, and if magnitude is already fixed at 1 for everything, there's nothing left to cancel.

This matters practically because a plain dot product is cheaper to compute than cosine similarity — you skip calculating and dividing by two magnitudes for every single comparison. So production systems normalize every vector once, at the time they're first created (ingestion), and then use the cheaper dot product for every search comparison afterward, getting the exact same result as cosine similarity would have given, for less computation per comparison.

*One-liner: cosine similarity divides the dot product by both vectors' lengths to cancel out magnitude — if you normalize every vector to length 1 ahead of time, that division becomes dividing by 1, so the formula collapses into a plain dot product, which is cheaper to compute at search time.*

**Q: When will dense embeddings fail and sparse/BM25 succeed? Give a concrete example.**
A: Dense embeddings are built to capture *meaning* — they're good at recognizing that two different wordings are really asking about the same idea. But that strength becomes a weakness for anything where the *exact characters* matter more than the general topic.

Take a concrete example: a user searches for "error TS-999" in a technical support knowledge base. A dense embedding model has likely never seen this specific error code before, or seen it rarely — it has no strong semantic "meaning" to anchor onto, since it's essentially an arbitrary identifier, not a concept. The embedding might end up placing this query somewhere vaguely near "error codes" or "troubleshooting" in general, but it has no special mechanism for recognizing that a document containing the literal string "TS-999" is almost certainly the single most relevant one — to the embedding, "TS-999" and "TS-998" might look nearly identical, even though for a human searching by error code, only an exact match actually matters.

This is exactly the situation sparse retrieval (like BM25) excels at. BM25 works by directly matching words and terms that literally appear in both the query and the document, weighted by how rare and distinctive those terms are. An exact, unusual string like "TS-999" is precisely the kind of rare, distinctive term BM25 rewards heavily — if a document contains that exact text, BM25 will surface it near the top, regardless of whether an embedding model understood any deeper "meaning" behind it. This is exactly why production retrieval systems often combine both: dense for conceptual, meaning-based queries, and sparse for exact codes, names, IDs, and other identifiers where precision beats meaning.

*One-liner: dense embeddings are tuned for meaning and often can't distinguish arbitrary identifiers like "error TS-999" from similar-looking ones — sparse/BM25 retrieval matches exact rare terms directly, which is exactly what identifiers, codes, and names need, so combining both covers meaning-based and exact-match queries together.*

**Q: What breaks if you embed your corpus with model A and search it using model B?**
A: The entire thing breaks, even though nothing throws an obvious error — and that's what makes this mistake particularly dangerous.

Here's why: each embedding model learns its own internal "meaning space," shaped by its own training process. Two different models don't produce vectors in the same coordinate system — a vector from model A living at some particular set of numbers has no guaranteed relationship to a vector from model B living at a similar-looking set of numbers. "Similar" vectors from two different models aren't actually comparable just because they happen to be made of the same count of floating-point numbers with roughly the same scale.

So if your documents were embedded using model A, and you then embed a new search query using model B, and compare that query vector against your document vectors using cosine similarity or dot product — you'll get similarity scores back. They're not meaningless numbers, computation-wise. But they don't actually reflect real semantic similarity anymore, because the two sets of vectors were never placed in a shared, comparable space to begin with. The scores you get back are essentially noise dressed up as a real similarity signal — sometimes right by coincidence, usually not meaningfully ranked at all.

This is why the rule is absolute: the exact same model and version has to be used to embed both your document corpus and every search query against it. If you ever switch embedding models — even to a newer version of the same model family — you have to re-embed your entire corpus from scratch. There's no way to "convert" embeddings from one model's space into another's after the fact.

*One-liner: different embedding models place text in different, incompatible meaning-spaces, so comparing a model-B query against model-A documents gives similarity scores that look valid but aren't meaningful — the same model and version must embed both the corpus and every query, and switching models means re-embedding everything from scratch.*

**Q: What is a Matryoshka embedding, and what dial does it give you?**
A: Picture Russian nesting dolls — each smaller doll fits inside a bigger one, and each one is still a complete, functional doll on its own. A Matryoshka embedding is trained the same way: it's a single, large embedding vector (say, 1536 numbers long) that's deliberately trained so that the *first* 256 numbers of it, taken alone, already form a decent, usable embedding by themselves — and the first 512 numbers form an even better one, and so on, all the way up to using the full 1536.

Normally, if you wanted a smaller, cheaper embedding, you'd have to train (or find) a genuinely different, smaller model — there's no way to just chop a regular embedding in half and expect it to still mean anything, since every number in a normal embedding depends on the full set to make sense together. Matryoshka training specifically arranges the information so that earlier dimensions carry the most essential meaning, and later dimensions add progressively finer detail on top — similar to how a blurry low-resolution image is still recognizable, and more detail sharpens it further rather than being required for it to make any sense at all.

What this gives you in practice is a single dial you control *after* the embeddings have already been generated: you can truncate a 1536-dimension vector down to 256 dimensions when you need a smaller index (less storage, less memory, faster search), accepting a bit of quality loss — and you can switch back to the full size when you need maximum retrieval quality, all without retraining or re-generating anything. It turns "pick a dimension size" from a fixed decision baked in at model-selection time into a flexible tradeoff you can adjust per use case.

*One-liner: a Matryoshka embedding is trained so that truncating it (using just the first N numbers instead of all of them) still gives a usable, if slightly lower-quality, embedding — turning vector size into a dial you can adjust after the fact to trade quality for storage and speed, instead of a fixed choice you make once.*

**Q: Estimate the index size for 2 million chunks at 1536 dimensions, stored as float32.**
A: Work this out from the basic unit: one float32 number takes 4 bytes of storage, no matter what it represents. Each chunk's embedding has 1536 of these numbers, so one embedding takes `1536 × 4 = 6,144 bytes`, or about 6 KB.

Now multiply by how many chunks you have: `2,000,000 chunks × 6,144 bytes = 12,288,000,000 bytes`. Converting that to a more readable unit: dividing by 1 billion (since 1 GB is roughly 1 billion bytes) gives about 12.3 GB.

So storing the raw vectors alone for 2 million chunks at this size takes roughly 12 GB — and that's before accounting for whatever index structure sits on top (like the graph structure in HNSW, which adds its own overhead on top of the raw vectors) or any metadata stored alongside each chunk. This is exactly the kind of back-of-envelope math worth being able to do quickly, since "how big will this be, and what will it cost to host" is one of the first questions that comes up when planning real infrastructure.

*One-liner: each float32 number is 4 bytes, so a 1536-dimension embedding is `1536 × 4 = 6,144 bytes` (~6 KB) — multiplied by 2 million chunks, that's about 12.3 GB just for the raw vectors, before adding index structure or metadata overhead.*

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Generating and Comparing Embeddings]], [[04 Code Snippets/LLM/Semantic Search Over a Corpus]]
- Distilled: [[03 Permanent Notes/Embeddings Turn Meaning into Geometry]], [[03 Permanent Notes/Normalize Embeddings to Use Dot Product as Cosine]]
- Upstream: [[02 Literature Notes/LLM Engineering/Tokenization]] · Downstream: [[02 Literature Notes/LLM Engineering/Embedding Model Selection]], [[02 Literature Notes/LLM Engineering/Vector Search]]
