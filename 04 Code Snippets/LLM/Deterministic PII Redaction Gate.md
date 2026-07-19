# Deterministic PII Redaction Gate

> Domain 9 · AI Security & Governance. Regex-detect common identifiers and pseudonymize them before model or log exposure.

```python
import re, hashlib
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}

def pseudonymize(kind, value):
    digest = hashlib.sha256(value.encode()).hexdigest()[:10]
    return f"<{kind.upper()}:{digest}>"

def redact_pii(text):
    findings = []
    for kind, pat in PII_PATTERNS.items():
        def repl(m):
            findings.append({"type": kind, "value": m.group(0)})
            return pseudonymize(kind, m.group(0))
        text = pat.sub(repl, text)
    return text, findings

sample = "Email jane@corp.com or call 415-555-1212; SSN 123-45-6789."
redacted, findings = redact_pii(sample)
print(redacted)
print([f["type"] for f in findings])
```


Related: [[04 Code Snippets/LLM/RAG RBAC Audit Gate]]
