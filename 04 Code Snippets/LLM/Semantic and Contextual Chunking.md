# Semantic and Contextual Chunking

## Purpose
- Two higher-quality chunking upgrades: (1) **semantic chunking** cuts at topic shifts instead of fixed sizes; (2) **contextual retrieval** (Anthropic pattern) prepends LLM-generated context to each chunk before embedding, to restore meaning lost by chunking.

## Language
- Python

## Snippet
```python
# pip install "langchain-experimental>=0.3" "langchain-openai>=0.2"
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# --- 1. Semantic chunking: split at similarity valleys between sentences -------
def semantic_chunks(raw_text):
    chunker = SemanticChunker(
        OpenAIEmbeddings(model="text-embedding-3-small"),
        breakpoint_threshold_type="percentile",  # or "standard_deviation","gradient"
        breakpoint_threshold_amount=95,           # higher -> fewer, larger chunks
    )
    return chunker.create_documents([raw_text])

# --- 2. Contextual retrieval: LLM writes standalone context per chunk ----------
CONTEXT_PROMPT = """<document>
{doc}
</document>

Here is a chunk we want to situate within the document:
<chunk>
{chunk}
</chunk>

Write a short (1-2 sentence) context that situates this chunk within the overall
document so it can be understood on its own. Respond with ONLY the context."""

def contextualize_chunks(full_doc, chunks, model="gpt-4o-mini"):
    llm = ChatOpenAI(model=model, temperature=0)
    enriched = []
    for ch in chunks:
        text = ch.page_content if hasattr(ch, "page_content") else ch
        ctx = llm.invoke(
            CONTEXT_PROMPT.format(doc=full_doc, chunk=text)
        ).content.strip()
        # Embed THIS enriched text (context + original chunk), not the bare chunk:
        enriched.append(f"{ctx}\n\n{text}")
    return enriched

if __name__ == "__main__":
    doc = open("report.txt").read()
    base = semantic_chunks(doc)                     # or reuse recursive chunks
    enriched = contextualize_chunks(doc, base)
    print(enriched[0][:400])
```

## Notes
- **Semantic chunking** embeds every sentence, so ingestion is more expensive than recursive splitting. Use it only when evals show fixed-size chunking is fragmenting topics — not by default.
- `breakpoint_threshold_amount` tunes granularity: higher percentile = fewer, larger chunks; lower = more, smaller chunks.
- **Contextual retrieval** costs one LLM call per chunk at ingestion. Control cost by: using a small/cheap model (`gpt-4o-mini`), enabling **prompt caching** on the repeated `{doc}` prefix, and batching. It's a one-time ingestion cost amortized over all future queries.
- Anthropic's published results pair contextual chunks with **BM25 hybrid search** for the biggest recall gains — embed the enriched text AND index it for keyword search.
- Store the *original* chunk text for display/citation, but embed the *enriched* text for retrieval.

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
- Related: [[04 Code Snippets/LLM/Recursive and Token-Aware Chunking]]
- Distilled: [[03 Permanent Notes/Contextual Retrieval Restores Lost Chunk Context]]
- Related project:
