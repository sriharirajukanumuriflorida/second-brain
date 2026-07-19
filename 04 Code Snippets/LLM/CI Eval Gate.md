# CI Eval Gate

> Domain 6 · Eval Framework Literacy (RAGAS, DeepEval, Promptfoo). Framework-agnostic gate that fails builds on metric regressions.

```python
def ci_gate(report, thresholds):
    failures=[]
    for metric, minimum in thresholds.items():
        value=report.get(metric)
        if value is None or value < minimum: failures.append(f"{metric}={value} below {minimum}")
    return {"pass": not failures, "failures": failures}
print(ci_gate({"faithfulness":0.82,"answer_relevance":0.76}, {"faithfulness":0.80,"answer_relevance":0.75}))
```


Related: [[04 Code Snippets/LLM/Eval Framework Selection Matrix]]
