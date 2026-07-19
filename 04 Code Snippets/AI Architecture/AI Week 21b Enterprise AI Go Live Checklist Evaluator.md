# AI Week 21b Enterprise AI Go Live Checklist Evaluator

> Week 21b · Security, Governance & Responsible AI — Applied. Pydantic v2 25-item AI production go-live checklist with GO, CONDITIONAL_GO, and NO_GO verdicts, grouped status report, blockers, and a second all-green scenario.

```python
from __future__ import annotations
from collections import defaultdict
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Status = Literal['green', 'amber', 'red']
Verdict = Literal['GO', 'CONDITIONAL_GO', 'NO_GO']

class ChecklistItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str
    category: str
    evidence_ref: str
    status: Status
    owner: str
    blocking: bool = True

class GoLiveChecklist(BaseModel):
    system: str
    items: list[ChecklistItem] = Field(min_length=1)

    def verdict(self) -> Verdict:
        if any(i.status == 'red' for i in self.items):
            return 'NO_GO'
        if any(i.status == 'amber' and i.blocking for i in self.items):
            return 'NO_GO'
        if any(i.status == 'amber' for i in self.items):
            return 'CONDITIONAL_GO'
        return 'GO'

    def blockers(self) -> list[ChecklistItem]:
        return [i for i in self.items if i.status == 'red' or (i.status == 'amber' and i.blocking)]

    def render_status_report(self) -> str:
        grouped = defaultdict(list)
        for item in self.items:
            grouped[item.category].append(item)
        lines = [f'# Go-Live Checklist — {self.system}', f'Verdict: **{self.verdict()}**', '']
        for category in sorted(grouped):
            lines.append(f'## {category}')
            for item in grouped[category]:
                marker = 'BLOCKER' if item in self.blockers() else ('WATCH' if item.status == 'amber' else 'OK')
                lines.append(f'- [{item.status.upper()}] {item.title} — owner: {item.owner}; evidence: {item.evidence_ref}; {marker}')
            lines.append('')
        if self.blockers():
            lines.append('## Required closures before traffic reaches 100%')
            for item in self.blockers():
                lines.append(f'- {item.title} ({item.category}) → {item.owner} must close {item.evidence_ref}')
        return '\n'.join(lines)

def seed_items() -> list[ChecklistItem]:
    raw = [
        ('Data classification approved','Data','DPIA-21b sec 2','green','DPO',True),
        ('Redact-before-embed enabled for names and DOBs','Data','ingestion-manifest-2026-07-18','green','Data Eng',True),
        ('Prompt-side PII scan enabled','Data','guardrail-config-v12','green','AppSec',True),
        ('GDPR Article 17 erasure workflow tested','Data','erasure-drill-04','amber','DPO',True),
        ('Entra groups mapped to underwriter roles','Identity & Access','iam-mapping-v5','green','IAM',True),
        ('Managed identity least privilege reviewed','Identity & Access','rbac-review-21b','green','Platform',True),
        ('No secrets in image or GitHub Actions logs','Identity & Access','trivy-secret-scan','green','Platform',True),
        ('Front Door WAF and TLS 1.2+ configured','Network','frontdoor-policy-prod','green','SRE',True),
        ('Private endpoints and private DNS verified','Network','pe-audit-prod','green','Network',True),
        ('Container App public egress denied','Network','egress-deny-test','green','Network',True),
        ('Postgres RLS by region and line passing','Network','rls-test-suite','red','Data Platform',True),
        ('Blob WORM immutability and CMK enabled','Audit & Retention','storage-policy-prod','green','Platform',True),
        ('OTel redaction boundary verified','Audit & Retention','trace-sample-review','green','SRE',True),
        ('Audit schema includes prompt/model/index/tool versions','Audit & Retention','audit-schema-v7','green','FDE',True),
        ('Retention conflict decision recorded','Audit & Retention','legal-retention-memo','amber','Legal',False),
        ('Prompt/model/index rollback tested','Versioning & Rollback','rollback-drill-21b','green','FDE/SRE',True),
        ('Eval regression green on underwriting golden set','Evaluation & Drift','eval-run-8831','green','FDE',True),
        ('Drift, safety, and cost alerts active','Evaluation & Drift','appins-alert-pack','green','SRE',True),
        ('Incident response runbooks approved','Incident Response','IR-LLM-01','green','CISO',True),
        ('DPIA and AI risk assessment complete','Governance','DPIA-21b','green','DPO',True),
        ('Model card and data card approved','Governance','model-card-v1 data-card-v1','red','Model Risk',True),
        ('Prompt registry approval complete','Governance','prompt-v21 approval','green','RAI Reviewer',True),
        ('Tool authorization catalog and HITL thresholds approved','Governance','tool-catalog-v3','amber','Underwriting Ops',False),
        ('LLM red-team and pen-test clean','Red Team','RT-clean-report','green','AppSec',True),
        ('DR restore, on-call rotation, and SLO contract signed','DR/BC, On-Call, Customer Contract','dr-test oncall-q3 slo-v1','green','SRE/Customer',True),
    ]
    return [ChecklistItem(title=t, category=c, evidence_ref=e, status=s, owner=o, blocking=b) for t,c,e,s,o,b in raw]

pre_go = GoLiveChecklist(system='Insurance Underwriter AI Assistant', items=seed_items())
print(pre_go.render_status_report())

closed_items = [item.model_copy(update={'status': 'green'}) for item in pre_go.items]
closed = GoLiveChecklist(system='Insurance Underwriter AI Assistant', items=closed_items)
print('\n' + '='*72 + '\n')
print(closed.render_status_report())
```


Related: [[03 Permanent Notes/AI Week 21b Enterprise AI Go-Live Checklist]]
