# ADR-006: Application Database Choice

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform requires a database to store note metadata, sync events, workflow history, cost logs, audit records, and cache metadata. The database must support concurrent requests, workflow history tracking, and future multi-user needs while remaining cost-effective for MVP.

## Decision
**Selected Database: Supabase Free PostgreSQL**
- Use Supabase Free PostgreSQL for cloud deployment
- Use SQLite for local prototype only

**Rationale:**
- SQLite is simple for local prototyping and development
- Supabase provides managed PostgreSQL with free tier suitable for MVP
- PostgreSQL is appropriate for cloud hosting, concurrent requests, workflow history, audit logs, and future multi-user needs
- Supabase PostgreSQL with pgvector will also serve as vector store (see ADR-007)

**Data to Store:**
- Note metadata (path, hash, tags, backlinks, frontmatter)
- Sync events and status
- Workflow runs and status
- Cost tracking records
- Audit logs
- Cache metadata
- User sessions and permissions (for multi-user future)

## Alternatives Considered

### SQLite for Production
- **Pros:** Simple, no external dependency, zero-config
- **Cons:** Poor concurrency, no cloud-native features, not suitable for multi-user, rejected for production

### MySQL
- **Pros:** Widely supported, mature
- **Cons:** pgvector support less mature than PostgreSQL, PostgreSQL preferred for vector operations

### MongoDB
- **Pros:** Flexible schema, good for document storage
- **Cons:** Overkill for structured metadata, transaction support weaker than PostgreSQL

### Managed Vector Database (Pinecone, Weaviate)
- **Pros:** Optimized for vector search
- **Cons:** Additional cost, complexity, PostgreSQL with pgvector sufficient for MVP

## Consequences
- Local development uses SQLite for simplicity
- Cloud deployment uses PostgreSQL
- PostgreSQL serves dual purpose: relational data + vector store
- Database schema must support both SQLite and PostgreSQL (for local dev)
- Migration strategy required for SQLite → PostgreSQL transition

## Cost Impact
- PostgreSQL: Managed PostgreSQL provider cost (Azure Database for PostgreSQL or equivalent)
- SQLite: No cost for local development
- Single database reduces infrastructure cost (relational + vector combined)

## Security Impact
- Managed PostgreSQL provides built-in security features
- Connection encryption required
- Database access restricted to backend only
- No direct database access from frontend
- Secrets managed through provider's secret management

## Operational Impact
- PostgreSQL backups are managed by provider
- Connection pooling required for concurrent requests
- Database migrations must be version-controlled
- Monitoring through provider metrics
- Disaster recovery leverages provider backup features

## Follow-Up Actions
- [x] Select Supabase Free PostgreSQL for cloud deployment
- [ ] Create Supabase project
- [ ] Design database schema for metadata, workflows, costs, audit logs
- [ ] Implement database abstraction layer for SQLite/PostgreSQL compatibility
- [ ] Configure connection pooling
- [ ] Set up backup strategy (Supabase automated backups)
- [ ] Implement database migrations
- [ ] Test performance with expected data volume
