# Preference Pair Quality Checks

> Domain 7 · Preference Optimization (RLHF, RLAIF, DPO, ORPO). Flag duplicate or low-signal chosen/rejected pairs.

```python
pairs=[("good","good"),("cites policy","invents guarantee")]
for c,r in pairs: print(c==r, abs(len(c)-len(r)))
```


Related: [[04 Code Snippets/LLM/DPO Loss on Toy Log Probabilities]]
