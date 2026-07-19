# SE Week 04+ OpenTelemetry Retry With Jitter Demo

> Week 04+ · Production API and Backend Patterns. An in-process client shows exponential backoff with jitter across simulated 429/503 responses and captures spans locally.

```python
import random
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

exporter = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))
tracer = provider.get_tracer('retry-demo')

class FakeAPI:
    def __init__(self, statuses): self.statuses = list(statuses)
    def get(self): return self.statuses.pop(0) if self.statuses else 200

def call_with_retry(api, max_attempts=4, base=0.05, cap=1.0, rng=random.Random(4)):
    delays = []
    with tracer.start_as_current_span('client.request') as root:
        for attempt in range(max_attempts):
            with tracer.start_as_current_span('attempt') as span:
                status = api.get()
                span.set_attribute('http.status_code', status)
                span.set_attribute('retry.attempt', attempt)
                if status < 500 and status != 429:
                    root.set_attribute('final.status_code', status)
                    return status, delays
            if status not in (429, 502, 503, 504):
                return status, delays
            delays.append(rng.uniform(0, min(cap, base * (2 ** attempt))))
    return status, delays

status, delays = call_with_retry(FakeAPI([429, 503, 200]))
print(status, [round(d, 3) for d in delays], len(exporter.get_finished_spans()))
```


Related: [[03 Permanent Notes/SE Week 04+ OAuth2 OIDC and Token Patterns]]
