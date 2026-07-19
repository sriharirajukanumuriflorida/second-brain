# SE Week 01+ GitHub Actions Delivery Workflow Validator

> Week 01+ · Production Delivery Engineering. Embed a realistic GitHub Actions workflow as a Python string and validate required production controls without network access.

```python
import re

GITHUB_ACTIONS_WORKFLOW = '''
name: ci
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: python -m pip install -r requirements.txt -r requirements-dev.txt
      - run: ruff check . && black --check . && mypy src
      - run: pytest --cov=src --cov-fail-under=85 --junitxml=reports/junit.xml
      - run: bandit -r src && pip-audit
      - uses: actions/upload-artifact@v4
        with:
          name: test-reports-${{ matrix.python-version }}
          path: reports/
  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - run: echo deploy immutable artifact to staging
'''

REQUIRED_PATTERNS = {
    "least_privilege_permissions": r"permissions:\s*\n\s*contents: read",
    "matrix_python": r"matrix:\s*\n\s*python-version:.*3\.11.*3\.12",
    "dependency_cache": r"cache: pip",
    "coverage_gate": r"--cov-fail-under=85",
    "sast_sca": r"bandit -r src && pip-audit",
    "artifact_upload": r"actions/upload-artifact@v4",
    "protected_environment": r"environment: staging",
}

def validate_workflow(text):
    missing = [name for name, pattern in REQUIRED_PATTERNS.items()
               if not re.search(pattern, text, flags=re.S)]
    return {"ok": not missing, "missing": missing, "lines": len(text.splitlines())}

print(validate_workflow(GITHUB_ACTIONS_WORKFLOW))
```


Related: [[03 Permanent Notes/SE Week 01+ CI CD Pipeline Design Checklist]]
