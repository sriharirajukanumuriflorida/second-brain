# FDE Week 24b Capstone Evaluation Harness Regression Report

> Week 24b · Capstone FDE Portfolio Project — Applied. Deterministic Pydantic eval harness for 8 seeded golden items, aggregate scoring, and markdown regression reports with HOLD/PROMOTE verdicts across three prompt versions.

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


Related: [[03 Permanent Notes/FDE Week 24b Capstone Interview and Handoff Scripts]]
