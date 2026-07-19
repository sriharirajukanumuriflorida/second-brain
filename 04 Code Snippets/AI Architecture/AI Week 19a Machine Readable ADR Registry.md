# AI Week 19a Machine Readable ADR Registry

> Week 19a · AI Solution Architecture — Reference Patterns. A Pydantic v2 ADR model plus an in-memory registry that renders accepted AI architecture decisions as Markdown.

```python
from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class ADRStatus(str, Enum):
    proposed = 'proposed'
    accepted = 'accepted'
    superseded = 'superseded'
    deprecated = 'deprecated'

class ADR(BaseModel):
    id: str = Field(pattern=r'^ADR-\d{4}$')
    title: str
    context: str
    decision: str
    consequences: List[str]
    alternatives: List[str]
    status: ADRStatus = ADRStatus.proposed

    def markdown(self) -> str:
        lines = [f'# {self.id} {self.title}', '', f'Status: **{self.status.value}**', '', '## Context', self.context, '', '## Decision', self.decision, '', '## Consequences']
        lines += [f'- {c}' for c in self.consequences]
        lines += ['', '## Alternatives'] + [f'- {a}' for a in self.alternatives]
        return '\n'.join(lines)

class ADRRegistry:
    def __init__(self):
        self.records: dict[str, ADR] = {}
    def add(self, adr: ADR):
        if adr.id in self.records:
            raise ValueError(f'duplicate ADR id {adr.id}')
        self.records[adr.id] = adr
    def accepted(self):
        return [a for a in self.records.values() if a.status == ADRStatus.accepted]
    def render_all(self) -> str:
        return '\n\n---\n\n'.join(a.markdown() for a in self.records.values())

registry = ADRRegistry()
registry.add(ADR(
    id='ADR-0001', title='Choose pgvector over Pinecone for MVP',
    context='The MVP has fewer than five million chunks, strict tenant metadata joins, and a platform team that already operates Postgres.',
    decision='Use Postgres with pgvector for the first production release.',
    consequences=['One backup and transaction model for document metadata plus vectors.', 'Revisit Pinecone or Qdrant if latency, recall, or scale targets are missed.'],
    alternatives=['Pinecone managed service', 'Qdrant dedicated vector cluster'], status=ADRStatus.accepted))
registry.add(ADR(
    id='ADR-0002', title='Use provider fallback for GPT-4 outages',
    context='The assistant is customer-facing and must degrade during regional Azure OpenAI incidents.',
    decision='Route through an LLMProvider port with a tested fallback provider and a search-only degraded mode.',
    consequences=['Improves availability.', 'Requires prompt compatibility tests and response-quality evals across providers.'],
    alternatives=['Single provider direct SDK calls', 'Disable the assistant during outage'], status=ADRStatus.accepted))
registry.add(ADR(
    id='ADR-0003', title='Adopt hexagonal ports for LLM providers',
    context='Procurement and residency constraints may require Azure OpenAI, Bedrock, Vertex, or self-hosted adapters by tenant.',
    decision='Keep provider SDKs behind LLMProvider and EmbeddingProvider ports.',
    consequences=['Swappable providers.', 'More interface design up front.'],
    alternatives=['Import provider SDKs in application services', 'Use one orchestration framework everywhere'], status=ADRStatus.accepted))

print(len(registry.accepted()), 'accepted ADRs')
print(registry.accepted()[0].markdown().splitlines()[0])
```


Related: [[03 Permanent Notes/AI Week 19a ADR Template for AI Systems]]
