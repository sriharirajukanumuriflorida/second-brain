# Chunking Strategies

> Topic package — Domain 1 (Data Representation) · maps to Roadmap Week 13 (RAG System Design) & Week 14 (Retrieval Quality).
> Depth goal: understand *why* chunking decides RAG quality, and be able to implement production chunkers today.

## Source
- Track: LLM Engineering (self-directed, FDE roadmap)
- Slide deck: `07 Resources Library/LLM Engineering/Slides/Lesson_01_Chunking_Strategies.pptx`
- Hands-on notebook: `07 Resources Library/LLM Engineering/Notebooks/01_Chunking_Strategies.ipynb` (runs offline)
- Related lessons: builds on [[02 Literature Notes/Courses/Deep Learning - Lesson 12 Transformer Models for NLP]]
- Reference reading: Anthropic "Contextual Retrieval" (2024, −49%/−67% failed retrievals); Pinecone "Chunking Strategies for LLM Applications" (2025); Jina AI "Late Chunking" (2024); LangChain text-splitter docs; Liu et al. "Lost in the Middle" (arXiv:2307.03172)
- Date: 2026-07-18

---

## 1. Mental Model

**The problem chunking solves:** Retrieval systems search over *pieces* of documents, not whole documents. You embed each piece into a vector, store it, and at query time retrieve the top-k most similar pieces to feed the LLM. **Chunking is the act of cutting source documents into those pieces.**

Why not embed whole documents?
- **Embedding dilution** — a single vector for a 30-page PDF averages away the specific passage that answers the question. One vector cannot represent many distinct ideas well.
- **Context budget** — you can only fit so many tokens into the LLM prompt. You want to inject the *relevant* 500 tokens, not the whole 30 pages.
- **Precision of retrieval** — smaller, topically-focused chunks match a specific query more sharply.

Why not chunk into tiny pieces (e.g., one sentence)?
- **Context loss** — a sentence like "This reduced latency by 40%." is useless without knowing what "this" refers to. The chunk must carry enough surrounding context to stand alone.

**So chunking is a tension:** small enough to be precise and embed cleanly, large enough to be self-contained and meaningful. Everything below is about resolving that tension for real documents.

> Key intuition: **the chunk is the unit of retrieval AND the unit of grounding.** If the answer isn't fully inside a retrieved chunk (plus its neighbors), the LLM cannot ground on it and will either omit it or hallucinate. Bad chunking caps the ceiling of the entire RAG system — no reranker or bigger model fixes it downstream.

### Where chunking sits in the pipeline

```mermaid
flowchart LR
    A[Raw documents<br/>PDF / HTML / MD / code] --> B[Ingestion & parsing<br/>OCR, layout, cleaning]
    B --> C[**Chunking**<br/>split + metadata]
    C --> D[Embedding model<br/>chunk -> vector]
    D --> E[(Vector store<br/>+ metadata index)]
    F[User query] --> G[Query embedding]
    G --> E
    E --> H[Top-k retrieval<br/>+ rerank]
    H --> I[Prompt assembly<br/>context + question]
    I --> J[LLM answer<br/>grounded + cited]
    style C fill:#ff9900,stroke:#333,color:#000
```

Chunking is upstream of everything and downstream of ingestion quality. Its output — the chunk text + metadata — is frozen into the vector store, so a mistake here propagates to every future query until you re-index.

---

## 2. How It Actually Works

### 2.1 The core parameters
- **Chunk size** — measured in **tokens** (not characters), because both the embedding model and the LLM think in tokens. A "500-token" chunk is the meaningful unit; "500 characters" varies wildly by language and content.
- **Chunk overlap** — how many tokens each chunk shares with its neighbor. Overlap prevents an idea that straddles a boundary from being split in half. Typical: 10–20% of chunk size.
- **Boundary respect** — where you are *allowed* to cut. Cutting mid-sentence or mid-code-block destroys meaning. Good splitters cut on natural boundaries (paragraph → sentence → word) in priority order.

### 2.2 The strategy ladder (from naive to advanced)

