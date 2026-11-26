# Trajectory Level Agent Scorer

> Domain 6 · Eval Fundamentals. Score response correctness, step validity, and trajectory efficiency separately.

```python
def score_trajectory(actual_steps, expected_steps, final_correct):
    response_score = 1.0 if final_correct else 0.0
    valid_steps = sum(1 for s in actual_steps if s in {"search", "compute", "verify", "finish"})
    step_score = valid_steps / max(1, len(actual_steps))
    trajectory_score = 1.0 if actual_steps == expected_steps else max(0.0, 1 - abs(len(actual_steps) - len(expected_steps)) / len(expected_steps))
    return {"response": response_score, "step": step_score, "trajectory": trajectory_score}

print(score_trajectory(["search", "search", "search", "finish"], ["search", "finish"], True))
print(score_trajectory(["search", "finish"], ["search", "finish"], True))
```

Related: [[04 Code Snippets/LLM/Golden Dataset Metric Harness]], [[04 Code Snippets/LLM/Eval Slice Gate]]
