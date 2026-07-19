# Sample Ratio Mismatch Check

> Domain 6 · Online Evaluation (A/B, live feedback). Chi-square SRM check for expected assignment proportions.

```python
def srm_chi_square(observed, expected_props):
    total = sum(observed)
    exp = [total * p for p in expected_props]
    return sum((o-e)**2/e for o,e in zip(observed, exp))
print(srm_chi_square([5010,4990], [0.5,0.5]))
print(srm_chi_square([5600,4400], [0.5,0.5]))
```


Related: [[04 Code Snippets/LLM/AB Test Mean Difference CI]]
