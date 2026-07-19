# Citation Coverage Checker

> Domain 6 · Groundedness / Faithfulness / Hallucination. Checks whether answer citations cover every claim and point to existing sources.

```python
def citation_coverage(claims, citations, sources):
    ids = set(sources)
    missing = []
    for i, claim in enumerate(claims):
        cited = citations.get(i, [])
        if not cited or not all(c in ids for c in cited): missing.append(claim)
    return {"coverage": 1 - len(missing)/max(1,len(claims)), "missing": missing}
print(citation_coverage(["A","B"], {0:["doc1"], 1:["doc9"]}, {"doc1":"text"}))
```


Related: [[04 Code Snippets/LLM/Claim Support Overlap Scorer]]
