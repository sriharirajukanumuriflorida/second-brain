# Agentic Workflow Pattern Selector

> Domain 5 · Agentic Workflow Patterns. Map task-shape questions to one of the five canonical workflow archetypes.

```python
def select_pattern(subtasks_known_upfront, subtasks_independent, needs_classification, needs_quality_iteration):
    if needs_classification:
        return "routing"
    if needs_quality_iteration:
        return "evaluator-optimizer"
    if not subtasks_known_upfront:
        return "orchestrator-workers"
    if subtasks_independent:
        return "parallelization"
    return "prompt-chaining"

print(select_pattern(True, False, False, False))   # prompt-chaining
print(select_pattern(True, True, False, False))     # parallelization
print(select_pattern(False, False, False, False))   # orchestrator-workers
```

Related: [[04 Code Snippets/LLM/Orchestrator Worker Dynamic Dispatch]]
