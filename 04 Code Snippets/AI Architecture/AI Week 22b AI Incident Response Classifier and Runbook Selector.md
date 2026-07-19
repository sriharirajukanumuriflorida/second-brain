# AI Week 22b AI Incident Response Classifier and Runbook Selector

> Week 22b · LLMOps, Monitoring, Cost & Reliability — Applied. Rule-driven Pydantic incident classifier that maps alerts to first SLI check, rollback axis, customer message, and post-incident correction for the underwriter assistant.

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

SignalType = Literal['groundedness_drop','cost_spike','latency_regression','safety_flag_spike','provider_5xx_burst','injection_pattern_detected']
Axis = Literal['prompt','model','index','tenant_limit','provider_route','guardrail']

class AlertPayload(BaseModel):
    model_config = ConfigDict(extra='forbid')
    signal_type: SignalType
    magnitude: float
    tenant: str
    model: str
    prompt_version: str

class Runbook(BaseModel):
    incident: str
    sli_to_check_first: str
    rollback_axis: Axis
    steps: list[str]
    customer_message_template: str
    post_incident_correction: str

def select_runbook(alert: AlertPayload) -> Runbook:
    common = ['Acknowledge page and open incident channel', 'Attach App Insights trace links and current prompt/model/index tuple']
    if alert.signal_type == 'groundedness_drop':
        return Runbook(
            incident='Groundedness regression canary', rollback_axis='model', sli_to_check_first='Hourly golden-set groundedness and canary-vs-baseline delta',
            steps=common + ['Confirm eval agent is healthy', 'Compare Azure OpenAI deployment and prompt version to last green canary', 'Rollback model deployment if changed; otherwise rollback prompt pointer', 'Monitor next canary before closing mitigation'],
            customer_message_template='We detected a quality regression in controlled canaries for {tenant}, mitigated by reverting the model/prompt lane, and are validating the next canary before user traffic is expanded.',
            post_incident_correction='Add failed canary items to the golden set and pin or isolate the model deployment where supported.')
    if alert.signal_type == 'cost_spike':
        return Runbook(
            incident='Runaway retrieval-context or agent cost', rollback_axis='tenant_limit', sli_to_check_first='Cost/query, prompt-token p95, retrieved.count p95 by tenant and prompt version',
            steps=common + ['Slice spend by tenant, feature, prompt version, model, and token type', 'Apply temporary per-tenant rate limit or feature throttle', 'Rollback prompt/index if retrieval context expanded after release', 'Review query pattern with customer owner'],
            customer_message_template='We see a spend anomaly isolated to {tenant}; service remains available while we apply a temporary budget guard and review the usage pattern with your team.',
            post_incident_correction='Add cost regression tests and an alert on retrieval-context token p95; tune top-k/rerank/prompt context.')
    if alert.signal_type == 'injection_pattern_detected':
        return Runbook(
            incident='Suspected prompt injection', rollback_axis='guardrail', sli_to_check_first='Safety flag spike and audit report of system-prompt leakage',
            steps=common + ['Capture Blob audit record and trace id', 'Block similar pattern with guardrail rule', 'Escalate to security and compliance', 'Pause affected prompt version or tenant route if needed'],
            customer_message_template='We detected a suspected prompt-injection pattern for {tenant}, contained similar prompts, preserved audit evidence, and escalated to security for impact review.',
            post_incident_correction='Add the attack to red-team and golden evals; strengthen delimiters, instruction precedence, and retrieval sanitization.')
    if alert.signal_type == 'latency_regression':
        axis = 'model' if alert.magnitude > 1.5 else 'index'
        return Runbook(incident='Latency regression', rollback_axis=axis, sli_to_check_first='p95 /query latency by model, index, tenant, and provider status', steps=common + ['Check Azure OpenAI latency and Postgres retrieval latency', f'Rollback {axis} axis if regression aligns with release', 'Scale Container Apps or switch PTU/Standard route if saturation is confirmed'], customer_message_template='We are mitigating a latency regression affecting {tenant}; answers remain controlled by the same audit and quality gates.', post_incident_correction='Add latency replay case and capacity threshold to release gate.')
    if alert.signal_type == 'provider_5xx_burst':
        return Runbook(incident='Azure OpenAI provider 5xx burst', rollback_axis='provider_route', sli_to_check_first='Provider 5xx rate and Retry-After compliance', steps=common + ['Enable circuit breaker', 'Reduce concurrency and respect Retry-After', 'Fail to cached-answer/human-review mode for high-risk questions'], customer_message_template='Azure OpenAI is returning elevated transient errors; we have reduced retry pressure and enabled fallback operating mode for {tenant}.', post_incident_correction='Tune retry budget and provider outage drill.')
    return Runbook(incident='Safety flag spike', rollback_axis='guardrail', sli_to_check_first='Unsafe completion rate and refusal correctness', steps=common + ['Raise refusal threshold', 'Review flagged samples', 'Escalate if regulated content was exposed'], customer_message_template='We are investigating elevated safety flags for {tenant} and have tightened temporary guardrails.', post_incident_correction='Refresh safety eval set and policy labels.')

scenarios = [
    AlertPayload(signal_type='groundedness_drop', magnitude=0.025, tenant='commercial-lines', model='gpt-4o-prod', prompt_version='prompt-v21'),
    AlertPayload(signal_type='cost_spike', magnitude=4.0, tenant='west-region', model='gpt-4o-prod', prompt_version='prompt-v21'),
    AlertPayload(signal_type='injection_pattern_detected', magnitude=1.0, tenant='commercial-lines', model='gpt-4o-prod', prompt_version='prompt-v21'),
]
for alert in scenarios:
    rb = select_runbook(alert)
    print('\n##', rb.incident)
    print('first SLI:', rb.sli_to_check_first)
    print('rollback axis:', rb.rollback_axis)
    for step in rb.steps:
        print('-', step)
    print('customer:', rb.customer_message_template.format(tenant=alert.tenant))
    print('correction:', rb.post_incident_correction)
```


Related: [[03 Permanent Notes/AI Week 22b Enterprise AI On-Call Runbook Bundle]]
