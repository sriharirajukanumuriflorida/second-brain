# AI Week 22a SLO and Cost Budget Guard

> Week 22a · LLMOps, Monitoring, Cost & Reliability — Reference Patterns. A Pydantic v2 policy model and deterministic evaluator that allows, downgrades, or denies requests based on SLO thresholds, user budgets, tenant caps, and system-query exceptions.

```python
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class Action(str, Enum):
    ALLOW = 'ALLOW'
    DOWNGRADE = 'DOWNGRADE-TO-CHEAPER-MODEL'
    DENY = 'DENY-WITH-BUDGET-ERROR'

class SLOThresholds(BaseModel):
    model_config = ConfigDict(extra='forbid')
    availability: float = Field(default=0.999, ge=0, le=1)
    p95_latency_ms: int = Field(default=4000, ge=1)
    groundedness: float = Field(default=0.88, ge=0, le=1)
    max_cost_per_request_usd: float = Field(default=0.20, gt=0)

class BudgetPolicy(BaseModel):
    model_config = ConfigDict(extra='forbid')
    per_user_daily_budget_usd: float = Field(default=2.00, gt=0)
    per_tenant_monthly_cap_usd: float = Field(default=100.00, gt=0)
    fallback_model: str = 'gpt-4o-mini-prod'
    downgrade_when_user_remaining_below_usd: float = 0.25

class RequestContext(BaseModel):
    user_id: str
    tenant_id: str
    feature: str
    model: str
    estimated_cost_usd: float
    is_system_query: bool = False

def evaluate_request(ctx: RequestContext, user_spend_today: dict[str, float], tenant_spend_month: dict[str, float], policy: BudgetPolicy):
    if ctx.is_system_query:
        return Action.ALLOW, ctx.model, 'system query'
    tenant_after = tenant_spend_month.get(ctx.tenant_id, 0.0) + ctx.estimated_cost_usd
    if tenant_after > policy.per_tenant_monthly_cap_usd:
        return Action.DENY, None, f'tenant monthly cap exceeded: {tenant_after:.2f}'
    user_after = user_spend_today.get(ctx.user_id, 0.0) + ctx.estimated_cost_usd
    remaining = policy.per_user_daily_budget_usd - user_after
    if user_after > policy.per_user_daily_budget_usd:
        if ctx.model != policy.fallback_model:
            return Action.DOWNGRADE, policy.fallback_model, f'user daily budget would exceed by {abs(remaining):.2f}'
        return Action.DENY, None, f'user daily cap exceeded: {user_after:.2f}'
    if remaining < policy.downgrade_when_user_remaining_below_usd and ctx.model != policy.fallback_model:
        return Action.DOWNGRADE, policy.fallback_model, f'user budget nearly exhausted: {remaining:.2f} remaining'
    return Action.ALLOW, ctx.model, f'budget ok: {remaining:.2f} user budget remaining'

slo = SLOThresholds()
policy = BudgetPolicy()
user_spend = {'heavy': 1.82}
tenant_spend = {'over-cap': 100.05, 'acme': 73.20}
scenarios = [
    RequestContext(user_id='fresh', tenant_id='acme', feature='chat', model='gpt-4o-prod', estimated_cost_usd=0.08),
    RequestContext(user_id='heavy', tenant_id='acme', feature='analysis', model='gpt-4o-prod', estimated_cost_usd=0.15),
    RequestContext(user_id='u3', tenant_id='over-cap', feature='chat', model='gpt-4o-mini-prod', estimated_cost_usd=0.01),
    RequestContext(user_id='monitor', tenant_id='over-cap', feature='health-check', model='gpt-4o-prod', estimated_cost_usd=0.50, is_system_query=True),
]
for ctx in scenarios:
    action, model, reason = evaluate_request(ctx, user_spend, tenant_spend, policy)
    print(ctx.user_id, '->', action.value, model, '|', reason)
print('slo_floor_groundedness', slo.groundedness, 'p95_ms', slo.p95_latency_ms)
```


Related: [[03 Permanent Notes/AI Week 22a AI SLO Design Guide]]
