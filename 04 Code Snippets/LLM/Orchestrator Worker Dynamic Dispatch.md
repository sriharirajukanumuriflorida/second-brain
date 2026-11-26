# Orchestrator Worker Dynamic Dispatch

> Domain 5 · Agentic Workflow Patterns. Orchestrator decides subtask count/shape at runtime; workers execute; synthesizer combines.

```python
def orchestrator(task):
    # In production this is an LLM call producing a plan; here, deterministic for demo.
    if "report" in task:
        return ["gather_data", "analyze_trends", "draft_summary"]
    return ["handle_generic"]

def worker(subtask):
    return f"result({subtask})"

def synthesize(results):
    return " + ".join(results)

plan = orchestrator("write market report")
results = [worker(s) for s in plan]
print(synthesize(results))
```

Related: [[04 Code Snippets/LLM/Agentic Workflow Pattern Selector]]
