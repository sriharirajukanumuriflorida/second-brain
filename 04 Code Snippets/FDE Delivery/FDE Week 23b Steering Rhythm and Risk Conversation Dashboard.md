# FDE Week 23b Steering Rhythm and Risk Conversation Dashboard

> Week 23b · Customer Discovery & Stakeholder Communication — Applied. Pydantic v2 live engagement dashboard for week 8 and week 19, rendering the weekly five-slide steering pack, risk register, decision log, stakeholder cadence, and calm hard-conversation messaging.

```python
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Status = Literal['green','yellow','red']

class SprintStatus(BaseModel):
    week: int; goals: list[str]; delivered: list[str]; blockers: list[str]; burnup_done: int; burnup_total: int

class RiskItem(BaseModel):
    risk: str; likelihood: Literal['low','medium','high']; impact: Literal['low','medium','high']; mitigation: str; owner: str; status: Status; review_date: str
    @property
    def severity(self):
        score = {'low':1,'medium':2,'high':3}[self.likelihood] * {'low':1,'medium':2,'high':3}[self.impact]
        return score

class Decision(BaseModel):
    date: str; what: str; who: str; rationale: str

class CommsCadence(BaseModel):
    stakeholder: str; cadence: str; last_update: str; status: Status; note: str

class EngagementDashboard(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str; sprint: SprintStatus; risks: list[RiskItem]; decisions: list[Decision]; comms: list[CommsCadence]; demo_highlight: str; exec_message: str
    def top_risks(self): return sorted(self.risks, key=lambda r: (r.status == 'red', r.status == 'yellow', r.severity), reverse=True)[:3]
    def render_weekly_exec_slide_pack(self) -> str:
        pct = self.sprint.burnup_done / self.sprint.burnup_total * 100
        lines = [f'# Weekly steering pack — {self.title} — week {self.sprint.week}', '', '## Slide 1 — Burn-up narrative', f'- Scope complete: {self.sprint.burnup_done}/{self.sprint.burnup_total} delivery units ({pct:.0f}%).', f'- Exec message: {self.exec_message}', '', '## Slide 2 — This week / next week', '**Goals**:']
        lines += [f'- {g}' for g in self.sprint.goals]
        lines += ['**Delivered**:'] + [f'- {d}' for d in self.sprint.delivered]
        lines += ['**Blockers**:'] + ([f'- {b}' for b in self.sprint.blockers] or ['- none'])
        lines += ['', '## Slide 3 — Top 3 risks']
        for r in self.top_risks(): lines.append(f'- [{r.status.upper()}] {r.risk} — owner={r.owner}; mitigation={r.mitigation}; review={r.review_date}')
        lines += ['', '## Slide 4 — Top decisions needed']
        for d in self.decisions[-5:]: lines.append(f'- {d.date}: {d.what} — {d.who}; rationale: {d.rationale}')
        lines += ['', '## Slide 5 — Demo highlight', f'- {self.demo_highlight}', '', '## Cadence health']
        for c in self.comms: lines.append(f'- [{c.status.upper()}] {c.stakeholder} ({c.cadence}) last={c.last_update}: {c.note}')
        return '\n'.join(lines)

def dashboard_week8() -> EngagementDashboard:
    return EngagementDashboard(title='Insurance Underwriter AI Assistant', sprint=SprintStatus(week=8, goals=['Close refusal-threshold tuning with eval team','Finish Guidewire-context retrieval filters','Prepare week-9 SME golden-set review'], delivered=['Valid-question refusal case reproduced and added to golden set','Threshold adjusted after showing hallucination-rate impact','PTU cost forecast reviewed against Standard baseline'], blockers=['Awaiting final procurement confirmation for Azure OpenAI production quota'], burnup_done=31, burnup_total=92), risks=[RiskItem(risk='Refusal threshold blocks legitimate underwriting questions', likelihood='medium', impact='medium', mitigation='Tune threshold with golden-set slices and same-day CUO note', owner='FDE + eval lead', status='yellow', review_date='week 9'), RiskItem(risk='Azure OpenAI PTU estimate 30% over forecast', likelihood='medium', impact='medium', mitigation='Stay Standard until 200-user trigger; CFO memo sent', owner='FDE + platform lead', status='yellow', review_date='week 10'), RiskItem(risk='Hallucination causes unsupported recommendation', likelihood='medium', impact='high', mitigation='Citations, refusal path, senior-review queue, golden-set gate', owner='Commercial SME', status='yellow', review_date='weekly'), RiskItem(risk='DPO rejects data-boundary evidence', likelihood='low', impact='high', mitigation='Private endpoint design review and redacted telemetry sample', owner='DPO/platform lead', status='green', review_date='week 12'), RiskItem(risk='SME labeling bottleneck slows evals', likelihood='medium', impact='medium', mitigation='Biweekly working session and 20-question batches', owner='SME leads', status='green', review_date='weekly')], decisions=[Decision(date='week 7', what='Keep automatic underwriting decisions out of v1', who='CUO + FDE', rationale='Preserve Tier 2 decision-support posture'), Decision(date='week 8', what='Lower refusal threshold for commercial exception questions', who='FDE + eval lead + SME', rationale='Improves valid-answer rate with hallucination still under 1% on slice'), Decision(date='week 8', what='Remain on Standard Azure OpenAI for pilot', who='FDE recommendation to CFO', rationale='PTU not economical until 200-user scale or p95 variance requires it')], comms=[CommsCadence(stakeholder='CUO', cadence='weekly steering', last_update='today', status='green', note='Refusal tradeoff communicated same day'), CommsCadence(stakeholder='Underwriter SMEs', cadence='biweekly working session', last_update='2 days ago', status='green', note='Golden-set ownership active'), CommsCadence(stakeholder='CFO', cadence='budget exception memo as needed', last_update='today', status='green', note='PTU/Standard memo sent'), CommsCadence(stakeholder='DPO/CISO', cadence='monthly risk committee', last_update='3 weeks ago', status='yellow', note='next evidence review due')], demo_highlight='Commercial policy question answered in 52 seconds with policy, memo, and regulatory citations; refusal example shows improved valid-answer behavior and updated eval numbers.', exec_message='We made a measured refusal-threshold adjustment and contained the PTU cost surprise with a Standard-until-scale recommendation; no change to timeline or business case.')

def dashboard_week19() -> EngagementDashboard:
    d = dashboard_week8().model_copy(deep=True)
    d.sprint = SprintStatus(week=19, goals=['Close SRB red-team evidence gap','Complete 25-item go-live checklist blockers','Move training analytics to v2 backlog'], delivered=['SRB feedback received and triaged','Red-team plan added to final three weeks','Nice-to-have scope moved without changing core business benefit'], blockers=['Production go-live waits for added red-team evidence and checklist closure'], burnup_done=76, burnup_total=92)
    d.risks.append(RiskItem(risk='SRB requires additional red-team evidence before go-live', likelihood='high', impact='high', mitigation='Re-scope final 3 weeks to red-team closure; defer training analytics to v2', owner='FDE + CISO + AppSec', status='red', review_date='weekly until go-live'))
    d.decisions.append(Decision(date='week 19', what='Re-plan final three weeks for SRB evidence', who='CUO + CISO + FDE', rationale='Protect go-live approval and preserve core time-to-quote benefit'))
    d.comms = [CommsCadence(stakeholder='CUO', cadence='weekly steering', last_update='today', status='green', note='Re-plan explained: what changes, impact, recommendation'), CommsCadence(stakeholder='CISO/SRB', cadence='weekly until approval', last_update='today', status='green', note='Evidence owner map agreed'), CommsCadence(stakeholder='Underwriter SMEs', cadence='biweekly working session', last_update='1 week ago', status='green', note='Training analytics moved to v2; golden set unaffected'), CommsCadence(stakeholder='CFO', cadence='monthly budget', last_update='1 week ago', status='green', note='No budget increase; scope swap only')]
    d.demo_highlight = 'Go-live readiness demo shows audit trail, groundedness >= 92%, and red-team evidence checklist; training analytics explicitly labeled v2.'
    d.exec_message = 'SRB feedback changes the last three weeks of work, not the core business benefit: we will close red-team evidence before production and defer one nice-to-have to v2.'
    return d

print(dashboard_week8().render_weekly_exec_slide_pack())
print('\n' + '='*80 + '\n')
print(dashboard_week19().render_weekly_exec_slide_pack())
```


Related: [[03 Permanent Notes/FDE Week 23b Hard Conversation Templates for AI Engagements]]
