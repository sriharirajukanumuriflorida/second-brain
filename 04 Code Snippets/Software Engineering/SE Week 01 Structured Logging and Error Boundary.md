# SE Week 01 Structured Logging and Error Boundary

> Week 01 · Software Engineering Refresh. Wrap an application boundary with typed errors, exception chaining, and structured JSON logs.

```python
import json, logging, sys

class PaymentDeclined(Exception):
    pass

class GatewayUnavailable(Exception):
    pass

logger = logging.getLogger("checkout")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers[:] = [handler]

def log_event(event, **fields):
    logger.info(json.dumps({"event": event, **fields}, sort_keys=True))

def charge_gateway(amount_cents):
    if amount_cents <= 0:
        raise PaymentDeclined("amount must be positive")
    if amount_cents == 503:
        raise TimeoutError("gateway timed out")
    return {"auth_code": "OK123"}

def checkout(request_id, amount_cents):
    try:
        result = charge_gateway(amount_cents)
        log_event("checkout.succeeded", request_id=request_id, amount_cents=amount_cents)
        return result
    except PaymentDeclined:
        log_event("checkout.declined", request_id=request_id, amount_cents=amount_cents)
        raise
    except TimeoutError as exc:
        log_event("checkout.gateway_unavailable", request_id=request_id, error_type=type(exc).__name__)
        raise GatewayUnavailable("payment gateway unavailable") from exc

print(checkout("req-1", 2500))
try:
    checkout("req-2", 503)
except GatewayUnavailable as exc:
    print(type(exc).__name__, "caused by", type(exc.__cause__).__name__)
```


Related: [[03 Permanent Notes/SE Week 01 Testing Pyramid and Delivery Strategy]]