**(a) Fixed-size / character splitting** — cut every N characters. Simple, fast, and bad: it slices through sentences and words. Use only as a baseline.

**(b) Recursive character splitting** — the workhorse default. Try to split on the largest natural separator first (`\n\n` paragraphs), and only if a piece is still too big, recurse to smaller separators (`\n` lines → `. ` sentences → ` ` words). Respects structure while guaranteeing a max size. This is the sane default for most text.

**(c) Token-aware splitting** — same as recursive, but size is measured with the actual tokenizer (e.g., tiktoken for OpenAI, the model's tokenizer for others) so chunks never exceed the embedding model's input limit and cost is predictable.

**(d) Structure-aware / document-specific splitting** — respect the document's *format*: split Markdown by headers, code by functions/classes, HTML by tags, PDFs by layout blocks. Keeps semantically-coherent units intact and lets you attach structural metadata (which section a chunk came from).

**(e) Semantic chunking** — don't cut at fixed sizes at all. Embed each sentence, then start a new chunk wherever the *embedding similarity between consecutive sentences drops* below a threshold (a topic shift). Produces variable-size, topically-coherent chunks. More expensive (embeds every sentence) and only sometimes worth it.

**(f) Contextual retrieval (Anthropic pattern)** — the highest-ROI recent technique. For each chunk, use an LLM to prepend a short, document-aware context sentence ("This chunk is from the 2023 10-K, Risk Factors section, discussing supply-chain exposure...") *before embedding it*. This restores the context that chunking stripped away, dramatically improving retrieval on chunks that were otherwise ambiguous. Combine with BM25 for best recall.

**(g) Late chunking (Jina pattern)** — invert the order: embed the *whole document* with a long-context embedding model first (so every token's embedding already "sees" the full document), *then* pool token embeddings into per-chunk vectors. Each chunk vector carries global context without an extra LLM call. Requires a long-context embedding model that outputs token-level embeddings.

### 2.3 What "good" looks like
A well-chunked corpus has chunks that: (1) are self-contained enough to answer a question alone, (2) fit comfortably in the embedding model's context, (3) carry metadata (source, section, page) for filtering and citation, and (4) don't fragment atomic units (tables, code blocks, list items).

### 2.4 The math of chunking

**(a) Number of chunks from size + overlap.** For a document of `T` tokens, chunk size `c`, and overlap `o` (with stride `s = c − o`), the chunk count is:

$$N = \left\lceil \frac{T - o}{c - o} \right\rceil = \left\lceil \frac{T - o}{s} \right\rceil$$

This drives **storage and cost**: every chunk is one stored vector and one embedding call. Raising overlap from 0 → 20% of `c` shrinks the stride `s` and multiplies `N` (and cost) by roughly `c / (c − o)`. Example: `T=10000, c=500, o=75 → N = ⌈9925/425⌉ = 24` chunks; at `o=0` it's 20 chunks — a 20% storage increase to buy boundary safety.

**(b) Semantic breakpoint detection.** Embed each sentence `i` into vector $\mathbf{e}_i$. The *dissimilarity* between consecutive sentences uses cosine distance:

$$d_i = 1 - \cos(\mathbf{e}_i, \mathbf{e}_{i+1}) = 1 - \frac{\mathbf{e}_i \cdot \mathbf{e}_{i+1}}{\lVert \mathbf{e}_i \rVert \, \lVert \mathbf{e}_{i+1} \rVert}$$

A **breakpoint** (chunk boundary) is placed wherever `d_i` exceeds a threshold. The "percentile" method sets that threshold at, say, the 95th percentile of all `d_i`:

$$\text{break at } i \iff d_i > \operatorname{percentile}_{95}(\{d_1, \dots, d_{n-1}\})$$

Higher percentile → fewer, larger chunks (only the sharpest topic shifts cut). This is why `breakpoint_threshold_amount` behaves the way it does.

**(c) Late chunking pooling.** A long-context embedding model produces one token embedding $\mathbf{t}_j$ per token. A chunk spanning tokens `[a, b]` gets its vector by **mean-pooling** those token embeddings *after* the transformer has already contextualized them over the whole document:

$$\mathbf{c}_{[a,b]} = \frac{1}{b - a + 1} \sum_{j=a}^{b} \mathbf{t}_j$$

Because each $\mathbf{t}_j$ was computed with full-document attention, $\mathbf{c}_{[a,b]}$ carries global context **without** a per-chunk LLM call — the key efficiency win over contextual retrieval.

**(d) Why size affects retrieval recall.** Treat a chunk's embedding as (roughly) the mean of its sentence embeddings. A chunk covering `k` distinct topics has vector $\bar{\mathbf{e}} = \frac{1}{k}\sum \mathbf{e}_{t}$; its similarity to a query about topic 1 is diluted by a factor ~`1/k` relative to a pure single-topic chunk. **This is embedding dilution made precise:** the more topics you cram into a chunk, the weaker its match to any one of them — the mathematical reason over-large chunks retrieve poorly.

### 2.5 Strategy ladder at a glance

```mermaid
flowchart TD
    A[Text to chunk] --> B{Known structure?<br/>MD / code / HTML}
    B -- Yes --> C[Structure-aware split<br/>headers / functions]
    B -- No --> D{Topic coherence<br/>matters more than size?}
    D -- No --> E[Recursive + token-aware<br/>DEFAULT]
    D -- Yes --> F[Semantic chunking<br/>embed sentences, cut at valleys]
    C --> G{Chunks ambiguous<br/>out of context?}
    E --> G
    F --> G
    G -- Yes --> H[Add Contextual Retrieval<br/>LLM context per chunk]
    G -- Yes, long-ctx model --> I[Late chunking<br/>pool token embeddings]
    G -- No --> J[Embed + index]
    H --> J
    I --> J
```

---

## 3. Implementation

Assumed stack (pin these; APIs move): `langchain-text-splitters>=0.3`, `langchain-experimental>=0.3`, `tiktoken>=0.7`, `langchain-openai>=0.2`. See the runnable snippets:
- [[04 Code Snippets/LLM/Recursive and Token-Aware Chunking]]
- [[04 Code Snippets/LLM/Semantic and Contextual Chunking]]
- [[04 Code Snippets/LLM/Semantic Chunking From Scratch]] — the mechanics of §2.4(b), no framework
- [[04 Code Snippets/LLM/Late Chunking with Token Embeddings]] — the pooling of §2.4(c)
- [[04 Code Snippets/LLM/Chunk Size Evaluation Harness]] — pick size/overlap by recall@k, not vibes

### 3.1 The default you should reach for first
Recursive, token-measured, with metadata:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Measure size in OpenAI tokens so chunks never blow the embedding limit.
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="o200k_base",   # gpt-4o / text-embedding-3 family
    chunk_size=500,               # tokens
    chunk_overlap=75,             # ~15% overlap
    separators=["\n\n", "\n", ". ", " ", ""],  # largest -> smallest
)

docs = splitter.create_documents(
    texts=[raw_text],
    metadatas=[{"source": "2023-10k.pdf", "section": "Risk Factors"}],
)
# Each doc.page_content is a chunk; doc.metadata rides along for filtering + citation.
```

### 3.2 Structure-aware for Markdown/code
```python
from langchain_text_splitters import MarkdownHeaderTextSplitter, Language, RecursiveCharacterTextSplitter

# Markdown: split by headers first, keep header path as metadata.
md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")]
)
sections = md_splitter.split_text(markdown_text)  # metadata carries h1/h2/h3

