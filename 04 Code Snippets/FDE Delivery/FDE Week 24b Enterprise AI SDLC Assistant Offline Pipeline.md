# FDE Week 24b Enterprise AI SDLC Assistant Offline Pipeline

> Week 24b · Capstone FDE Portfolio Project — Applied. A deterministic in-process SDLC Assistant: Pydantic models, RAG corpus, hexagonal LLMProvider protocol, fake LLM, citation attachment, schema validation, and clarification behavior for underspecified requirements.

```python
from __future__ import annotations
import json
from typing import Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field, ValidationError

class Citation(BaseModel):
    chunk_id: str
    quote: str

class GeneratedItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str
    description: str
    source_citations: list[Citation] = Field(min_length=1)

class TestCase(GeneratedItem):
    category: Literal['functional','non_functional','automation']
    steps: list[str] = Field(default_factory=list)
    expected_result: str
    metric: str | None = None
    threshold: str | None = None
    measurement_method: str | None = None

class PBI(GeneratedItem):
    kind: Literal['functional','non_functional']
    acceptance_criteria: list[str]
    test_cases: list[TestCase]

class Feature(GeneratedItem):
    pbis: list[PBI]

class Epic(GeneratedItem):
    acceptance_criteria: list[str]
    estimated_effort: Literal['S','M','L']
    dependencies: list[str] = Field(default_factory=list)
    clarification_needed: bool = False
    clarification_questions: list[str] = Field(default_factory=list)
    features: list[Feature] = Field(default_factory=list)

class Chunk(BaseModel):
    chunk_id: str
    text: str
    metadata: dict[str, str]

class RAGCorpus:
    def __init__(self, chunks: list[Chunk]): self.chunks = chunks
    def retrieve(self, query: str, k: int = 5) -> list[Chunk]:
        terms = {t.lower().strip('.,:;()') for t in query.split() if len(t) > 3}
        scored = []
        for c in self.chunks:
            score = sum(1 for t in terms if t in c.text.lower())
            if score: scored.append((score, c))
        return [c for _, c in sorted(scored, key=lambda x: x[0], reverse=True)[:k]] or self.chunks[:k]

class LLMProvider(Protocol):
    def generate_json(self, prompt: str, chunks: list[Chunk]) -> dict: ...

class FakeLLMProvider:
    def generate_json(self, prompt: str, chunks: list[Chunk]) -> dict:
        cite = {'chunk_id': chunks[0].chunk_id, 'quote': chunks[0].text[:100]}
        if 'TBD' in prompt or 'some reports' in prompt.lower():
            return {'title':'Clarification needed before backlog generation','description':'The requirement lacks actor, workflow, or acceptance detail.','acceptance_criteria':['Clarify user, trigger, and success condition.'],'estimated_effort':'S','dependencies':[],'clarification_needed':True,'clarification_questions':['Which user role owns the workflow?','What measurable outcome defines success?'],'source_citations':[cite],'features':[]}
        tc = {'title':'Successful approval path is recorded','description':'Verify happy path and cited audit trail.','category':'functional','steps':['Open requirement workflow','Approve generated PBI','Inspect audit entry'],'expected_result':'Approval is stored with reviewer and citation ids.','source_citations':[cite]}
        nft = {'title':'Generation latency stays under target','description':'Measure p95 latency for a typical epic run.','category':'non_functional','steps':['Run 20 seeded epic generations'],'expected_result':'p95 latency is within target.','metric':'p95_latency_seconds','threshold':'<=120','measurement_method':'OpenTelemetry span aggregation','source_citations':[cite]}
        auto = {'title':'API contract automation test','description':'Validate schema for generated backlog JSON.','category':'automation','steps':['POST /generate','Validate response against schema'],'expected_result':'Response is JSON schema valid.','source_citations':[cite]}
        pbi = {'title':'Reviewer approves generated backlog item','description':'As a Product Owner I can approve a cited generated PBI before export.','kind':'functional','acceptance_criteria':['Given generated JSON, when reviewer approves, then status becomes approved.','Every approved item includes at least one source citation.'],'source_citations':[cite],'test_cases':[tc,nft,auto]}
        feature = {'title':'Human-reviewed backlog generation','description':'Generate and review cited PBIs before export.','source_citations':[cite],'pbis':[pbi]}
        return {'title':'AI-assisted requirements-to-backlog workflow','description':'Convert uploaded requirements into cited, reviewable backlog JSON.','acceptance_criteria':['Generated output is schema-valid.','Every epic, feature, PBI, and test has citations.','Reviewer can approve or request changes before export.'],'estimated_effort':'M','dependencies':['Jira/Azure DevOps field mapping'],'clarification_needed':False,'clarification_questions':[],'source_citations':[cite],'features':[feature]}

def build_corpus() -> RAGCorpus:
    return RAGCorpus([
        Chunk(chunk_id='proj-001', text='All backlog items require source citations and human approval before export to Jira Cloud.', metadata={'source':'team-conventions'}),
        Chunk(chunk_id='proj-002', text='Non-functional tests must name a metric, threshold, and measurement method.', metadata={'source':'qa-standards'}),
        Chunk(chunk_id='proj-003', text='The SDLC assistant must keep cost below 0.20 USD per generated PBI.', metadata={'source':'finops'}),
        Chunk(chunk_id='proj-004', text='Automation candidates should prefer API-level tests over brittle UI selectors.', metadata={'source':'test-strategy'}),
        Chunk(chunk_id='proj-005', text='Every generation request logs prompt version, model version, index version, latency, and cost.', metadata={'source':'ops'}),
    ])

def assemble_prompt(requirement_text: str, chunks: list[Chunk]) -> str:
    context = '\n'.join(f'[{c.chunk_id}] {c.text}' for c in chunks)
    return f'CONTEXT:\n{context}\n\nREQUIREMENT:\n{requirement_text}\nReturn Epic JSON only.'

def sdlc_pipeline(requirement_text: str, corpus: RAGCorpus | None = None, provider: LLMProvider | None = None) -> Epic:
    corpus = corpus or build_corpus(); provider = provider or FakeLLMProvider()
    chunks = corpus.retrieve(requirement_text)
    raw = provider.generate_json(assemble_prompt(requirement_text, chunks), chunks)
    return Epic.model_validate(raw)

clean = 'Build a workflow so a Product Owner uploads a requirements document and reviews generated PBIs with citations before Jira export.'
underspecified = 'TBD: add AI for some reports later.'
for label, text in [('clean', clean), ('underspecified', underspecified)]:
    result = sdlc_pipeline(text)
    print('\n###', label)
    print(result.model_dump_json(indent=2))
try:
    Epic.model_validate({'title':'bad','description':'missing citations','acceptance_criteria':[],'estimated_effort':'XL'})
except ValidationError as exc:
    print('\nSCHEMA VALIDATION CAUGHT:', exc.errors()[0]['msg'])
```


Related: [[03 Permanent Notes/FDE Week 24b Enterprise AI SDLC Assistant Capstone Blueprint]]
