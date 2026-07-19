# Capstone FDE Portfolio Project — Applied

> Topic package — Week 24b · Roadmap Week 24b — Capstone FDE Portfolio Project · Applied.
> Depth goal: ship the final portfolio-grade FDE artifact: discover, scope, architect, prompt-contract, evaluate, secure, deploy, cost, demo, and explain an Enterprise AI SDLC Assistant on a fresh problem so a hiring manager or enterprise customer can trust the pattern was learned, not memorized from the insurance scenario.

## Source
- Track: FDE Delivery (self-directed, FDE roadmap)
- Slide deck: `07 Resources Library/FDE Delivery/Slides/Lesson_04_Capstone_FDE_Portfolio_Project_—_Applied.pptx`
- Hands-on notebook: `07 Resources Library/FDE Delivery/Notebooks/04_Capstone_FDE_Portfolio_Project_—_Applied.ipynb` (runs offline)
- Reference reading: C4 Model; FastAPI and Pydantic v2 docs; OpenAPI 3.1; SQLAlchemy and pgvector; Azure OpenAI enterprise deployment guidance; OpenTelemetry; OWASP Top 10 for LLM Applications; NIST AI RMF; GitHub Actions; Azure Container Apps and ACR; Bicep; RAG evaluation, LLM-as-judge rubric, groundedness, citation coverage, FinOps, BLUF, Pyramid Principle, Jobs-To-Be-Done, RICE-for-AI, MoSCoW, SMART goals
- Builds on: [[02 Literature Notes/FDE Delivery/Capstone FDE Portfolio Project — Reference Patterns]]
- Date: 2026-07-18

---

## 1. Mental Model

**Week 24b is the closing artifact for the entire FDE roadmap.** The project is not another insurance-underwriter assistant; it proves transfer. The capstone scenario is an **Enterprise AI SDLC Assistant** for a mid-size product engineering organization: upload a requirements document, ground generation in project knowledge, and return schema-valid JSON for epics, features, functional PBIs, non-functional PBIs, functional tests, non-functional tests, and automation tests with citations, review workflow, eval tracking, API/UI, and cost/latency logs.

The portfolio claim is deliberately measurable: **cut requirement-to-backlog time from 3-5 days to 4 hours for a typical epic, at about $0.15 all-in per generated PBI, with Jira/Azure DevOps-ready JSON and eval-tracked groundedness at or above 90% on a 250-item golden set.** This note instantiates all ten capstone deliverables: repo shape, README, architecture, API, prompt contracts, evaluation report, demo, deployment guide, risk/go-live checklist, and roadmap.

> Key intuition: **the final capstone is an evidence loop** — business claim → discovered scope → hexagonal architecture → prompt contracts → validated JSON → human review → eval regression → secure deployment → ops metrics → interview narrative.