# Code: split on language-aware boundaries (functions/classes) so logic stays intact.
code_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON, chunk_size=800, chunk_overlap=0
)
```

### 3.3 Semantic chunking (when topic boundaries matter more than size)
```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

semantic = SemanticChunker(
    OpenAIEmbeddings(model="text-embedding-3-small"),
    breakpoint_threshold_type="percentile",  # split at similarity valleys
    breakpoint_threshold_amount=95,
)
chunks = semantic.create_documents([raw_text])
```

### 3.4 Contextual retrieval (the high-ROI upgrade)
```python
CONTEXT_PROMPT = """<document>{doc}</document>
Here is a chunk from the document:
<chunk>{chunk}</chunk>
Give a short (1-2 sentence) context situating this chunk within the overall
document, so it can be understood standalone. Answer only with the context."""

def contextualize(llm, full_doc, chunk):
    ctx = llm.invoke(CONTEXT_PROMPT.format(doc=full_doc, chunk=chunk)).content
    return f"{ctx}\n\n{chunk}"   # embed THIS, not the bare chunk

# Cost control: cache the document prefix (prompt caching) so re-sending the
# full doc per chunk is cheap. This is what makes the pattern affordable.
```

### 3.5 The mechanics from scratch (understand, don't just call)
Libraries hide the algorithm. To truly own it, implement the token-aware split and the semantic breakpoint detector yourself — see [[04 Code Snippets/LLM/Semantic Chunking From Scratch]]. The core loop is only a few lines:

```python
import numpy as np

