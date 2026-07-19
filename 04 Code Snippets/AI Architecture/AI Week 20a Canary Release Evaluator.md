# AI Week 20a Canary Release Evaluator

> Week 20a · Cloud Architecture & Deployment — Reference Patterns. A deterministic gate comparing baseline and canary latency, error rate, and groundedness to return PROMOTE, HOLD, or ROLLBACK with reasons.

```python
from dataclasses import dataclass
from enum import Enum

class Decision(str, Enum):
    PROMOTE = 'PROMOTE'
    HOLD = 'HOLD'
    ROLLBACK = 'ROLLBACK'

@dataclass(frozen=True)
class Metrics:
    p95_latency_ms: float
    error_rate: float
    groundedness: float

@dataclass(frozen=True)
class RolloutConfig:
    traffic_percent: int
    max_latency_regression_pct: float = 20.0
    max_error_rate_abs: float = 0.02
    max_error_rate_delta: float = 0.01
    min_groundedness: float = 0.86
    rollback_groundedness_drop: float = 0.05

def evaluate_canary(baseline: Metrics, canary: Metrics, cfg: RolloutConfig):
    reasons = []
    latency_delta = ((canary.p95_latency_ms - baseline.p95_latency_ms) / baseline.p95_latency_ms) * 100
    error_delta = canary.error_rate - baseline.error_rate
    groundedness_drop = baseline.groundedness - canary.groundedness
    if groundedness_drop >= cfg.rollback_groundedness_drop or canary.groundedness < cfg.min_groundedness - 0.03:
        return Decision.ROLLBACK, [f'groundedness dropped {groundedness_drop:.3f} to {canary.groundedness:.3f}']
    if canary.error_rate > cfg.max_error_rate_abs + 0.02:
        return Decision.ROLLBACK, [f'error rate {canary.error_rate:.3%} is unsafe']
    if latency_delta > cfg.max_latency_regression_pct:
        reasons.append(f'p95 latency regression {latency_delta:.1f}% exceeds {cfg.max_latency_regression_pct:.1f}%')
    if error_delta > cfg.max_error_rate_delta or canary.error_rate > cfg.max_error_rate_abs:
        reasons.append(f'error-rate delta {error_delta:.3%} or absolute {canary.error_rate:.3%} exceeds guardrail')
    if canary.groundedness < cfg.min_groundedness:
        reasons.append(f'groundedness {canary.groundedness:.3f} below floor {cfg.min_groundedness:.3f}')
    return (Decision.HOLD, reasons) if reasons else (Decision.PROMOTE, [f'{cfg.traffic_percent}% canary within guardrails'])

baseline = Metrics(900, 0.008, 0.91)
config = RolloutConfig(traffic_percent=10)
for name, metrics in {'healthy canary': Metrics(880, 0.007, 0.915), 'latency regression': Metrics(1180, 0.009, 0.905), 'groundedness drop': Metrics(870, 0.007, 0.82)}.items():
    decision, reasons = evaluate_canary(baseline, metrics, config)
    print(name, '->', decision.value, '|', '; '.join(reasons))
```


Related: [[03 Permanent Notes/AI Week 20a Cloud AI Platform Decision Guide]]
