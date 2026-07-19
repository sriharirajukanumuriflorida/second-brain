# FDE Week 24a Capstone Deliverable Scorecard

> Week 24a · Capstone FDE Portfolio Project — Reference Patterns. A Pydantic v2 scorecard for FDE capstone deliverables that grades evidence quality, reports top gaps, and compares early-stage versus portfolio-ready snapshots.

```python
from enum import Enum
from collections import defaultdict
from pydantic import BaseModel, ConfigDict, Field

class Status(str, Enum):
    missing = 'missing'
    stub = 'stub'
    draft = 'draft'
    polished = 'polished'

class Signal(str, Enum):
    has_eval_numbers = 'has_eval_numbers'
    has_diagram_from_source = 'has_diagram_from_source'
    has_cost_analysis = 'has_cost_analysis'
    has_risk_register = 'has_risk_register'
    has_deployment_guide = 'has_deployment_guide'
    reproducible_from_repo = 'reproducible_from_repo'
    demo_video_present = 'demo_video_present'
    readme_bluf_in_first_paragraph = 'readme_bluf_in_first_paragraph'
    ci_passing = 'ci_passing'
    prompt_contract_versioned = 'prompt_contract_versioned'
    api_docs_generated = 'api_docs_generated'

EXPECTED = {
    'repo': {Signal.ci_passing, Signal.reproducible_from_repo},
    'readme': {Signal.readme_bluf_in_first_paragraph, Signal.has_eval_numbers, Signal.has_cost_analysis},
    'architecture': {Signal.has_diagram_from_source},
    'api_docs': {Signal.api_docs_generated, Signal.reproducible_from_repo},
    'prompt_contract': {Signal.prompt_contract_versioned},
    'evaluation': {Signal.has_eval_numbers, Signal.reproducible_from_repo},
    'demo': {Signal.demo_video_present, Signal.reproducible_from_repo, Signal.has_eval_numbers},
    'deployment': {Signal.has_deployment_guide, Signal.reproducible_from_repo},
    'risk': {Signal.has_risk_register},
    'roadmap': {Signal.has_cost_analysis},
}
STATUS_POINTS = {Status.missing: 0, Status.stub: 25, Status.draft: 60, Status.polished: 100}

class CapstoneDeliverable(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str
    category: str
    status: Status
    evidence_ref: str
    quality_signals: list[Signal] = Field(default_factory=list)

    def score(self) -> int:
        expected = EXPECTED.get(self.category, set())
        present = set(self.quality_signals)
        coverage = len(expected & present) / len(expected) if expected else 1.0
        return int(round(STATUS_POINTS[self.status] * 0.7 + coverage * 30))

    def gaps(self) -> list[str]:
        gaps = []
        if self.status != Status.polished:
            gaps.append(f'{self.title}: status is {self.status.value}')
        missing = EXPECTED.get(self.category, set()) - set(self.quality_signals)
        gaps += [f'{self.title}: missing {m.value}' for m in sorted(missing, key=lambda s: s.value)]
        return gaps

class CapstoneScorecard(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    deliverables: list[CapstoneDeliverable]

    def evaluate(self) -> dict:
        by_cat = defaultdict(list)
        for d in self.deliverables:
            by_cat[d.category].append(d.score())
        per_category = {cat: round(sum(vals) / len(vals), 1) for cat, vals in sorted(by_cat.items())}
        overall = round(sum(d.score() for d in self.deliverables) / len(self.deliverables), 1)
        all_gaps = [gap for d in self.deliverables for gap in d.gaps()]
        verdict = 'portfolio-ready' if overall >= 90 and not all_gaps else 'demo-ready' if overall >= 75 else 'working-prototype' if overall >= 50 else 'early'
        return {'overall': overall, 'per_category': per_category, 'top_5_gaps': all_gaps[:5], 'verdict': verdict}

    def print_report(self):
        result = self.evaluate()
        print(f"# {self.name} readiness: {result['overall']} -> {result['verdict']}")
        for cat, score in result['per_category'].items():
            print(f'- {cat:16s} {score:5.1f}')
        print('top gaps:', result['top_5_gaps'] or 'none')

early = CapstoneScorecard(name='Underwriting Policy Assistant', deliverables=[
    CapstoneDeliverable(title='GitHub repo structure', category='repo', status='polished', evidence_ref='/', quality_signals=[Signal.ci_passing, Signal.reproducible_from_repo]),
    CapstoneDeliverable(title='README with BLUF', category='readme', status='draft', evidence_ref='README.md', quality_signals=[Signal.readme_bluf_in_first_paragraph]),
    CapstoneDeliverable(title='C4 architecture diagram', category='architecture', status='polished', evidence_ref='docs/architecture.md', quality_signals=[Signal.has_diagram_from_source]),
    CapstoneDeliverable(title='OpenAPI documentation', category='api_docs', status='draft', evidence_ref='src/api/openapi.json', quality_signals=[Signal.api_docs_generated]),
    CapstoneDeliverable(title='Prompt contract registry', category='prompt_contract', status='stub', evidence_ref='docs/prompt-contract.md', quality_signals=[]),
    CapstoneDeliverable(title='Golden set', category='evaluation', status='draft', evidence_ref='evals/golden.jsonl', quality_signals=[Signal.reproducible_from_repo]),
    CapstoneDeliverable(title='Evaluation report chart', category='evaluation', status='missing', evidence_ref='docs/evaluation.md', quality_signals=[]),
    CapstoneDeliverable(title='Demo video', category='demo', status='stub', evidence_ref='docs/demo.md', quality_signals=[]),
    CapstoneDeliverable(title='Docker compose deployment', category='deployment', status='draft', evidence_ref='docker-compose.yml', quality_signals=[Signal.has_deployment_guide]),
    CapstoneDeliverable(title='Cloud deploy guide', category='deployment', status='missing', evidence_ref='infra/', quality_signals=[]),
    CapstoneDeliverable(title='Risk register', category='risk', status='draft', evidence_ref='docs/risk-register.md', quality_signals=[Signal.has_risk_register]),
    CapstoneDeliverable(title='Cost model', category='readme', status='missing', evidence_ref='docs/cost.md', quality_signals=[]),
    CapstoneDeliverable(title='Roadmap', category='roadmap', status='polished', evidence_ref='docs/roadmap.md', quality_signals=[Signal.has_cost_analysis]),
    CapstoneDeliverable(title='CI eval regression job', category='repo', status='draft', evidence_ref='.github/workflows/eval.yml', quality_signals=[Signal.ci_passing]),
    CapstoneDeliverable(title='Screenshots and GIF', category='demo', status='polished', evidence_ref='docs/assets/', quality_signals=[Signal.demo_video_present]),
])
early.print_report()

polished_rows = []
for d in early.deliverables:
    expected = sorted(EXPECTED.get(d.category, set()), key=lambda s: s.value)
    polished_rows.append(d.model_copy(update={'status': Status.polished, 'quality_signals': expected}))
CapstoneScorecard(name='Underwriting Policy Assistant polished', deliverables=polished_rows).print_report()
```


Related: [[03 Permanent Notes/FDE Week 24a Capstone Deliverable Checklist]]
