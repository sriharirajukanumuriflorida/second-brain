# ADR-007: Vector Store and Embedding Strategy

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform requires semantic search capabilities to improve retrieval quality beyond keyword search. The platform must store embeddings for vault notes, support hybrid search (keyword + semantic), and handle embedding model changes without breaking existing functionality.

## Decision
**Selected Vector Store: Supabase PostgreSQL with pgvector**
- Cloud deployment: Supabase PostgreSQL with pgvector (Phase 5+)
- Local prototype: FAISS for local development
- Note: pgvector implementation deferred to Phase 5 (Semantic and Hybrid Retrieval)

**Embedding Model Defaults:**
- Cloud MVP default: text-embedding-3-small or equivalent approved model
- Enterprise/internal default: Approved internal embedding model (e.g., NASH platform)
- Local prototype default: sentence-transformers/all-MiniLM-L6-v2 or equivalent lightweight model

**Embedding Metadata (Per Chunk):**
```text
embedding_provider
embedding_model
embedding_model_version
embedding_dimensions
chunk_hash
file_hash
embedded_at
```

**Re-Embedding Strategy:**
- Mark old embeddings as stale when model changes
- Do not immediately re-embed entire vault
- Re-embed lazily on access or through controlled admin job
- Estimate and display cost before bulk re-embedding
- Log all re-embedding activity

**What to Embed:**
- 03 Permanent Notes
- 05 Projects
- 06 Maps of Content
- 10 FDE Playbooks
- 11 Architecture Decisions
- 12 Solution Patterns
- 13 Governance
- 02 Literature Notes
- 04 Code Snippets

**What NOT to Embed:**
- 08 Attachments
- 99 Archive
- Large datasets
- Binary files
- Images
- Generated cache files

**Chunking Strategy (Phase 5 Baseline):**
- Chunk size: 500 to 1,000 tokens
- Overlap: approximately 100 tokens
- Method: heading-aware Markdown chunking
- Preserve per chunk: note path, heading, frontmatter, tags, backlinks, file hash, chunk hash

## Alternatives Considered

### Managed Vector Database (Pinecone, Weaviate)
- **Pros:** Optimized for vector search, managed service
- **Cons:** Additional cost, complexity, PostgreSQL with pgvector sufficient for MVP scale

### No Embeddings (Keyword Only)
- **Pros:** Simpler, no embedding cost
- **Cons:** Poor retrieval quality for semantic queries, rejected per Phase 5 goals

### Fixed Embedding Model
- **Pros:** Simpler implementation
- **Cons:** Cannot upgrade models, locked into initial choice, rejected for flexibility

## Consequences
- PostgreSQL with pgvector serves dual purpose (relational + vector)
- Embedding model is configurable, not hardcoded
- Re-embedding is lazy and cost-aware
- Embedding metadata enables model version tracking
- Chunking strategy must be defined (not in this ADR)
- Hybrid search ranking must be defined (not in this ADR)

## Cost Impact
- Embedding cost tracked per workflow
- Re-embedding cost estimated before bulk operations
- PostgreSQL with pgvector: no additional cost beyond database
- FAISS: no cost for local prototype
- Budget enforcement required (see ADR-009)

## Security Impact
- Embeddings do not contain raw sensitive content
- Embedding metadata does not expose vault structure publicly
- Vector store access restricted to backend only
- No embedding data exposed through frontend APIs

## Operational Impact
- Embedding pipeline adds complexity to Phase 5
- File hash caching reduces re-embedding overhead
- Lazy re-embedding reduces immediate cost impact
- Model changes require admin coordination
- Retrieval quality metrics must be tracked

## Follow-Up Actions
- [x] Select Supabase PostgreSQL with pgvector for vector store
- [x] Define chunking strategy baseline (500-1000 tokens, 100 overlap, heading-aware)
- [ ] Implement embedding provider abstraction (Phase 5)
- [ ] Implement pgvector integration in Supabase (Phase 5)
- [ ] Implement file hash-based embedding cache (Phase 5)
- [ ] Implement lazy re-embedding logic (Phase 5)
- [ ] Implement embedding cost tracking (Phase 5)
- [ ] Define hybrid search ranking algorithm (Phase 5)
- [ ] Create retrieval evaluation set (Phase 5)
