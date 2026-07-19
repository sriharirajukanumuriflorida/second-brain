# FDE Week 23b Insurance Discovery Brief and MVP Scope Package

> Week 23b · Customer Discovery & Stakeholder Communication — Applied. Pydantic v2 model tree for the populated insurance-underwriter DiscoveryBrief, 14 scored feature candidates, and three-option scope proposal, rendering a CFO/CUO/CIO markdown package.

```python
from __future__ import annotations
from enum import Enum
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class Influence(str, Enum): low='low'; high='high'
class Interest(str, Enum): low='low'; high='high'

class Stakeholder(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str; role: str; interest: Interest; influence: Influence; concern: str
    @property
    def quadrant(self):
        if self.interest == Interest.high and self.influence == Influence.high: return 'Manage Closely'
        if self.interest == Interest.low and self.influence == Influence.high: return 'Keep Satisfied'
        if self.interest == Interest.high and self.influence == Influence.low: return 'Keep Informed'
        return 'Monitor'

class SuccessCriterion(BaseModel):
    statement: str; metric: str; baseline: str; target: str; timeframe: str; measurement: str

class Constraint(BaseModel):
    category: Literal['technical','regulatory','timeline','budget','integration']
    statement: str

class PremortemRisk(BaseModel):
    risk: str; likelihood: Literal['low','medium','high']; impact: Literal['low','medium','high']; mitigation: str; owner: str

class DiscoveryBrief(BaseModel):
    model_config = ConfigDict(extra='forbid')
    customer: str; vague_ask: str; business_problem: str; jtbd: str; current_pain: str
    stakeholders: list[Stakeholder]; success_criteria: list[SuccessCriterion]
    constraints: list[Constraint]; risks: list[PremortemRisk]; must_not_do: list[str]

class FeatureCandidate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    feature_id: str; name: str; category: str
    business_value: int = Field(ge=1, le=10)
    ai_confidence: float = Field(ge=0, le=1)
    reach: int = Field(gt=0)
    effort_days: int = Field(gt=0)
    must_have: bool = False
    dependencies: list[str] = Field(default_factory=list)
    @property
    def rice_ai(self): return round((self.reach * self.business_value * self.ai_confidence) / self.effort_days, 2)

class ScopeOption(BaseModel):
    name: str; cost_usd: int; timeline_months: float; feature_ids: list[str]; risk_summary: str; recommendation: str

class EngagementPackage(BaseModel):
    brief: DiscoveryBrief; features: list[FeatureCandidate]; options: list[ScopeOption]
    def render_engagement_package_markdown(self) -> str:
        by_id = {f.feature_id: f for f in self.features}
        lines = [f'# Engagement package — {self.brief.customer}', '', '## 1-page discovery brief', f'**Initial ask:** {self.brief.vague_ask}', f'**Business problem:** {self.brief.business_problem}', f'**JTBD:** {self.brief.jtbd}', f'**Current pain:** {self.brief.current_pain}', '', '### SMART success criteria']
        for c in self.brief.success_criteria:
            lines.append(f'- {c.statement} Metric={c.metric}; baseline={c.baseline}; target={c.target}; timeframe={c.timeframe}; measurement={c.measurement}')
        lines += ['', '### Stakeholders']
        for s in self.brief.stakeholders:
            lines.append(f'- {s.name} ({s.role}) — {s.quadrant}; concern: {s.concern}')
        lines += ['', '### Constraints'] + [f'- {c.category}: {c.statement}' for c in self.brief.constraints]
        lines += ['', '### Pre-mortem risks'] + [f'- {r.risk} [{r.likelihood}/{r.impact}] owner={r.owner}; mitigation={r.mitigation}' for r in self.brief.risks]
        lines += ['', '## 3-option MVP scope proposal', '| Feature | Category | BV | Conf | Reach | Effort | RICE-AI | Must | Dependencies |', '|---|---|---:|---:|---:|---:|---:|---|---|']
        for f in sorted(self.features, key=lambda x: (x.must_have, x.rice_ai), reverse=True):
            lines.append(f'| {f.name} | {f.category} | {f.business_value} | {f.ai_confidence:.2f} | {f.reach} | {f.effort_days} | {f.rice_ai:.2f} | {f.must_have} | {", ".join(f.dependencies) or "—"} |')
        for o in self.options:
            feats = [by_id[i].name for i in o.feature_ids]
            lines += [f'\n### {o.name}', f'- Cost: ${o.cost_usd:,}; timeline: {o.timeline_months:g} months', f'- Features: {", ".join(feats)}', f'- Risk summary: {o.risk_summary}', f'- Recommendation: {o.recommendation}']
        lines += ['', '## Eval-criteria sketch', '- Golden set: 200 SME-owned underwriter questions across personal/commercial, jurisdictions, policy versions, memos, and regulatory feeds.', '- Groundedness: >= 92% before launch and monitored weekly.', '- Hallucination: <= 1%; unsupported questions refuse or route to review.', '- Latency/cost: p95 <= 6s; cost/query <= $0.08; baseline run envelope $3,300/month.', '- Audit: 100% of answers log prompt/model/index versions, citations, policy context, decision path, latency, and cost.']
        return '\n'.join(lines)

def seed_package() -> EngagementPackage:
    brief = DiscoveryBrief(
        customer='Mid-sized insurance carrier — commercial underwriting',
        vague_ask='We want an AI assistant for underwriters.',
        business_problem='Complex commercial policies take a median 4 hours to quote because underwriters spend most of the workflow searching policy docs, memos, and regulatory feeds; target is 90 minutes within 6 months of go-live.',
        jtbd='When I am underwriting a complex commercial policy, I want trusted policy, precedent, and regulatory evidence with citations, so I can quote faster while preserving human judgment and auditability.',
        current_pain='Senior SMEs estimated 60% of the day is search across 15 years of underwriting memos, 40k policy documents, Guidewire context, claims precedents, and 3 regulatory feeds.',
        stakeholders=[Stakeholder(name='Chief Underwriting Officer', role='exec sponsor', interest='high', influence='high', concern='4h to 90m business case'), Stakeholder(name='Senior Underwriter — Personal Lines', role='domain SME', interest='high', influence='high', concern='policy version and state filing nuance'), Stakeholder(name='Senior Underwriter — Commercial', role='domain SME', interest='high', influence='high', concern='complex commercial precedent quality'), Stakeholder(name='25 Underwriters in two offices', role='end users', interest='high', influence='low', concern='trust, citations, workflow fit'), Stakeholder(name='CISO', role='security', interest='low', influence='high', concern='private endpoint and incident evidence'), Stakeholder(name='DPO', role='privacy', interest='low', influence='high', concern='no third-party leakage and retention'), Stakeholder(name='Azure Platform Lead', role='platform owner', interest='high', influence='high', concern='landing-zone handoff'), Stakeholder(name='Procurement', role='Azure OpenAI contract', interest='low', influence='high', concern='contract timing')],
        success_criteria=[SuccessCriterion(statement='Reduce median time-to-quote for complex commercial policies.', metric='median workflow time', baseline='4 hours', target='90 minutes', timeframe='within 6 months of go-live', measurement='workflow instrumentation'), SuccessCriterion(statement='Maintain grounded answers.', metric='golden-set groundedness', baseline='no measured baseline', target='>= 92%', timeframe='before launch and weekly after', measurement='SME-owned 200-question eval'), SuccessCriterion(statement='Keep answer latency usable.', metric='p95 /query latency', baseline='manual first search often >10 minutes', target='<= 6 seconds', timeframe='production SLO', measurement='OpenTelemetry/App Insights'), SuccessCriterion(statement='Stay inside operating envelope.', metric='monthly baseline run cost', baseline='new workload', target='<=$3,300/month', timeframe='50-user baseline', measurement='FinOps dashboard'), SuccessCriterion(statement='Preserve auditability.', metric='answers with complete audit record', baseline='manual copy-paste notes inconsistent', target='100%', timeframe='from pilot go-live', measurement='immutable Blob audit sampling')],
        constraints=[Constraint(category='technical', statement='Azure-only processing with private endpoints where supported'), Constraint(category='regulatory', statement='Data residency in approved region and no third-party data leakage'), Constraint(category='integration', statement='Guidewire PolicyCenter context must filter retrieval'), Constraint(category='timeline', statement='6-month delivery timeline'), Constraint(category='budget', statement='$850k initial budget ceiling')],
        risks=[PremortemRisk(risk='Hallucination causes a bad underwriting recommendation', likelihood='medium', impact='high', mitigation='decision support only, citations, groundedness gate, senior-review route', owner='CUO/FDE'), PremortemRisk(risk='Model provider outage halts workflow', likelihood='medium', impact='medium', mitigation='manual fallback, cached approved answers, outage runbook', owner='Platform Lead'), PremortemRisk(risk='Underwriters distrust AI and adoption stalls', likelihood='medium', impact='high', mitigation='SME-owned golden set, in-app citations, working sessions, training', owner='Commercial SME')],
        must_not_do=['Bind coverage autonomously', 'Approve exceptions without human judgment', 'Leak prompts or retrieved text to third parties', 'Bypass Guidewire policy context', 'Ship without SRB approval'])
    features = [
        FeatureCandidate(feature_id='policy_qa', name='Policy history Q&A with citations', category='core', business_value=10, ai_confidence=.86, reach=25, effort_days=28, must_have=True),
        FeatureCandidate(feature_id='memo_search', name='15-year memo precedent search', category='core', business_value=9, ai_confidence=.82, reach=25, effort_days=24, must_have=True),
        FeatureCandidate(feature_id='reg_feeds', name='Regulatory feed cross-reference', category='core', business_value=8, ai_confidence=.78, reach=20, effort_days=22),
        FeatureCandidate(feature_id='guidewire', name='Guidewire policy context filters', category='integration', business_value=9, ai_confidence=.80, reach=25, effort_days=20, must_have=True, dependencies=['Guidewire API access']),
        FeatureCandidate(feature_id='citation_export', name='Cited audit-note export', category='workflow', business_value=9, ai_confidence=.90, reach=25, effort_days=16),
        FeatureCandidate(feature_id='audit', name='Immutable audit log', category='governance', business_value=8, ai_confidence=.88, reach=25, effort_days=18, must_have=True),
        FeatureCandidate(feature_id='feedback', name='SME and underwriter feedback capture', category='eval', business_value=7, ai_confidence=.90, reach=25, effort_days=12),
        FeatureCandidate(feature_id='evals', name='Golden-set eval framework', category='eval', business_value=9, ai_confidence=.92, reach=25, effort_days=18, must_have=True),
        FeatureCandidate(feature_id='review_queue', name='Refusal and senior-review queue', category='risk', business_value=8, ai_confidence=.84, reach=20, effort_days=16, must_have=True),
        FeatureCandidate(feature_id='training_analytics', name='Underwriter training analytics', category='adoption', business_value=5, ai_confidence=.76, reach=12, effort_days=14),
        FeatureCandidate(feature_id='semantic_cache', name='Tenant-scoped semantic cache', category='ops', business_value=6, ai_confidence=.82, reach=25, effort_days=14),
        FeatureCandidate(feature_id='auto_decisions', name='Automatic underwriting decisions', category='autonomy', business_value=10, ai_confidence=.35, reach=8, effort_days=40, dependencies=['validated labels','model-risk approval']),
        FeatureCandidate(feature_id='broker_email', name='Real-time broker email drafting', category='workflow', business_value=5, ai_confidence=.55, reach=10, effort_days=24, dependencies=['legal-approved templates']),
        FeatureCandidate(feature_id='portfolio_analytics', name='Cross-line portfolio analytics', category='analytics', business_value=6, ai_confidence=.50, reach=8, effort_days=30, dependencies=['warehouse access'])]
    options = [ScopeOption(name='Option A — Complete Vision', cost_usd=1_200_000, timeline_months=9, feature_ids=[f.feature_id for f in features if f.feature_id != 'portfolio_analytics'], risk_summary='High delivery and hallucination risk; includes autonomy-adjacent features before evidence exists.', recommendation='Reject for v1; use as vision backlog.'), ScopeOption(name='Option B — Balanced MVP', cost_usd=780_000, timeline_months=6, feature_ids=['policy_qa','memo_search','reg_feeds','guidewire','citation_export','audit','feedback','evals','review_queue','semantic_cache'], risk_summary='Fits timebox; defers automatic decisions, broker email drafting, and portfolio analytics while collecting data for v2.', recommendation='Approve.'), ScopeOption(name='Option C — Foundation Only', cost_usd=480_000, timeline_months=4, feature_ids=['policy_qa','memo_search','citation_export','audit','evals'], risk_summary='Lowest risk, but mostly search plus citations; weaker business-case path to 90-minute quote target.', recommendation='Keep as fallback if budget is cut.')]
    return EngagementPackage(brief=brief, features=features, options=options)

print(seed_package().render_engagement_package_markdown())
```


Related: [[03 Permanent Notes/FDE Week 23b Enterprise AI Engagement Playbook]]
