# Software Engineering Concepts

> Phase 1 (Core Foundation) of the 24-Week FDE roadmap — the engineering base that everything AI/LLM sits on.
> Goal: senior-level, implementation-ready refresh of software engineering, system design, DSA, and backend/API skills for Forward Deployed Engineering work.
> Legend: ✅ built · 🟡 partial · ⬜ planned

## How to use this track
1. Skim the **Slide deck** (`07 Resources Library/Software Engineering/Slides/`) for the overview.
2. Read the topic's **Literature Note** (`02 Literature Notes/Software Engineering/`) for the deep material.
3. Work the **Notebook** (`07 Resources Library/Software Engineering/Notebooks/`) hands-on — it runs offline.
4. Keep the linked **Code Snippet(s)** (`04 Code Snippets/Software Engineering/`) as reusable reference.
5. Distill durable insights into **Permanent Notes** (`03`).
6. Do the note's **Self-Check** before marking a topic done.

## Resource Library
- Slides: `07 Resources Library/Software Engineering/Slides/`
- Notebooks: `07 Resources Library/Software Engineering/Notebooks/`

---

## Phase 1 — Core Foundation

### Week 01 — Software Engineering Refresh
- ✅ [[02 Literature Notes/Software Engineering/Software Engineering Refresh]]
  - Clean code · SOLID · design patterns · modular architecture · error handling · logging · testing strategy · git workflow · CI/CD basics
  - Snippets: [[04 Code Snippets/Software Engineering/SE Week 01 SOLID Strategy Boundary Example]] · [[04 Code Snippets/Software Engineering/SE Week 01 Structured Logging and Error Boundary]]
  - Permanent: [[03 Permanent Notes/SE Week 01 SOLID Principles Quick Reference]] · [[03 Permanent Notes/SE Week 01 Testing Pyramid and Delivery Strategy]]

### Week 02 — System Design Fundamentals
- ✅ [[02 Literature Notes/Software Engineering/System Design Fundamentals]]
  - Client-server · layered · hexagonal · microservices · event-driven · queues · caching · rate limiting · scalability · reliability · fault tolerance
  - Snippets: [[04 Code Snippets/Software Engineering/SE Week 02 Token Bucket Rate Limiter]] · [[04 Code Snippets/Software Engineering/SE Week 02 In-Memory LRU Cache]]
  - Permanent: [[03 Permanent Notes/SE Week 02 Scalability Reliability and Fault Tolerance]] · [[03 Permanent Notes/SE Week 02 Caching Strategies and Invalidation]]

### Week 03 — Data Structures, Algorithms & Complexity
- ✅ [[02 Literature Notes/Software Engineering/Data Structures, Algorithms & Complexity]]
  - Arrays · hash maps · trees · graphs · queues · stacks · search · sorting · Big-O · memory vs speed tradeoffs
  - Snippets: [[04 Code Snippets/Software Engineering/SE Week 03 Graph BFS DFS Traversal]] · [[04 Code Snippets/Software Engineering/SE Week 03 Binary Search Sort and Hash Index]]
  - Permanent: [[03 Permanent Notes/SE Week 03 Big-O Complexity Cheat Sheet]] · [[03 Permanent Notes/SE Week 03 Choosing the Right Data Structure]]

### Week 04 — APIs, Integration & Backend Engineering
- ✅ [[02 Literature Notes/Software Engineering/APIs, Integration & Backend Engineering]]
  - REST · FastAPI · request/response contracts · auth · authz · file upload · background jobs · async · versioning · DB access · SQL basics
  - Snippets: [[04 Code Snippets/Software Engineering/SE Week 04 Dataclass API Contract Handler]] · [[04 Code Snippets/Software Engineering/SE Week 04 Async Job Queue and SQLite Demo]]
  - Permanent: [[03 Permanent Notes/SE Week 04 REST API Design Checklist]] · [[03 Permanent Notes/SE Week 04 AuthN vs AuthZ and Token Patterns]]

---

