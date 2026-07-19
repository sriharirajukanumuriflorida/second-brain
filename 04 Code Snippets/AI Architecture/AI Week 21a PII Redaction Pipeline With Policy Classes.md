# AI Week 21a PII Redaction Pipeline With Policy Classes

> Week 21a · Security, Governance & Responsible AI — Reference Patterns. A Pydantic v2 PIIPolicy, deterministic regex-plus-heuristic entity detector, mask/tokenize strategies, redaction manifests with offsets, and policy diffs across Strict, Balanced, and Permissive settings.

```python
import hashlib
import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class PIIPolicy(BaseModel):
    model_config = ConfigDict(extra='forbid')
    redact_names: bool = True
    redact_emails: bool = True
    redact_phones: bool = True
    redact_ssn: bool = True
    redact_dates_of_birth: bool = True
    redact_addresses: bool = True
    tokenize_vs_mask: Literal['mask', 'tokenize'] = 'mask'
    entity_confidence_threshold: float = Field(default=0.75, ge=0, le=1)

COMMON_NAMES = {'Jane Doe', 'John Smith', 'Maria Garcia', 'Robert Johnson', 'Alice Brown'}
PATTERNS = [
    ('EMAIL', re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'), 'redact_emails', 0.99),
    ('PHONE', re.compile(r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b'), 'redact_phones', 0.95),
    ('SSN', re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), 'redact_ssn', 0.99),
    ('DOB', re.compile(r'\b(?:DOB|date of birth)[:\s]+(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|[A-Z][a-z]+ \d{1,2}, \d{4})\b'), 'redact_dates_of_birth', 0.92),
    ('ADDRESS', re.compile(r'\b\d{2,5}\s+[A-Z][A-Za-z]+\s+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Lane|Ln)\b(?:,\s*[A-Z][A-Za-z]+)?(?:,\s*[A-Z]{2})?\b'), 'redact_addresses', 0.88),
]

def _token(label, value):
    digest = hashlib.sha256((label + '|' + value.lower()).encode()).hexdigest()[:10]
    return f'[{label}_TOKEN_{digest}]'

def find_entities(text, policy):
    hits = []
    for label, pattern, flag, confidence in PATTERNS:
        if not getattr(policy, flag) or confidence < policy.entity_confidence_threshold:
            continue
        for m in pattern.finditer(text):
            hits.append({'type': label, 'start': m.start(), 'end': m.end(), 'text': m.group(0), 'confidence': confidence})
    if policy.redact_names:
        for name in COMMON_NAMES:
            for m in re.finditer(r'\b' + re.escape(name) + r'\b', text):
                if 0.86 >= policy.entity_confidence_threshold:
                    hits.append({'type': 'NAME', 'start': m.start(), 'end': m.end(), 'text': m.group(0), 'confidence': 0.86})
    hits.sort(key=lambda h: (h['start'], -(h['end'] - h['start'])))
    merged = []
    for h in hits:
        if merged and h['start'] < merged[-1]['end']:
            continue
        merged.append(h)
    return merged

def redact(text, policy):
    hits = find_entities(text, policy)
    redacted = text
    manifest = []
    for h in reversed(hits):
        replacement = f'[REDACTED_{h["type"]}]' if policy.tokenize_vs_mask == 'mask' else _token(h['type'], h['text'])
        redacted = redacted[:h['start']] + replacement + redacted[h['end']:]
        manifest.append({k: h[k] for k in ('type', 'start', 'end', 'confidence')} | {'replacement': replacement})
    manifest.reverse()
    return redacted, manifest

def policy_diff(text, policies):
    for name, policy in policies.items():
        out, manifest = redact(text, policy)
        print('\nPOLICY', name, 'redactions=', len(manifest))
        print(out)
        print(manifest)

strict = PIIPolicy(tokenize_vs_mask='tokenize', entity_confidence_threshold=0.70)
balanced = PIIPolicy(redact_names=False, entity_confidence_threshold=0.85)
permissive = PIIPolicy(redact_names=False, redact_dates_of_birth=False, redact_addresses=False, entity_confidence_threshold=0.95)
texts = [
    'Underwriter memo: Jane Doe DOB 03/14/1980 SSN 123-45-6789 qualifies for review.',
    'System log: user john.smith@example.com from 10.2.3.4 called /claims; support phone (415) 555-1212.',
    'Retrieved chunk: Mail forms to 123 Main St, Boston, MA or call 212-555-0199 for Alice Brown.'
]
for text in texts:
    print('\nBEFORE:', text)
    after, manifest = redact(text, strict)
    print('AFTER :', after)
    print('MANIFEST:', manifest)
policy_diff(texts[0], {'Strict': strict, 'Balanced': balanced, 'Permissive': permissive})
```


Related: [[03 Permanent Notes/AI Week 21a OWASP LLM Top 10 Engineering Controls Map]]
