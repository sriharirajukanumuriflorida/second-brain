# Synthetic Eval Contamination Check

> Domain 7 · Synthetic Data Generation. Catch generated training rows that overlap with held-out eval prompts.

```python
train_prompts={"define sft","write refund email","summarize x"}
eval_prompts={"define sft","hard legal question"}
leak=train_prompts & eval_prompts
print("leaks", leak)
assert not ({"write refund email"} & eval_prompts)
```


Related: [[04 Code Snippets/LLM/Synthetic Data Filter and Deduper]]
