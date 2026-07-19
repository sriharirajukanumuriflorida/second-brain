# FDE Week 23a Discovery Brief Generator

> Week 23a · Customer Discovery & Stakeholder Communication — Reference Patterns. A Pydantic v2 discovery-brief model tree that validates SMART success criteria and JTBD shape, then renders a full markdown brief for a healthcare medical-coding assistant scenario.

```python
import re
from enum import Enum
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class Influence(str, Enum):
    low = 'low'
    high = 'high'
class Interest(str, Enum):
    low = 'low'
    high = 'high'

class Stakeholder(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    role: str
    interest: Interest
    influence: Influence
    concern: str
    @property
    def quadrant(self):
        if self.interest == Interest.high and self.influence == Influence.high: return 'Manage Closely'
        if self.interest == Interest.low and self.influence == Influence.high: return 'Keep Satisfied'
        if self.interest == Interest.high and self.influence == Influence.low: return 'Keep Informed'
        return 'Monitor'

class SuccessCriterion(BaseModel):
    model_config = ConfigDict(extra='forbid')
    statement: str
    metric: str
    target: str
    timeframe: str
    @model_validator(mode='after')
    def smart_enough(self):
        target_has_number = bool(re.search(r'\d', self.target))
        timeframe_has_time = bool(re.search(r'\b(day|week|month|quarter|q[1-4]|year|pilot|by)\b', self.timeframe.lower()))
        if not (self.metric.strip() and target_has_number and timeframe_has_time):
            raise ValueError('success criteria must include metric, numeric target, and timeframe')
        return self

class Constraints(BaseModel):
    model_config = ConfigDict(extra='forbid')
    technical: list[str]
    regulatory: list[str]
    budget: list[str]
    timeline: list[str]

class Risk(BaseModel):
    model_config = ConfigDict(extra='forbid')
    risk: str
    likelihood: Literal['low','medium','high']
    impact: Literal['low','medium','high']
    mitigation: str
    owner: str

class DiscoveryBrief(BaseModel):
    model_config = ConfigDict(extra='forbid')
    customer: str
    vague_ask: str
    business_problem: str
    user: str
    current_workflow: str
    data_locations: list[str]
    success_criteria: list[SuccessCriterion]
    constraints: Constraints
    risks: list[Risk]
    must_not_break: list[str]
    jtbd: str
    stakeholders: list[Stakeholder]
    five_whys: list[str]

    @field_validator('jtbd')
    @classmethod
    def jtbd_shape(cls, v):
        if not re.match(r'^When .+, I want to .+, so I can .+\.?$', v.strip()):
            raise ValueError('JTBD must match: When..., I want to..., so I can...')
        return v

    @model_validator(mode='after')
    def eight_questions_present(self):
        required = [self.business_problem, self.user, self.current_workflow, ','.join(self.data_locations), ','.join(self.must_not_break)]
        if any(not x.strip() for x in required) or not self.success_criteria or not self.constraints or not self.risks:
            raise ValueError('brief must answer all eight discovery questions')
        return self

    def render_brief_markdown(self):
        lines = [f'# Discovery Brief: {self.customer}', '', f'**Vague ask:** {self.vague_ask}', '', '## Eight discovery answers']
        rows = [
            ('Business problem', self.business_problem), ('User', self.user), ('Current workflow', self.current_workflow),
            ('Data', '; '.join(self.data_locations)), ('Success', '; '.join(c.statement for c in self.success_criteria)),
            ('Constraints', 'Tech: ' + '; '.join(self.constraints.technical) + ' | Regulatory: ' + '; '.join(self.constraints.regulatory) + ' | Budget: ' + '; '.join(self.constraints.budget) + ' | Timeline: ' + '; '.join(self.constraints.timeline)),
            ('Risks', '; '.join(r.risk for r in self.risks)), ('Must not break', '; '.join(self.must_not_break)),
        ]
        lines += [f'- **{k}:** {v}' for k, v in rows]
        lines += ['', '## JTBD', self.jtbd, '', '## Stakeholder map']
        lines += [f'- {s.name} ({s.role}) — {s.quadrant}; concern: {s.concern}' for s in self.stakeholders]
        lines += ['', '## Pre-mortem risks']
        lines += [f'- {r.risk} [{r.likelihood}/{r.impact}] owner={r.owner}; mitigation={r.mitigation}' for r in self.risks]
        lines += ['', '## Five Whys trail'] + [f'{i+1}. {why}' for i, why in enumerate(self.five_whys)]
        return '\n'.join(lines)

brief = DiscoveryBrief(
    customer='Northstar Health Provider Network',
    vague_ask='We want an AI assistant for medical coding.',
    business_problem='Complex ambulatory encounters take too long to code and coding-related denials are increasing, delaying revenue and creating rework.',
    user='Certified medical coders working specialty clinic encounters after physician documentation is complete.',
    current_workflow='Coders read encounter notes, search payer guidance and coding manuals, choose ICD-10 and CPT codes, add modifiers, and route ambiguous cases to a lead coder.',
    data_locations=['EHR encounter notes in Epic export tables', 'payer policy PDFs in SharePoint', 'historical coded claims in the billing warehouse', 'denial reason codes in revenue-cycle reports'],
    success_criteria=[
        SuccessCriterion(statement='Reduce average coding research time for complex encounters.', metric='average minutes per complex encounter', target='from 18 minutes to 11 minutes', timeframe='within 10-week pilot'),
        SuccessCriterion(statement='Reduce coding-related denial rate for pilot specialties.', metric='coding-related denial rate', target='from 7.5% to 6.0%', timeframe='by end of quarter'),
        SuccessCriterion(statement='Maintain grounded recommendations.', metric='golden-set groundedness', target='>= 92%', timeframe='before pilot go-live'),
    ],
    constraints=Constraints(
        technical=['EHR writeback is out of scope for v1', 'assistant must cite source guideline ids', 'nightly batch extract is available; real-time CDC is not'],
        regulatory=['HIPAA PHI boundary', 'audit trail required for suggestions and user decisions'],
        budget=['pilot budget caps implementation at 55 engineering days', 'cost per assistant call must stay below $0.08 average'],
        timeline=['scope sign-off in 2 weeks', 'pilot demo in 8 weeks']
    ),
    risks=[
        Risk(risk='Groundedness regression on rare specialty cases', likelihood='medium', impact='high', mitigation='SME-labeled golden set and human review for low confidence', owner='coding SME lead'),
        Risk(risk='PHI leakage into traces or eval exports', likelihood='low', impact='high', mitigation='redacted tracing and approved eval data handling', owner='security architect'),
        Risk(risk='Payer policy PDFs are stale or conflicting', likelihood='medium', impact='medium', mitigation='document freshness owner and citation timestamp in UI', owner='revenue-cycle director'),
    ],
    must_not_break=['existing coder sign-off workflow', 'auditability of final submitted codes', 'PHI access controls', 'monthly revenue-cycle reporting'],
    jtbd='When I am coding a complex specialty encounter, I want to see grounded code candidates with evidence, so I can finish accurately with less research and fewer denials.',
    stakeholders=[
        Stakeholder(name='VP Revenue Cycle', role='executive sponsor', interest='high', influence='high', concern='denials and cash acceleration'),
        Stakeholder(name='Coding Operations Manager', role='domain SME', interest='high', influence='high', concern='coder adoption and policy accuracy'),
        Stakeholder(name='Senior Medical Coder', role='end user', interest='high', influence='low', concern='trust, speed, and override workflow'),
        Stakeholder(name='Security Architect', role='data/security', interest='low', influence='high', concern='HIPAA, logging, access boundaries'),
        Stakeholder(name='EHR Integration Lead', role='engineering owner', interest='low', influence='high', concern='batch export capacity and no EHR writeback in v1'),
    ],
    five_whys=[
        'Why AI assistant? Coders spend too much time researching ambiguous encounters.',
        'Why is research slow? Guidance is split across payer PDFs, EHR notes, and tribal SME knowledge.',
        'Why does it matter financially? Slow and inconsistent coding increases denial rework and days in A/R.',
        'Why not automate final coding? Compliance requires human coder accountability for submitted codes.',
        'Why pilot now? Specialty clinics have high denial concentration and available historical claims for evaluation.'
    ]
)
print(brief.render_brief_markdown())
```


Related: [[03 Permanent Notes/FDE Week 23a Discovery Question Bank]]
