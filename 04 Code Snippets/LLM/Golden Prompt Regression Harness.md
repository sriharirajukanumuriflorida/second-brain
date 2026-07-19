# Golden Prompt Regression Harness

> Domain 3 · Prompt Versioning & Regression Testing. Compare two prompt versions over a golden set and fail CI on behavior regressions.

```python
def fake_model(prompt_version, case):
    text = case["input"].lower()
    if "refund" in text or "invoice" in text: label = "billing"
    elif "error" in text or "crash" in text: label = "bug"
    else: label = "other"
    if prompt_version.endswith("bad") and "refund" in text: label = "other"
    return {"label": label}

def run_regression(version, golden):
    rows, ok = [], 0
    for case in golden:
        pred = fake_model(version, case)
        passed = pred["label"] == case["expected"]
        ok += int(passed); rows.append((case["id"], passed, pred["label"], case["expected"]))
    return ok / len(golden), rows

golden = [{"id":"g1","input":"Refund my invoice","expected":"billing"},
          {"id":"g2","input":"App crashes with error 500","expected":"bug"}]
score, rows = run_regression("support_triage@1.3.0", golden)
print("score", score, "pass", score >= 0.95, rows)
```


Related: [[04 Code Snippets/LLM/Prompt Registry With Semantic Versions]]
