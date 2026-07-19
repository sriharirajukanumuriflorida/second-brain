# SE Week 04+ FastAPI JWT Rate Limit Idempotency Demo

> Week 04+ · Production API and Backend Patterns. A real in-process FastAPI app using Pydantic v2 models, JWT auth, tenant rate limits, and an Idempotency-Key middleware exercised by TestClient.

```python
import json, time
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
import jwt

SECRET = 'dev-secret'
AUDIENCE = 'llm-jobs-api'
app = FastAPI(title='Production API Demo')
bearer = HTTPBearer()
idempotency_store = {}
rate_state = {}

class JobCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    prompt: str = Field(min_length=1, max_length=500)
    tenant_id: str = Field(pattern='^[a-z0-9-]+$')

class JobOut(BaseModel):
    job_id: str
    status: str

async def principal(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        claims = jwt.decode(creds.credentials, SECRET, algorithms=['HS256'], audience=AUDIENCE)
    except jwt.PyJWTError as exc:
        raise HTTPException(401, 'invalid token') from exc
    if 'jobs:write' not in claims.get('scope', '').split():
        raise HTTPException(403, 'missing jobs:write')
    return claims

async def rate_limit(claims=Depends(principal)):
    tenant = claims['tenant']
    limit = 3
    used = rate_state.get(tenant, 0)
    if used >= limit:
        raise HTTPException(429, 'rate limited', headers={'X-RateLimit-Limit': str(limit), 'X-RateLimit-Remaining': '0'})
    rate_state[tenant] = used + 1
    return claims

@app.middleware('http')
async def idempotency(request: Request, call_next):
    key = request.headers.get('Idempotency-Key')
    if request.method != 'POST' or not key:
        return await call_next(request)
    body = await request.body()
    cache_key = (request.url.path, key, body)
    if cache_key in idempotency_store:
        status, headers, payload = idempotency_store[cache_key]
        return JSONResponse(payload, status_code=status, headers={**headers, 'Idempotency-Replayed': 'true'})
    response = await call_next(request)
    chunks = [chunk async for chunk in response.body_iterator]
    payload = json.loads(b''.join(chunks) or b'{}')
    idempotency_store[cache_key] = (response.status_code, dict(response.headers), payload)
    return JSONResponse(payload, status_code=response.status_code, headers=dict(response.headers))

@app.post('/jobs', response_model=JobOut, status_code=202)
def create_job(req: JobCreate, claims=Depends(rate_limit)):
    if req.tenant_id != claims['tenant']:
        raise HTTPException(403, 'wrong tenant')
    return JobOut(job_id='job-1', status='queued')

token = jwt.encode({'sub': 'svc-1', 'tenant': 'acme', 'aud': AUDIENCE, 'scope': 'jobs:write', 'exp': int(time.time()) + 300}, SECRET, algorithm='HS256')
client = TestClient(app)
headers = {'Authorization': f'Bearer {token}', 'Idempotency-Key': 'abc'}
print(client.post('/jobs', json={'prompt':'index docs','tenant_id':'acme'}, headers=headers).json())
print(client.post('/jobs', json={'prompt':'index docs','tenant_id':'acme'}, headers=headers).headers.get('Idempotency-Replayed'))
```


Related: [[03 Permanent Notes/SE Week 04+ Production API Design Checklist]]
