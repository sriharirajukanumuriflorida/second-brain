# Recursive and Token-Aware Chunking

## Purpose
- Production-ready default chunker for RAG: recursive splitting on natural boundaries, sized in real tokens, with per-chunk metadata for filtering and citation. Includes Markdown- and code-aware variants.

## Language
- Python

## Snippet
```python
# pip install "langchain-text-splitters>=0.3" "tiktoken>=0.7"
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    Language,
)

# --- 1. Default: recursive + token-measured + metadata ------------------------
def make_default_splitter(chunk_size=500, overlap_ratio=0.15):
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="o200k_base",            # gpt-4o / text-embedding-3 family
        chunk_size=chunk_size,                  # measured in TOKENS
        chunk_overlap=int(chunk_size * overlap_ratio),
        separators=["\n\n", "\n", ". ", " ", ""],  # largest -> smallest boundary
    )

def chunk_document(raw_text, source, section=None):
    splitter = make_default_splitter()
    return splitter.create_documents(
        texts=[raw_text],
        metadatas=[{"source": source, "section": section}],
    )

# --- 2. Structure-aware: Markdown by headers (keeps header path as metadata) ---
def chunk_markdown(md_text):
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")]
    )
    sections = header_splitter.split_text(md_text)          # metadata: h1/h2/h3
    # Second pass to cap size of any long section:
    size_splitter = make_default_splitter(chunk_size=600)
    return size_splitter.split_documents(sections)

# --- 3. Structure-aware: code by language (functions/classes stay intact) ------
def chunk_code(code_text, language=Language.PYTHON):
    code_splitter = RecursiveCharacterTextSplitter.from_language(
        language=language, chunk_size=800, chunk_overlap=0
    )
    return code_splitter.create_documents([code_text])

if __name__ == "__main__":
    text = open("report.txt").read()
    chunks = chunk_document(text, source="2023-10k.pdf", section="Risk Factors")
    print(f"{len(chunks)} chunks; first chunk metadata: {chunks[0].metadata}")
    print(chunks[0].page_content[:300])
```

## Notes
- `from_tiktoken_encoder(...)` makes `chunk_size` mean **tokens**, so chunks never exceed the embedding model's input limit and cost is predictable. Character-based sizing silently truncates.
- `separators` are tried in order — paragraphs first, characters last — so cuts land on the largest natural boundary that satisfies the size cap.
- Always attach `metadata` at chunk time: it powers metadata filtering, access control, and source citations later. It's effectively free here.
- Code/Markdown variants keep atomic units (functions, sections) whole; use zero overlap when units are already self-contained.
- Any change to `chunk_size`/`overlap`/strategy requires re-embedding and re-indexing the corpus. Version your chunking config.

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
- Related: [[04 Code Snippets/LLM/Semantic and Contextual Chunking]]
- Related project:
