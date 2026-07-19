# AI Week 22b Underwriter SLO Dashboard Evaluator

> Week 22b · LLMOps, Monitoring, Cost & Reliability — Applied. Pydantic v2 SLO contract and deterministic weekly-report evaluator for availability, p95 latency, groundedness, refusal, hallucination, cost, tool success, error budget, cost tenants, and drift indicators.

```python
from __future__ import annotations
from collections import defaultdict
from statistics import mean
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Status = Literal['PASS', 'AT_RISK', 'BREACH']

class CustomerSLOContract(BaseModel):
    model_config = ConfigDict(extra='forbid')
    availability: float = Field(0.995, ge=0, le=1)
    p95_latency_s: float = Field(6.0, gt=0)
    groundedness: float = Field(0.92, ge=0, le=1)
    refusal_rate: float = Field(0.08, ge=0, le=1)
    hallucination_rate: float = Field(0.01, ge=0, le=1)
    cost_per_query_usd: float = Field(0.08, gt=0)
    tool_call_success: float = Field(0.98, ge=0, le=1)
    monthly_availability_error_budget_min: float = 216.0  # 99.5% ~= 3.6 hours/month

class RequestRecord(BaseModel):
    tenant: str
    latency_s: float
    answered: bool = True
    grounded_score: float
    refused: bool = False
    hallucinated: bool = False
    cost_usd: float
    tool_ok: bool = True
    query_embedding_shift: float = 0.0
    available: bool = True

class SLOResult(BaseModel):
    observed: float
    target: float
    status: Status
    delta: float

class PeriodReport(BaseModel):
    slo_results: dict[str, SLOResult]
    error_budget_remaining_pct: float
    top_cost_tenants: list[tuple[str, float]]
    top_drift_indicator: str
    markdown: str

def p95(values: list[float]) -> float:
    values = sorted(values)
    if not values:
        return 0.0
    index = int(round(0.95 * (len(values) - 1)))
    return values[index]

def classify_good(observed: float, target: float, higher_is_better: bool) -> Status:
    margin = observed - target if higher_is_better else target - observed
    if margin >= 0:
        return 'PASS'
    tolerance = abs(target) * 0.05
    return 'AT_RISK' if margin >= -tolerance else 'BREACH'

def evaluate_period(records: list[RequestRecord], contract: CustomerSLOContract = CustomerSLOContract()) -> PeriodReport:
    total = len(records)
    availability = sum(r.available for r in records) / total
    answered = [r for r in records if r.answered]
    latency = p95([r.latency_s for r in answered])
    grounded = mean([r.grounded_score for r in answered])
    refusal_rate = sum(r.refused for r in records) / total
    hallucination_rate = sum(r.hallucinated for r in records) / total
    cost = mean([r.cost_usd for r in answered])
    tool_success = sum(r.tool_ok for r in records) / total
    observed = {
        'availability': (availability, contract.availability, True),
        'p95_latency_s': (latency, contract.p95_latency_s, False),
        'groundedness': (grounded, contract.groundedness, True),
        'refusal_rate': (refusal_rate, contract.refusal_rate, False),
        'hallucination_rate': (hallucination_rate, contract.hallucination_rate, False),
        'cost_per_query_usd': (cost, contract.cost_per_query_usd, False),
        'tool_call_success': (tool_success, contract.tool_call_success, True),
    }
    results = {name: SLOResult(observed=round(v, 4), target=t, status=classify_good(v, t, hib), delta=round(v - t, 4)) for name, (v, t, hib) in observed.items()}
    downtime_min = (1 - availability) * contract.monthly_availability_error_budget_min / (1 - contract.availability)
    remaining = max(0.0, 100.0 * (1 - downtime_min / contract.monthly_availability_error_budget_min))
    by_tenant = defaultdict(float)
    drift_by_tenant = defaultdict(list)
    for r in records:
        by_tenant[r.tenant] += r.cost_usd
        drift_by_tenant[r.tenant].append(r.query_embedding_shift)
    top_cost = sorted(by_tenant.items(), key=lambda kv: kv[1], reverse=True)[:3]
    drift_scores = {tenant: mean(vals) for tenant, vals in drift_by_tenant.items()}
    drift_tenant, drift_value = max(drift_scores.items(), key=lambda kv: kv[1])
    lines = ['# Weekly Underwriter AI SLO Report', '', '| SLO | Observed | Target | Status | Delta |', '|---|---:|---:|---|---:|']
    for name, result in results.items():
        lines.append(f"| {name} | {result.observed:.4f} | {result.target:.4f} | {result.status} | {result.delta:+.4f} |")
    lines += ['', f'Error budget remaining: **{remaining:.1f}%**', '', 'Top cost tenants:']
    lines += [f'- {tenant}: ${amount:.2f}' for tenant, amount in top_cost]
    lines.append(f'Top drift indicator: {drift_tenant} rolling query shift {drift_value:.3f}')
    return PeriodReport(slo_results=results, error_budget_remaining_pct=round(remaining, 1), top_cost_tenants=[(t, round(c, 2)) for t, c in top_cost], top_drift_indicator=f'{drift_tenant}:{drift_value:.3f}', markdown='\n'.join(lines))

records = [RequestRecord(tenant=f'tenant-{i%4}', latency_s=4.2 + (i%9)*0.18, grounded_score=0.93 - (0.03 if i in {7, 31} else 0), refused=i%17==0, hallucinated=i==31, cost_usd=0.045 + (0.04 if i%13==0 else 0), tool_ok=i%29!=0, query_embedding_shift=0.10 + (0.25 if i%11==0 else 0)) for i in range(50)]
report = evaluate_period(records)
print(report.markdown)
```


Related: [[03 Permanent Notes/AI Week 22b Customer SLO Contract for Enterprise AI]]