```mermaid
C4Container
    title Enterprise AI SDLC Assistant — container-level capstone architecture
    Person(po, "Product Owner", "Uploads requirements and reviews generated backlog")
    Person(eng, "Engineering/QA Lead", "Reviews PBIs, tests, quality metrics, and export package")
    System_Boundary(sdlc, "Enterprise AI SDLC Assistant") {
      Container(ui, "Human Review UI", "Streamlit or Next.js", "Upload docs, inspect citations, edit JSON, approve exports")
      Container(api, "FastAPI Backend", "FastAPI + Pydantic v2", "OpenAPI, auth, orchestration, JSON validation, review queue")
      Container(rag, "RAG Pipeline", "Python service", "ingest → chunk → embed → retrieve → rerank → prompt → LLM → validate → cite")
      Container(guard, "Guardrails", "policy modules", "input/output classifier, PII redact, injection wrapper, schema validator, tool authz")
      ContainerDb(pg, "Project Knowledge Index", "Postgres + pgvector", "chunks, embeddings, metadata, golden eval results")
      Container(reg, "Prompt Registry", "Blob/Git config", "prompt ids, schemas, owners, changelogs, rollout pointers")
      Container(eval, "Eval Harness", "offline/CI runner", "250-item golden set, LLM-judge rubrics, regression verdicts")
      Container(obs, "Cost + Latency Logger", "OpenTelemetry", "tokens, cost/PBI, p95 latency, trace ids, release tuple")
      Container(queue, "Human Review Queue", "SQL tables", "draft epic/feature/PBI/test packages awaiting approval")
      Container(cfg, "Config Store", "environment config", "provider route, model, index alias, thresholds")
    }
    System_Ext(llm, "Azure OpenAI", "gpt-4o generation + embeddings; swappable via LLMProvider port")
    System_Ext(jira, "Jira Cloud / Azure DevOps", "future export target after approval")
    System_Ext(actions, "GitHub Actions", "test → scan → eval → deploy → smoke eval → traffic gates")
    po --> ui
    eng --> ui
    ui --> api
    api --> guard
    api --> rag
    rag --> pg
    rag --> reg
    rag --> llm
    api --> queue
    api --> obs
    eval --> api
    eval --> pg
    api --> cfg
    actions --> eval
    actions --> api
    queue -. approved JSON .-> jira
```

---

## 2. How It Actually Works

### 24b.1 Business claim, discovery brief, and MVP scope
The capstone opens with BLUF: **Cut requirement-to-backlog time from 3-5 days to 4 hours for a typical epic, at about $0.15 all-in per generated PBI, with structured JSON that can plug into Jira/Azure DevOps and eval-tracked groundedness ≥ 90% on the 250-item golden set.** The buyer is a mid-size product organization where Product Owners, Engineering Managers, and QA Leads manually convert 20-60 page requirement documents into epics, features, PBIs, and tests. The JTBD: *when a new requirements document arrives, I want a cited draft backlog and test suite that matches our project conventions so I can spend time reviewing product decisions rather than transcribing and decomposing work.*

The DiscoveryBrief is explicit. Users: Product/Engineering leads, QA leads, platform engineering, and compliance reviewers. Stakeholders: Product Owner owns workflow adoption; Engineering Manager owns implementation feasibility; QA Lead owns functional/non-functional/automation test quality; Platform Engineering owns deployment and observability; Compliance owns data handling and audit evidence. SMART success criteria: reduce median requirement-to-reviewed-backlog cycle from 3-5 days to 4 hours within two release trains; maintain groundedness ≥ 90% on 250 golden items before launch; produce 100% JSON schema-valid outputs for supported work item types; keep all-in metered cost ≤ $0.20/PBI at pilot scale and target $0.15/PBI; keep p95 end-to-end generation latency ≤ 120 seconds for a 40-page requirements doc; capture citation/source references on 100% of generated epics, features, PBIs, and tests. Constraints: Jira Cloud integration target, Azure DevOps-compatible schema, no source code shipped to third-party providers, OAuth/OIDC, RBAC, PII redaction on uploaded docs, and cost cap $0.20/PBI.

MVP scope uses Week 23a's RICE-for-AI plus MoSCoW. **Must for v1:** upload requirement doc; ingest project knowledge; generate epic; generate features; generate functional PBIs; generate non-functional PBIs; generate functional, non-functional, and automation tests; RAG grounding with citations; structured JSON output with Pydantic validation; human review UI; source references; cost+latency logs. **Should:** evaluation dashboard, API access, prompt registry, OpenAPI docs, export package formatted for Jira/Azure DevOps import. **Could:** multi-tenant theming, semantic cache, batch uploads, reviewer assignment. **Won't for v1:** automatic Jira submission and autonomous backlog acceptance. Automatic Jira submission is cut to preserve human-in-the-loop and avoid polluting production boards; autonomous acceptance is cut because eval evidence should support review acceleration, not replacement of product judgment.

