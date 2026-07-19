# Leaderboard Normalization

> Domain 6 · Benchmark Literacy. Combine benchmark, cost, and latency into task-fit instead of ranking by one public metric.

```python
def task_fit(row, weights):
    return sum(row[k]*w for k,w in weights.items()) / sum(weights.values())
models={"A":{"bench":0.92,"cost":0.40,"latency":0.50},"B":{"bench":0.86,"cost":0.90,"latency":0.85}}
weights={"bench":2,"cost":1,"latency":1}
print(sorted((task_fit(v, weights), k) for k,v in models.items()))
```


Related: [[04 Code Snippets/LLM/Benchmark Contamination Probe]]
