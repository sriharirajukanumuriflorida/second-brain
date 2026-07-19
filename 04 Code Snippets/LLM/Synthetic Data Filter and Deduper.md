# Synthetic Data Filter and Deduper

> Domain 7 · Synthetic Data Generation. Filter rows by quality score and remove normalized duplicates.

```python
rows=[{"prompt":"Summarize X","answer":"A", "score":.9},{"prompt":"summarize x ","answer":"A","score":.8},{"prompt":"","answer":"bad","score":.2}]
seen=set(); kept=[]
for r in rows:
    key=(r["prompt"].strip().lower(), r["answer"].strip().lower())
    if r["score"]>=.7 and key[0] and key not in seen:
        seen.add(key); kept.append(r)
print(kept)
```


Related: [[04 Code Snippets/LLM/Synthetic Eval Contamination Check]]