## Phase 1 Depth Pass — Production Reality
> Complements the Phase 1 refreshers with what real production teams actually implement. Notebooks use real FastAPI, Pydantic v2, SQLAlchemy, PyJWT, and OpenTelemetry (all in-process via TestClient / in-memory SQLite / in-memory span exporter — no network).

### Week 01+ — Production Delivery Engineering
- ✅ [[02 Literature Notes/Software Engineering/Production Delivery Engineering]]
  - GitHub Actions · pre-commit · trunk-based dev · conventional commits · SemVer · coverage/mutation gates · SAST/SCA · feature flags · contract testing · blue/green · canary · monorepo vs polyrepo
  - Snippets: [[04 Code Snippets/Software Engineering/SE Week 01+ GitHub Actions Delivery Workflow Validator]] · [[04 Code Snippets/Software Engineering/SE Week 01+ Deterministic Feature Flag Rollout Evaluator]]
  - Permanent: [[03 Permanent Notes/SE Week 01+ CI CD Pipeline Design Checklist]] · [[03 Permanent Notes/SE Week 01+ Deployment Strategies Decision Guide]]

### Week 02+ — Distributed Systems Reality
- ✅ [[02 Literature Notes/Software Engineering/Distributed Systems Reality]]
  - CAP/PACELC · consistency levels · idempotency keys · outbox · saga · CQRS · circuit breakers · bulkheads · backpressure · cache stampede · consistent hashing · capacity math · leader election
  - Snippets: [[04 Code Snippets/Software Engineering/SE Week 02+ Idempotency Key Middleware Simulation]] · [[04 Code Snippets/Software Engineering/SE Week 02+ Token Bucket Circuit Breaker]]
  - Permanent: [[03 Permanent Notes/SE Week 02+ Distributed Systems Failure Playbook]] · [[03 Permanent Notes/SE Week 02+ Capacity Estimation Cheat Sheet]]

### Week 03+ — Applied Data Structures for Backend & AI
- ✅ [[02 Literature Notes/Software Engineering/Applied Data Structures for Backend and AI]]
  - Heap/top-K · trie · union-find · Bloom · Count-Min · HyperLogLog · LRU/LFU/ARC/TinyLFU · consistent hashing · skip list · B-tree vs LSM · Merkle · sliding window
  - Snippets: [[04 Code Snippets/Software Engineering/SE Week 03+ Bloom Filter False Positive Demo]] · [[04 Code Snippets/Software Engineering/SE Week 03+ Heap Top K Vector Retriever]]
  - Permanent: [[03 Permanent Notes/SE Week 03+ Probabilistic Data Structures Cheat Sheet]] · [[03 Permanent Notes/SE Week 03+ B-Tree vs LSM-Tree Decision Guide]]

### Week 04+ — Production API and Backend Patterns
- ✅ [[02 Literature Notes/Software Engineering/Production API and Backend Patterns]]
  - OpenAPI · Pydantic v2 · OAuth2+PKCE · OIDC · JWT vs opaque · refresh rotation · RBAC/ABAC · idempotency-key · cursor pagination · ETags · rate limiting · retry+jitter · OpenTelemetry · N+1 · isolation levels · optimistic locking
  - Snippets: [[04 Code Snippets/Software Engineering/SE Week 04+ FastAPI JWT Rate Limit Idempotency Demo]] · [[04 Code Snippets/Software Engineering/SE Week 04+ OpenTelemetry Retry With Jitter Demo]]
  - Permanent: [[03 Permanent Notes/SE Week 04+ Production API Design Checklist]] · [[03 Permanent Notes/SE Week 04+ OAuth2 OIDC and Token Patterns]]

---

## Roadmap position
- Phase 1 (this track) is the foundation for the AI/LLM layer in [[06 Maps of Content/LLM Engineering Concepts]].
- Next FDE gaps: Week 19 AI Solution Architecture, Week 20 Cloud Architecture & Deployment, Week 23 Customer Discovery & Stakeholder Comms, Week 24 Capstone, and the cross-cutting Architecture Track.
