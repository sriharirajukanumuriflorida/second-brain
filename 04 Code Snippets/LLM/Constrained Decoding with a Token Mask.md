# Constrained Decoding with a Token Mask

> Domain 2 · Structured / Constrained Generation. Toy grammar-constrained decoder: only tokens legal in the current state are sampled.

```python
import numpy as np
# Minimal illustration: generate a boolean JSON value {"ok": true|false}
# States define which token IDs are legal; illegal logits -> -inf.
VOCAB = ['{', '"ok"', ':', 'true', 'false', '}']
TRANSITIONS = {0:[0], 1:[1], 2:[2], 3:[3,4], 4:[5]}  # state -> legal token idxs

def constrained_decode(logits_fn):
    out, state = [], 0
    order = [0,1,2,3,4]              # positions to fill
    for step in order:
        logits = logits_fn(out).astype(float)
        legal = TRANSITIONS[step]
        mask = np.full_like(logits, -np.inf)
        mask[legal] = logits[legal]  # keep only legal tokens
        tok = int(mask.argmax())     # greedy over legal tokens
        out.append(tok)
    return "".join(VOCAB[t] for t in out)

# fake model: prefers 'false' at the value step
def fake_logits(prefix): 
    z = np.zeros(len(VOCAB)); z[4] = 5; z[3] = 3; return z
print(constrained_decode(fake_logits))   # always valid: {"ok":false}
```


Related: [[04 Code Snippets/LLM/Validate and Repair Loop for JSON Output]]
