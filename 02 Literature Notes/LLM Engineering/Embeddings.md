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

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Generating and Comparing Embeddings]], [[04 Code Snippets/LLM/Semantic Search Over a Corpus]]
- Distilled: [[03 Permanent Notes/Embeddings Turn Meaning into Geometry]], [[03 Permanent Notes/Normalize Embeddings to Use Dot Product as Cosine]]
- Upstream: [[02 Literature Notes/LLM Engineering/Tokenization]] · Downstream: [[02 Literature Notes/LLM Engineering/Embedding Model Selection]], [[02 Literature Notes/LLM Engineering/Vector Search]]
