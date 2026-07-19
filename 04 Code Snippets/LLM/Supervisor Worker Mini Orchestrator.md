# Supervisor Worker Mini Orchestrator

> Domain 5 · Multi-Agent Orchestration. Dispatch deterministic role workers

```python
def worker(role, task): return f"{role} handled {task}"
trace=[]
for role in ["researcher","critic","writer"]:
    trace.append((role, worker(role,"tools")))
print(trace)
```


Related: [[04 Code Snippets/LLM/Multi-Agent Blackboard Store]]