### 24b.2 Architecture, prompt contract, and hexagonal shape
The reference architecture becomes concrete: **FastAPI + Pydantic v2 + SQLAlchemy + Postgres/pgvector + Azure OpenAI + OpenTelemetry + Streamlit or Next.js + Bicep + GitHub Actions.** The API owns OpenAPI, auth, idempotency for generation jobs, schema validation, and audit records. The RAG pipeline ingests requirement docs and project knowledge, chunks by headings/user journeys/API sections, embeds, retrieves with metadata filters, reranks for citation density, assembles a prompt from registry data, calls the LLM through a hexagonal `LLMProvider` port, validates JSON, and attaches citations. Azure OpenAI is the first adapter; Bedrock can be added in roughly one day because model calls are isolated behind `LLMProvider.generate_json(prompt, schema, trace_context)` and tests use a deterministic fake provider.

Prompt contracts are first-class data. `generate_epic.v1` purpose: convert one requirements document plus retrieved project knowledge into exactly one Epic object. Model route: `gpt-4o`. Input schema: `requirement_text`, `project_context_chunks[]`, `product_area`, `constraints[]`, `definition_of_ready`, and `citation_policy`. Output schema: `Epic{title, description, acceptance_criteria[], estimated_effort, dependencies[], source_citations[]}` plus `clarification_needed: bool` and `clarification_questions[]`. Safety rules: cite every claim, refuse or ask clarification when requirements are underspecified, do not invent project names, do not create implementation details not grounded in context, and return only JSON. Changelog: v1 initial contract, schema version `2026-07-18`.

Second contract: `generate_functional_test.v2`. Purpose: generate functional test cases for a PBI using cited requirements and project testing conventions. Output: tests with `name`, `preconditions`, `steps[]`, `expected_results[]`, `category`, `source_citations[]`, and `automation_candidate`. Changelog v2: **improved coverage of negative-path scenarios; groundedness +2pp, cost -8%** by reducing context to relevant acceptance criteria and adding two negative-path few-shot examples. The capstone rule: prompts live in `/prompts/` or a registry table with id, version, owner, schema, safety rules, eval artifact, and rollback pointer; they are not strings buried in route handlers.

### 24b.3 Evaluation harness — golden set, scoring, regression tracking
The credibility layer is a 250-item golden set: **50 requirements documents × 5 domains × 10 sizes**, each paired with human-reviewed expected epic, feature list, PBI list, and test-case list. Domains include SaaS billing, identity/access, ecommerce checkout, analytics dashboards, and developer platform APIs. Sizes range from one-page change requests to 60-page PRDs. Human product managers and QA leads review expected outputs; the person writing prompts cannot be the sole author of the golden labels.

Each eval run executes the full pipeline end-to-end. Structural scoring checks JSON schema validity, enum correctness, required fields, and whether every generated claim has a citation to retrieved context. Groundedness uses an LLM-as-judge rubric: for every epic, PBI, and test claim, verify support in cited chunks; score 0-100 with launch target ≥ 90. Coverage scores the generated PBI list against expected PBIs using semantic similarity, computing precision and recall rather than exact string match. Test-case quality uses a rubric: functional tests must include positive, negative, and edge paths; non-functional tests must name a metric, threshold, and measurement method; automation tests must include stable selectors or API-level automation strategy.

Regression tracking uses the Week 20b/22b vocabulary. Every commit touching prompts, retrieval, chunking, reranking, schemas, or provider configuration runs `make eval`. Results get version, baseline delta, token/cost delta, latency delta, sampled failures, and verdict: **PROMOTE**, **HOLD**, or **ROLLBACK**. Concrete table for `generate_functional_test`: v1 baseline groundedness 78%, cost $0.150/PBI, latency 92s → HOLD as initial baseline below target; v2 groundedness 84%, cost +15% ($0.173/PBI), latency 101s → HOLD for cost review despite quality lift; v3 groundedness 86%, cost back to $0.150/PBI, latency 89s → PROMOTE for the functional-test prompt lane while noting overall capstone launch still requires full-system groundedness ≥ 90. This visible imperfection makes the capstone credible: it shows measured progress, not cherry-picked screenshots.

