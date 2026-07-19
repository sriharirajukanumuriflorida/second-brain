# FDE Week 23a MVP Scope and Tradeoff Evaluator

> Week 23a · Customer Discovery & Stakeholder Communication — Reference Patterns. A deterministic scoping-workshop tool that scores AI features with confidence-weighted RICE, partitions MoSCoW scope under a timebox, and prints three executive options.

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

REACH = {'low': 1, 'medium': 2, 'high': 3, 'enterprise': 5}

class FeatureCandidate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    description: str
    business_value_score: int = Field(ge=1, le=10)
    ai_confidence: float = Field(ge=0, le=1)
    effort_days: int = Field(gt=0)
    reach: Literal['low','medium','high','enterprise']
    must_have_reason_or_null: str | None = None
    dependencies: list[str] = Field(default_factory=list)

    @property
    def score(self):
        return (self.business_value_score * self.ai_confidence * REACH[self.reach]) / self.effort_days


def score_and_partition(candidates, timebox_days):
    ordered = sorted(candidates, key=lambda c: (c.must_have_reason_or_null is not None, c.score), reverse=True)
    must = [c for c in ordered if c.must_have_reason_or_null]
    remaining = [c for c in ordered if not c.must_have_reason_or_null]

    used = sum(c.effort_days for c in must)
    should, could, wont = [], [], []
    for c in remaining:
        if used + c.effort_days <= timebox_days and c.ai_confidence >= 0.65:
            should.append(c); used += c.effort_days
        elif c.ai_confidence >= 0.55 and c.effort_days <= 8:
            could.append(c)
        else:
            wont.append(c)

    aggressive = must + should + could[:3]
    balanced = must + should
    safe = must + [c for c in should if c.ai_confidence >= 0.80 and not c.dependencies]

    def option(label, features, rationale):
        days = sum(f.effort_days for f in features)
        risky = [f.name for f in features if f.ai_confidence < 0.70]
        return {
            'label': label,
            'days': days,
            'delta_days': days - timebox_days,
            'features': [f.name for f in features],
            'rationale': rationale,
            'tradeoff': f"{days} days ({days - timebox_days:+d} vs timebox); AI-risky inclusions: {risky or 'none'}"
        }

    return {
        'MoSCoW': {'Must': must, 'Should': should, 'Could': could, "Won't": wont},
        'options': [
            option('Option A — aggressive scope', aggressive, 'Maximizes visible capability but accepts over-budget delivery and thinner AI-confidence hedges.'),
            option('Option B — recommended balanced scope', balanced, 'Fits the timebox while delivering the core metric: faster grounded code research with auditability.'),
            option('Option C — safe scope', safe, 'Under-runs budget and protects trust by deferring data- or model-risky features until eval evidence improves.'),
        ]
    }

candidates = [
    FeatureCandidate(name='Encounter note summarization', description='Summarize relevant diagnoses, procedures, and ambiguity from EHR notes.', business_value_score=8, ai_confidence=0.82, effort_days=7, reach='high', must_have_reason_or_null='Core coder workflow starts from note comprehension.'),
    FeatureCandidate(name='ICD-10 and CPT candidate suggestions', description='Return candidate codes with explanations and confidence.', business_value_score=10, ai_confidence=0.74, effort_days=12, reach='high', must_have_reason_or_null='The MVP must recommend code candidates.'),
    FeatureCandidate(name='Guideline citation retrieval', description='Cite payer policy and coding guideline evidence for every suggestion.', business_value_score=9, ai_confidence=0.86, effort_days=9, reach='high', must_have_reason_or_null='Grounding and trust require citations.'),
    FeatureCandidate(name='Coder feedback capture', description='Capture accepted, rejected, and edited suggestions for eval growth.', business_value_score=7, ai_confidence=0.90, effort_days=5, reach='high'),
    FeatureCandidate(name='Golden-set eval harness', description='Score groundedness and top-code recall on SME-labeled cases.', business_value_score=9, ai_confidence=0.88, effort_days=6, reach='medium', must_have_reason_or_null='AI acceptance criteria need eval evidence.'),
    FeatureCandidate(name='Audit log and trace export', description='Record prompt, model, sources, user decision, and cost per request.', business_value_score=8, ai_confidence=0.84, effort_days=6, reach='enterprise'),
    FeatureCandidate(name='Nightly batch claims ingestion', description='Load prior coded claims and denial outcomes nightly.', business_value_score=7, ai_confidence=0.78, effort_days=8, reach='medium'),
    FeatureCandidate(name='Real-time EHR writeback', description='Write final codes back into EHR coding module.', business_value_score=8, ai_confidence=0.40, effort_days=18, reach='high', dependencies=['EHR vendor approval','writeback API access']),
    FeatureCandidate(name='Denial risk prediction', description='Predict denial probability for proposed code sets.', business_value_score=7, ai_confidence=0.52, effort_days=10, reach='medium', dependencies=['labeled denial training data']),
    FeatureCandidate(name='Voice dictation workflow', description='Let coders dictate corrections and notes.', business_value_score=4, ai_confidence=0.70, effort_days=7, reach='low'),
]

result = score_and_partition(candidates, timebox_days=55)
for bucket, feats in result['MoSCoW'].items():
    print('\n' + bucket)
    for f in feats:
        print(f"- {f.name}: score={f.score:.2f}, effort={f.effort_days}d, confidence={f.ai_confidence:.2f}")
print('\nEXECUTIVE 3 OPTIONS')
for opt in result['options']:
    print(f"\n{opt['label']}")
    print('features:', ', '.join(opt['features']))
    print('rationale:', opt['rationale'])
    print('tradeoff:', opt['tradeoff'])
```


Related: [[03 Permanent Notes/FDE Week 23a Executive Communication Playbook]]
