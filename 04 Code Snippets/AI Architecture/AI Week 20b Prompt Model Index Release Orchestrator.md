# AI Week 20b Prompt Model Index Release Orchestrator

> Week 20b · Cloud Architecture & Deployment — Applied. Deterministic release planner for independent prompt, model, and index changes with canary promotion stages and per-axis rollback plans.

```python
from dataclasses import dataclass
from typing import Literal

Axis = Literal['prompt', 'model', 'index']
Decision = Literal['PROMOTE', 'HOLD', 'ROLLBACK']

@dataclass(frozen=True)
class VersionTuple:
    prompt: str
    model: str
    index: str

@dataclass(frozen=True)
class Metrics:
    latency_p95_ms: int
    error_rate: float
    groundedness_score: float
    cost_per_query: float

@dataclass(frozen=True)
class Guardrails:
    max_latency_p95_ms: int = 8500
    max_error_rate: float = 0.02
    min_groundedness_score: float = 0.86
    max_cost_per_query: float = 0.08

@dataclass(frozen=True)
class StageResult:
    traffic_percent: int
    decision: Decision
    reasons: list[str]

@dataclass(frozen=True)
class ReleasePlan:
    current: VersionTuple
    proposed: VersionTuple
    changed_axes: list[Axis]
    stages: list[StageResult]
    rollback_plan: dict[Axis, str]

def changed_axes(current: VersionTuple, proposed: VersionTuple) -> list[Axis]:
    return [axis for axis in ('prompt', 'model', 'index') if getattr(current, axis) != getattr(proposed, axis)]

def judge(metrics: Metrics, guardrails: Guardrails) -> tuple[Decision, list[str]]:
    reasons = []
    if metrics.latency_p95_ms > guardrails.max_latency_p95_ms:
        reasons.append(f'latency {metrics.latency_p95_ms}>{guardrails.max_latency_p95_ms}')
    if metrics.error_rate > guardrails.max_error_rate:
        reasons.append(f'error_rate {metrics.error_rate:.3f}>{guardrails.max_error_rate:.3f}')
    if metrics.groundedness_score < guardrails.min_groundedness_score:
        reasons.append(f'groundedness {metrics.groundedness_score:.2f}<{guardrails.min_groundedness_score:.2f}')
    if metrics.cost_per_query > guardrails.max_cost_per_query:
        reasons.append(f'cost {metrics.cost_per_query:.3f}>{guardrails.max_cost_per_query:.3f}')
    return ('ROLLBACK' if reasons else 'PROMOTE'), reasons or ['all guardrails passed']

def infer_axes_to_rollback(axes: list[Axis], reasons: list[str]) -> list[Axis]:
    if any('groundedness' in r for r in reasons) and 'prompt' in axes:
        return ['prompt']
    if any('latency' in r or 'cost' in r for r in reasons) and 'model' in axes:
        return ['model']
    if any('groundedness' in r for r in reasons) and 'index' in axes:
        return ['index']
    return axes

def orchestrate_release(current: VersionTuple, proposed_changes: dict[str, str], canary_metrics: list[Metrics], guardrails: Guardrails) -> ReleasePlan:
    proposed = VersionTuple(
        prompt=proposed_changes.get('prompt', current.prompt),
        model=proposed_changes.get('model', current.model),
        index=proposed_changes.get('index', current.index),
    )
    axes = changed_axes(current, proposed)
    stages = []
    rollback_axes: set[Axis] = set()
    for pct, metrics in zip((10, 50, 100), canary_metrics):
        decision, reasons = judge(metrics, guardrails)
        stages.append(StageResult(pct, decision, reasons))
        if decision == 'ROLLBACK':
            rollback_axes.update(infer_axes_to_rollback(axes, reasons))
            break
    rollback_plan = {}
    for axis in axes:
        if axis in rollback_axes:
            rollback_plan[axis] = f'rollback {axis} to {getattr(current, axis)}; preserve other axes if healthy'
        else:
            rollback_plan[axis] = f'keep {getattr(proposed, axis)}; no rollback triggered for {axis}'
    return ReleasePlan(current, proposed, axes, stages, rollback_plan)

def print_plan(name: str, plan: ReleasePlan):
    print()
    print(f"{name}: changed={plan.changed_axes} proposed={plan.proposed}")
    for stage in plan.stages:
        print(f"  {stage.traffic_percent:3d}% {stage.decision:8s} reasons={stage.reasons}")
    for axis, action in plan.rollback_plan.items():
        print(f"  {axis}: {action}")

current = VersionTuple(prompt='prompt-v17', model='gpt-4o-prod', index='index-2026-07-17')
guards = Guardrails()
healthy = [Metrics(6200, 0.006, 0.91, 0.031), Metrics(6500, 0.007, 0.90, 0.032), Metrics(6800, 0.008, 0.90, 0.033)]
prompt_bad = [Metrics(6100, 0.006, 0.80, 0.031)]
model_slow = [Metrics(9400, 0.006, 0.90, 0.041)]
print_plan('healthy release', orchestrate_release(current, {'prompt': 'prompt-v18'}, healthy, guards))
print_plan('prompt groundedness regression', orchestrate_release(current, {'prompt': 'prompt-v18', 'model': 'gpt-4o-prod', 'index': 'index-2026-07-17'}, prompt_bad, guards))
print_plan('model latency regression', orchestrate_release(current, {'model': 'gpt-4o-2024-11-prod'}, model_slow, guards))
```


Related: [[03 Permanent Notes/AI Week 20b Prompt Model Index Release Discipline]]