def cosine_distance(a, b):
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def semantic_breakpoints(sentence_embeddings, percentile=95):
    # distances between consecutive sentences  (eq. 2.4b)
    d = [cosine_distance(sentence_embeddings[i], sentence_embeddings[i + 1])
         for i in range(len(sentence_embeddings) - 1)]
    threshold = np.percentile(d, percentile)
    # a boundary sits after sentence i whenever the topic "jumps"
    return [i + 1 for i, dist in enumerate(d) if dist > threshold]
```

That single function *is* semantic chunking; everything else is plumbing (sentence splitting, grouping, embedding calls).

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Chunk size** | Start 300–600 tokens for Q&A over prose. Larger (800–1200) for narrative/legal where context spans paragraphs. Smaller (128–256) for fact lookup / dense reference. |
| **Overlap** | 10–20% of chunk size. More overlap = better boundary recall but more storage, cost, and duplicate hits. Zero overlap only for structure-aware splits (code functions) that are already self-contained. |
| **Which strategy** | Recursive+token = default. Structure-aware whenever the format is known (MD/code/HTML). Semantic only if evals show fixed-size is fragmenting topics. Contextual retrieval when chunks are ambiguous out of context (financial/legal/technical docs with lots of pronouns and references). |
| **Where to spend** | Chunking quality > embedding model choice > reranker, in that ROI order for most corpora. Fix chunking before buying a fancier model. |
| **Measure in tokens, always** | Cost, embedding limits, and LLM context are all token-denominated. |

**Cost/latency lens (the FDE reflex):**
- Fixed/recursive: near-free, one pass.
- Semantic: +1 embedding call per sentence at ingestion (one-time, but adds up over millions of docs).
- Contextual: +1 LLM call per chunk at ingestion — the most expensive; use prompt caching on the document prefix and batch. It's an ingestion-time cost, paid once, amortized over all future queries — usually worth it.

---

## 5. Failure Modes & Gotchas

- **Splitting on characters, not tokens** → chunks overflow the embedding model's max input and get silently truncated; the tail of every chunk is lost.
- **Fragmented tables/code** → a table split across two chunks becomes gibberish in both. Detect and keep atomic units whole (or convert tables to Markdown/text first during ingestion).
- **Over-small chunks** → high precision but the answer is spread across 5 chunks and top-k only returns 3. Symptom: retrieval "finds the right area" but answers are incomplete. Fix: larger chunks or higher k, plus overlap.
- **Over-large chunks** → embedding dilution; the chunk matches everything weakly and nothing strongly. Symptom: irrelevant chunks rank surprisingly high.
- **No metadata** → you can't filter by source/section/date, and you can't cite. Attach metadata at chunk time; it's nearly free and essential for enterprise (access control, citations).
- **Chunking scanned PDFs before OCR/layout parsing** → you chunk garbage. Chunking is downstream of ingestion quality (see the Document Ingestion topic). Garbage in, garbage chunks out.
- **Re-chunking without re-indexing** → stale vectors. Any chunking change requires a full re-embed + re-index; version your chunking config.
- **Assuming one strategy for a mixed corpus** → route by document type (PDF vs Markdown vs code) rather than forcing one splitter on everything.

---

## 6. FDE Angle (how this shows up on an engagement)

- When a client's RAG "isn't accurate," **chunking is the first thing to inspect**, before model or prompt changes. Pull 10 failed queries, look at the retrieved chunks — you'll usually see fragmentation or context loss.
- You will be asked "why is ingestion so expensive?" — contextual retrieval's per-chunk LLM call is often the answer. Be ready to explain the one-time-vs-per-query cost tradeoff and prompt caching.
- Chunk **metadata is your access-control and citation story** in enterprise (which department's doc, which section, what date). Design it up front; retrofitting is a re-index.
- A concrete deliverable: a **chunking config** (size, overlap, strategy per doc type) justified by a retrieval-eval number (recall@k), not by vibes. This is exactly the kind of evidence an FDE brings.

---

## 7. Self-Check (prove you're implementation-ready)

1. Why is chunk size measured in tokens, not characters — give two consequences of getting it wrong.
2. Explain to a non-technical stakeholder why chunking, not the model, is limiting answer quality.
3. Implement a token-aware recursive splitter with 15% overlap and per-chunk source metadata from memory.
4. A chunk reads "This cut costs by 40%." and never gets retrieved for "how did the supply-chain change reduce costs?" — diagnose and give two fixes (one cheap, one contextual).
5. When would you choose semantic or contextual chunking over recursive, and what does each cost at ingestion time?
6. Your client changes chunk_size from 400 to 800. What must happen to the existing vector store before queries are valid again?

---

---

## 9. Interview Q&A

**Q: Why is chunk size measured in tokens, not characters — give two consequences of getting it wrong.**
A: Both the embedding model and the LLM don't actually process characters at all — they process tokens, which don't map to characters in a fixed, predictable way. A chunk of "500 characters" could be anywhere from roughly 100 to 150 tokens depending on the language and content, while a chunk of "500 tokens" is a much more consistent, meaningful unit across different texts.

Here's the first consequence of measuring in characters instead: embedding models have a hard limit on how many tokens they can accept as input. If you size your chunks by character count, a chunk that happens to be dense (code, a non-English language, lots of punctuation) can quietly contain far more tokens than a chunk of plain English the same character length — and if that pushes past the embedding model's token limit, the excess gets silently truncated. You lose the tail of the chunk without any error being raised, and you don't find out until retrieval mysteriously underperforms on exactly that content.

The second consequence is cost and context-budget unpredictability. Since API pricing and LLM context windows are both measured in tokens, sizing your chunks by characters means you genuinely don't know how many tokens you're actually paying for or fitting into your prompt until after the fact — one "500-character" chunk might cost noticeably more, or take up more of your context budget, than another "500-character" chunk, purely because of what language or format it happened to contain.

*One-liner: both embedding models and LLMs process tokens, not characters, so character-based sizing can silently overflow the model's token limit (truncating chunks without warning) and makes cost/context-budget unpredictable — sizing by tokens avoids both problems by measuring in the actual unit the models use.*

**Q: Explain to a non-technical stakeholder why chunking, not the model, is limiting answer quality.**
A: Think of it like this: before the AI can answer a question using your documents, those documents first get cut up into smaller pieces, and only the most relevant pieces get shown to the AI when it's answering. The AI can only ever work with the pieces it was actually shown — it never sees the whole original document at answer time.

If those pieces get cut in the wrong places — say, right in the middle of an important explanation, separating a key fact from the context that explains what it means — the AI might get handed a piece that's confusing or incomplete, even if the original document explained everything perfectly clearly. The AI isn't failing to understand; it's answering based on a fragment that was already missing what it needed, through no fault of its own.

This is why upgrading to a "smarter" or "bigger" AI model often doesn't fix a bad answer — the model was never shown the right information in the first place, because the problem happened earlier, when the document got cut into pieces. It's like asking someone a question but only showing them one sentence of a three-sentence explanation, then being surprised their answer is incomplete — the fix isn't a smarter person, it's showing them the right sentences to begin with. This is exactly why we check how the documents are being cut up first, before assuming a better AI model is needed.

*One-liner: the AI only ever sees the small pieces it was handed, not the full original document — so if those pieces get cut in a way that separates a fact from its context, the AI gives an incomplete answer no matter how good the model is, because the real problem happened earlier, during the cutting step.*

**Q: Implement a token-aware recursive splitter with 15% overlap and per-chunk source metadata, from memory.**
A: Walk through what each piece needs to do before writing it. You need a splitter that: measures size using an actual tokenizer (not character count, per the first question), tries to cut on the largest natural boundary first and only falls back to smaller ones if a piece is still too big, includes some overlap between neighboring chunks so an idea that straddles a cut isn't lost entirely in either piece, and carries metadata (like which file it came from) along with each resulting chunk.

In plain terms, the structure looks like: create a splitter configured with your chosen tokenizer (matching whatever embedding model you'll use), a target chunk size in tokens (say 500), and an overlap in tokens (15% of 500 is 75). Give it a priority list of separators to try, largest first — paragraph breaks, then line breaks, then sentence endings, then plain spaces, falling back further only if a chunk is still too big after trying the bigger separators. Then call it on your raw text, passing along metadata (like the source filename) that should travel with every resulting chunk, so each piece knows where it came from later for filtering and citation.

The core idea to hold onto, regardless of the exact library syntax: the splitter respects structure first (don't cut through a paragraph if you don't have to), only uses an actual tokenizer to measure size (not character count), builds in deliberate overlap between neighbors, and attaches metadata that rides along with every chunk it produces.

*One-liner: configure a recursive splitter with a real tokenizer for size measurement, a 500-token target with 75-token (15%) overlap, a largest-to-smallest separator priority list (paragraphs, lines, sentences, words), and pass metadata (like source filename) through so every resulting chunk carries it.*

**Q: A chunk reads "This cut costs by 40%." and never gets retrieved for "how did the supply-chain change reduce costs?" — diagnose the problem and give two fixes.**
A: Diagnose this by thinking about what a search is actually comparing. The query is specifically about *supply-chain* changes reducing costs — but the chunk itself, on its own, says only "this cut costs by 40%," with no mention of supply chains, no mention of what "this" even refers to. When this chunk gets embedded into a vector, the embedding only has what's actually written in the chunk to work with — it has no way to know that "this" meant "the supply-chain change," because that context lived somewhere else in the original document and got stripped away during chunking. So the chunk's embedding ends up looking like a generic statement about cost reduction, with no particular connection to supply chains at all, and it simply doesn't match a query specifically about supply chains as strongly as it should.

The cheap fix: increase overlap between chunks, or widen the chunk size, so that whatever sentence originally explained what "this" referred to (likely the sentence right before it) gets included in the same chunk instead of being cut away into a separate piece. This is a quick, low-effort fix, though it's somewhat blunt — it doesn't specifically target this exact kind of problem, it just reduces the chances of it happening by keeping more surrounding text together.

The contextual fix: apply contextual retrieval — have an LLM read the whole original document plus this specific chunk, and generate a short sentence of context to prepend before embedding it, turning "This cut costs by 40%" into something like "[From the supply-chain section of the 2023 report, discussing the new supplier contract:] This cut costs by 40%." Now the embedding has the actual topic ("supply-chain," "supplier contract") directly present in the text being embedded, which makes it match the supply-chain-focused query correctly. This costs one extra LLM call per chunk at ingestion time, but it directly and reliably solves the exact "this" problem, rather than just reducing its odds like wider overlap does.

*One-liner: the chunk lost the context that explained what "this" referred to, so its embedding looks like a generic cost-reduction statement with no connection to supply chains — the cheap fix is more overlap/larger chunks to keep that context nearby, the more reliable fix is contextual retrieval, which has an LLM explicitly restate the missing context before the chunk is embedded.*

**Q: When would you choose semantic or contextual chunking over recursive, and what does each cost at ingestion time?**
A: Start from what's actually going wrong with the default (recursive, token-aware) approach, since that's the right baseline for most text and these two alternatives are upgrades for specific, real problems — not something to reach for by default.

Semantic chunking is the right choice when your content doesn't naturally break into chunks of roughly-similar sizes around topic boundaries — for example, prose where some ideas take one sentence and others take three paragraphs. Recursive splitting at a fixed target size doesn't know or care where topics actually shift; it just tries to fit the target size while respecting basic punctuation. Semantic chunking instead embeds each sentence individually and looks for the places where consecutive sentences' meanings genuinely diverge (a "topic shift"), cutting there instead of at a fixed size — producing chunks that are topically coherent, even if that means some chunks end up much longer or shorter than others. The cost: this requires embedding every single sentence in the document just to find the boundaries — a real, if usually modest, extra expense at ingestion time, on top of the embedding you'd do anyway for the final chunks.

Contextual chunking (contextual retrieval) is the right choice specifically when chunks, cut however you cut them, come out *ambiguous on their own* — full of pronouns and references ("this," "it," "the aforementioned approach") that only make sense if you already know what came before. This is common in formal, reference-heavy documents like financial filings, legal contracts, or technical reports. The fix here isn't changing where you cut — it's having an LLM read the chunk plus the whole surrounding document and explicitly spell out the missing context before embedding, as described above. The cost here is more significant: one full LLM call per chunk at ingestion, which for a large corpus is the most expensive of these upgrade options — though it's a one-time ingestion cost, not something you pay again per query, and techniques like prompt caching the shared document text help make it more affordable.

*One-liner: semantic chunking helps when topics don't fit neatly into fixed-size chunks (costing one embedding call per sentence to find topic boundaries); contextual chunking helps when chunks come out ambiguous due to pronouns/references needing document-wide context (costing one LLM call per chunk, the priciest of the two, but paid once at ingestion).*

**Q: Your client changes chunk_size from 400 to 800. What has to happen to the existing vector store before queries are valid again?**
A: The entire corpus has to be re-chunked and re-embedded from scratch — this isn't a setting you can change and have take effect gradually or only for new documents.

Here's why: the vectors already stored in the vector database were created by embedding the *old* 400-token chunks. Those chunks no longer exist as a concept once you change the setting — the new chunking boundaries at 800 tokens will cut the same source documents into entirely different pieces, with different text content in each piece. The old vectors represent text that, strictly speaking, isn't even the "current" chunking scheme anymore, so leaving them in place means your search index is a mix of chunks generated under two different, incompatible chunking rules — some representing the old 400-token boundaries, any newly added documents representing the new 800-token boundaries. Search results would become inconsistent and confusing, mixing both chunk granularities together.

So the correct process is: re-run the entire ingestion pipeline on every source document using the new chunk_size setting, producing a fresh set of chunks, re-embed every one of those new chunks (since the text content itself has changed, even if using the exact same embedding model), and replace the old vectors in the store with these new ones — typically by building the new index alongside the old one and then cutting over, rather than having a mixed, half-old-half-new state exposed to live queries while the rebuild is in progress.

*One-liner: changing chunk_size requires re-running the full ingestion pipeline (re-chunking then re-embedding) on every document in the corpus, since the stored vectors represent the old chunking scheme's text — this is a full rebuild, not an incremental change, and should be cut over cleanly rather than left half-old, half-new during the process.*

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Recursive and Token-Aware Chunking]], [[04 Code Snippets/LLM/Semantic and Contextual Chunking]]
- Distilled: [[03 Permanent Notes/Chunking Is the Unit of Retrieval and Grounding]], [[03 Permanent Notes/Contextual Retrieval Restores Lost Chunk Context]]
- Related (upstream): Document Ingestion & Parsing (to be added)
- Related (downstream): Advanced Retrieval, Retrieval Evaluation (to be added)