### 24b.4 Deployment, security, cost, and go-live checklist
Local deployment is boring on purpose: `make setup && make test && make eval && make run` starts docker compose with Postgres + pgvector, FastAPI, Streamlit, fake provider fixtures, and seeded project knowledge. Cloud deployment is `make deploy`: GitHub Actions builds and scans the image, pushes to ACR, deploys Azure Container Apps with Bicep, runs smoke eval, and gates traffic 10% → 50% → 100% with automatic rollback on eval regression, schema-validity breach, p95 latency breach, or cost/PBI breach. The repo structure is `/src/api`, `/src/rag`, `/src/providers`, `/src/guardrails`, `/src/evals`, `/prompts`, `/evals/golden`, `/infra/bicep`, `/docs`, `/tests`, and `/Makefile`.

Security posture: OAuth2/OIDC + JWT with audience/scope validation; RBAC roles Reader, Editor, Admin; PII redaction at ingestion for uploaded requirement docs that contain customer identifiers; prompt-injection defense with input classifier, instruction hierarchy wrapper, output validator, and tool-call authorization; audit log of request, response, prompt version, model version, index version, citations, user hash, cost, and latency to Blob. No source code is shipped to third-party providers; only requirement text and retrieved project knowledge cross the Azure OpenAI boundary under the approved enterprise data posture.

Cost model separates raw model tokens from all-in portfolio unit economics. Baseline: 10 users × 5 epic generations/day = 50 epic runs/day; 15 PBIs/epic = 750 PBIs/day. With 2,000 input + 500 output tokens per generated PBI plus shared retrieval/context overhead, raw GPT-4o generation is roughly $10/day (about $0.013/PBI). The capstone reports conservative all-in metered unit cost near **$0.15/PBI** after eval sampling, retries, embeddings amortization, logging, review infrastructure, and non-prod overhead; the hard cap is $0.20/PBI. At 22 business days, monthly all-in pilot cost is about 750 × 22 × $0.15 = **$2,475**, under a $3,300 pilot envelope. PTU is not economical at pilot scale; revisit when concurrency, p95 stability, or token volume approaches a Standard-vs-PTU trigger.

The 25-item go-live checklist result is **CONDITIONAL_GO**: 20 green; 3 amber — evaluation dashboard needs v1.1 trend slices, docker compose is documented but cloud deploy needs one more dry-run, cost dashboard needs per-tenant attribution; 2 red — missing DPA template for enterprise customers and missing rollback drill evidence. Next steps: legal owner drafts DPA template, platform owner performs rollback drill, FDE reruns checklist before 100% traffic.

### 24b.5 Portfolio narrative, README, and interview answer
The README starts with the claim and evidence, not the stack:

```markdown
# Enterprise AI SDLC Assistant

**BLUF:** Converts requirement docs into cited, schema-valid epics, features, PBIs, and test cases, cutting requirement-to-reviewed-backlog time from 3-5 days to 4 hours at ~$0.15/PBI and 92% groundedness on a 250-item golden set.

![Groundedness across prompt versions](docs/assets/groundedness-chart-placeholder.png)

This is an FDE capstone for product engineering teams. It ingests requirements and project knowledge, uses RAG and prompt contracts to generate structured backlog JSON, and keeps humans in review before Jira/Azure DevOps import.

[3-minute demo video](docs/demo-video-placeholder.md)

| Metric | Result |
|---|---:|
| Groundedness | 92% |
| Hallucination rate | 1.4% |
| Avg cost/PBI | $0.15 |
| Avg latency / epic run | 90s |

Run it in 15 minutes: `make setup`, `make test`, `make eval`, `make run`.
```

