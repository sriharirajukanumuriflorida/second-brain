# SSE Token Streaming Demo

> Domain 8 · Inference & Serving (vLLM, TGI, batching, streaming). Format generated tokens as Server-Sent Event chunks without calling a real model.

```python
import json

def fake_decode(prompt):
    for tok in ["The", " answer", " streams", " token", " by", " token", "."]:
        yield tok

def sse_events(prompt):
    for token in fake_decode(prompt):
        yield "data: " + json.dumps({"token": token}) + "

"
    yield "data: [DONE]

"

for event in sse_events("Explain batching"):
    print(event.strip())
```


Related: [[04 Code Snippets/LLM/Continuous Batching Scheduler Simulator]]