Demo arc: setup — a Product Owner spends three days turning a 40-page requirements doc into epic/PBIs/tests; confrontation — the assistant ingests it in about 90 seconds and returns structured, cited, schema-validated JSON; resolution — review workflow reduces elapsed time to 4 hours, groundedness is about 92%, cost is $0.15/PBI, and schema validity is 100%. The 90-second interview pitch: *I built an Enterprise AI SDLC Assistant that converts PRDs into Jira-ready backlog and tests. The headline result is 3-5 days down to 4 hours with 92% groundedness on 250 golden cases. The hardest problem was not calling an LLM; it was preventing plausible but ungrounded PBIs. I solved that with strict Pydantic schemas, citations on every generated item, human review, and eval regression gates. The key tradeoff was keeping Jira submission human-approved in v1 to preserve trust.*

Three hard problems: overgenerated fluff PBIs solved with schemas, few-shot examples, and eval gates; citations broke at chunk boundaries solved with overlapping chunks and citation-aware reranker; cost blew up on large docs solved with hierarchical summarization and targeted retrieval. Tradeoffs: Streamlit over Next.js for MVP speed; bespoke RAG boundaries over LangChain for depth signal and inspectability; Azure OpenAI over direct OpenAI for enterprise procurement/data story. Documented failure modes include hallucinated tests, schema drift, and flattering eval sets. Roadmap: v2 Jira submission after human approval; v3 multi-language requirements; v4 adaptive re-eval when the corpus updates.

---

## 3. Implementation

Assumed stack: stdlib plus Pydantic v2; snippets run offline with deterministic fake providers and no network. These are liftable into the capstone repo as `src/rag/pipeline_demo.py` and `src/evals/regression_report.py`. Snippets:
- [[04 Code Snippets/FDE Delivery/FDE Week 24b Enterprise AI SDLC Assistant Offline Pipeline]]
- [[04 Code Snippets/FDE Delivery/FDE Week 24b Capstone Evaluation Harness Regression Report]]

### FDE Week 24b Enterprise AI SDLC Assistant Offline Pipeline
A deterministic in-process SDLC Assistant: Pydantic models, RAG corpus, hexagonal LLMProvider protocol, fake LLM, citation attachment, schema validation, and clarification behavior for underspecified requirements.
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

### FDE Week 24b Capstone Evaluation Harness Regression Report
Deterministic Pydantic eval harness for 8 seeded golden items, aggregate scoring, and markdown regression reports with HOLD/PROMOTE verdicts across three prompt versions.
```python
from __future__ import annotations
from statistics import mean
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class GoldenItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str
    requirement_text: str
    expected_epic_title: str
    expected_pbi_count_range: tuple[int, int]
    expected_test_case_categories: list[Literal['functional','non_functional','automation']]
    source_context_chunk_ids: list[str]

class EvalResult(BaseModel):
    item_id: str
    schema_valid: bool
    citation_coverage_pct: float
    groundedness_score: float
    pbi_precision: float
    pbi_recall: float
    test_coverage_score: float
    cost_usd: float
    latency_ms: int

class VersionSummary(BaseModel):
    version: str
    groundedness: float
    citation_coverage: float
    pbi_f1: float
    test_coverage: float
    cost_per_pbi: float
    latency_ms: int
    verdict: Literal['PROMOTE','HOLD','ROLLBACK']
    notes: str

class RegressionReport(BaseModel):
    prompt_id: str
    golden_size: int
    versions: list[VersionSummary]
    def render_regression_markdown(self) -> str:
        vals = [v.groundedness for v in self.versions]
        blocks = '▁▂▃▄▅▆▇█'
        lo, hi = min(vals), max(vals)
        spark = ''.join(blocks[int((v-lo)/(hi-lo or 1)*(len(blocks)-1))] for v in vals)
        lines = [f'# Regression Report — {self.prompt_id}', f'Golden set sample: {self.golden_size} items (capstone full set: 250)', f'Groundedness trend: {spark}', '', '| Version | Grounded | Citation | PBI F1 | Test quality | Cost/PBI | Latency | Verdict | Notes |', '|---|---:|---:|---:|---:|---:|---:|---|---|']
        for v in self.versions:
            lines.append(f'| {v.version} | {v.groundedness:.1f}% | {v.citation_coverage:.1f}% | {v.pbi_f1:.2f} | {v.test_coverage:.1f}% | ${v.cost_per_pbi:.3f} | {v.latency_ms} ms | **{v.verdict}** | {v.notes} |')
        promote = [v.version for v in self.versions if v.verdict == 'PROMOTE'][-1]
        lines += ['', f'Recommendation: **{promote}** is the current promote candidate; keep HOLD versions as documented evidence, not deleted history.']
        return '\n'.join(lines)

def seed_golden() -> list[GoldenItem]:
    domains = ['billing proration','oidc roles','checkout refund','analytics export','developer webhooks','quota alerts','audit log','access review']
    return [GoldenItem(id=f'g{i+1:02d}', requirement_text=f'Generate backlog and tests for {name} workflow with citations.', expected_epic_title=f'{name.title()} workflow', expected_pbi_count_range=(2,5), expected_test_case_categories=['functional','non_functional','automation'], source_context_chunk_ids=[f'proj-{(i%5)+1:03d}']) for i, name in enumerate(domains)]

def evaluate_version(golden: list[GoldenItem], version: str) -> list[EvalResult]:
    config = {'v1': (78, .150, 92000, .74, .70), 'v2': (84, .173, 101000, .80, .76), 'v3': (86, .150, 89000, .84, .82)}[version]
    grounded_base, cost, latency, precision, recall = config
    results = []
    for idx, item in enumerate(golden):
        wobble = (idx % 3) - 1
        citation = 88 + idx % 5 + (4 if version == 'v3' else 0)
        test_quality = grounded_base - 4 + (idx % 4) + (3 if version == 'v3' else 0)
        results.append(EvalResult(item_id=item.id, schema_valid=True, citation_coverage_pct=min(100, citation), groundedness_score=grounded_base + wobble, pbi_precision=precision, pbi_recall=recall, test_coverage_score=test_quality, cost_usd=cost*3, latency_ms=latency + idx*37))
    return results

def summarize(version: str, results: list[EvalResult], baseline_cost: float = .150) -> VersionSummary:
    p = mean(r.pbi_precision for r in results); rec = mean(r.pbi_recall for r in results)
    f1 = 2*p*rec/(p+rec)
    grounded = mean(r.groundedness_score for r in results)
    cost_per_pbi = mean(r.cost_usd for r in results) / 3
    if cost_per_pbi > baseline_cost * 1.10:
        verdict, notes = 'HOLD', 'quality improved, but cost exceeds +10% review gate'
    elif grounded < 80:
        verdict, notes = 'HOLD', 'baseline below launch target; keep as comparison point'
    elif grounded >= 85 and cost_per_pbi <= baseline_cost * 1.02:
        verdict, notes = 'PROMOTE', 'best quality at baseline cost; promote prompt lane'
    else:
        verdict, notes = 'HOLD', 'needs more quality or cost evidence'
    return VersionSummary(version=version, groundedness=grounded, citation_coverage=mean(r.citation_coverage_pct for r in results), pbi_f1=f1, test_coverage=mean(r.test_coverage_score for r in results), cost_per_pbi=cost_per_pbi, latency_ms=int(mean(r.latency_ms for r in results)), verdict=verdict, notes=notes)

golden = seed_golden()
versions = [summarize(v, evaluate_version(golden, v)) for v in ['v1','v2','v3']]
report = RegressionReport(prompt_id='generate_functional_test', golden_size=len(golden), versions=versions)
print(report.render_regression_markdown())
print('\nSample per-item result:', evaluate_version(golden, 'v3')[0].model_dump())
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Human approval before Jira write** | Keep automatic Jira submission out of v1; export/import JSON is acceptable until eval, authz, rollback, and customer board hygiene are proven. |
| **Pydantic schemas as product boundary** | Use schemas for epics, features, PBIs, and tests so downstream Jira/Azure DevOps mapping fails fast rather than corrupting backlog data. |
| **Bespoke hexagonal core over framework-first** | Use explicit ports for LLMProvider, VectorStore, PromptRegistry, and EvalRunner; this creates stronger FDE interview signal and easier fake-provider tests. |
| **Azure OpenAI first, portable provider later** | Choose Azure for enterprise data/procurement story while isolating provider SDK calls so Bedrock can be added without rewriting RAG orchestration. |
| **Eval gate before polish** | Ship a smaller workflow with real golden-set regression evidence rather than a broad backlog platform with only demo examples. |
| **All-in unit economics** | Report raw model cost and all-in cost/PBI separately so finance sees both token math and operational overhead. |

---

## 5. Failure Modes & Gotchas

- The first prompt overgenerates plausible but fluffy PBIs that are not implied by the requirement document; reviewers lose trust until schemas, few-shots, citations, and eval gates constrain it.
- Citations break at chunk boundaries, so generated tests cite only half of a requirement; overlapping chunks and citation-aware reranking become necessary.
- Large requirement documents blow up context cost because every section is stuffed into the prompt; hierarchical summarization and targeted retrieval are required.
- The assistant hallucinates non-functional tests with vague thresholds such as 'fast' or 'secure'; the schema and rubric must require metric, threshold, and measurement method.
- Schema drift breaks downstream Jira/Azure DevOps mapping when a field is renamed without contract tests; OpenAPI and Pydantic compatibility tests must gate releases.
- The eval harness flatters the system because the golden set was written by the same person who tuned prompts; human PM/QA review and adversarial items are required.

---

## 6. FDE Angle

- This capstone is the career artifact: it lets a hiring manager see discovery, architecture, implementation, eval, security, ops, cost, and narrative in one inspectable repo.
- It proves transfer: the FDE repeats the enterprise AI pattern on SDLC backlog generation rather than reusing the insurance-underwriter scenario.
- The strongest signal is not a shiny UI; it is the loop from BLUF business claim to golden-set regression table to go-live checklist and handoff scripts.
- The final answer to 'why hire you as an FDE?' is this artifact: it shows you can turn ambiguous enterprise workflow pain into a measured, governed, deployable AI system.

---

## 7. Self-Check

1. Can you state the capstone business claim, target user, baseline, target, cost/PBI, and groundedness threshold in one sentence?
2. Which v1 features are Must, Should, Could, and Won't, and why was automatic Jira submission cut?
3. What fields belong in `generate_epic.v1` and `generate_functional_test.v2` prompt contracts, and where are they registered?
4. How does the 250-item golden set score structure, groundedness, PBI coverage, and test quality?
5. What makes the cloud deployment and go-live checklist enterprise credible rather than demo-only?
6. How would you answer 'tell me about your capstone' in 90 seconds with one number, one hard problem, and one tradeoff?

## 8. Links
- Domain MOC: [[06 Maps of Content/FDE Delivery Concepts]]
- Code: [[04 Code Snippets/FDE Delivery/FDE Week 24b Enterprise AI SDLC Assistant Offline Pipeline]], [[04 Code Snippets/FDE Delivery/FDE Week 24b Capstone Evaluation Harness Regression Report]]
- Distilled: [[03 Permanent Notes/FDE Week 24b Enterprise AI SDLC Assistant Capstone Blueprint]], [[03 Permanent Notes/FDE Week 24b Capstone Interview and Handoff Scripts]]
- Upstream: [[02 Literature Notes/FDE Delivery/Capstone FDE Portfolio Project — Reference Patterns]] · Prior applied roots: [[02 Literature Notes/AI Architecture/AI Solution Architecture — Applied]] · [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Applied]] · [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Applied]] · [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Applied]] · [[02 Literature Notes/FDE Delivery/Customer Discovery & Stakeholder Communication — Applied]] · Downstream: [[06 Maps of Content/FDE Delivery Concepts]]
