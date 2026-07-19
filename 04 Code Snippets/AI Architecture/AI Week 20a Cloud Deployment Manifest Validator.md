# AI Week 20a Cloud Deployment Manifest Validator

> Week 20a · Cloud Architecture & Deployment — Reference Patterns. A Pydantic v2 Azure Container Apps-style manifest validator that rejects unsafe secrets, impossible replica bounds, malformed memory values, and invalid probe paths before apply.

```python
import re
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

MEMORY_RE = re.compile(r'^(128|256|512)Mi$|^[1-9][0-9]*Gi$')

class Probe(BaseModel):
    model_config = ConfigDict(extra='forbid')
    path: str
    initial_delay_seconds: int = Field(default=5, ge=0, le=120)
    period_seconds: int = Field(default=10, ge=1, le=60)
    @field_validator('path')
    @classmethod
    def valid_path(cls, value):
        if not value.startswith('/') or ' ' in value or '?' in value:
            raise ValueError('probe path must be an absolute path without spaces or query string')
        return value

class ScaleRule(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    type: str
    metadata: dict[str, str] = Field(default_factory=dict)

class DeploymentManifest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(pattern=r'^[a-z][a-z0-9-]{2,40}$')
    image: str
    tag: str
    cpu: float = Field(gt=0, le=4)
    memory: str
    replicas: int = Field(ge=0, le=50)
    min_replicas: int = Field(alias='minReplicas', ge=0, le=50)
    max_replicas: int = Field(alias='maxReplicas', ge=1, le=100)
    ingress: bool = True
    env: dict[str, str] = Field(default_factory=dict)
    secret_refs: dict[str, str] = Field(default_factory=dict, alias='secretRefs')
    liveness: Probe
    readiness: Probe
    scale_rules: list[ScaleRule] = Field(default_factory=list, alias='scaleRules')
    @field_validator('memory')
    @classmethod
    def memory_shape(cls, value):
        if not MEMORY_RE.match(value):
            raise ValueError('memory must look like 256Mi, 512Mi, 1Gi, 2Gi, ...')
        return value
    @model_validator(mode='after')
    def cross_checks(self):
        if self.min_replicas > self.max_replicas:
            raise ValueError('minReplicas must be <= maxReplicas')
        if self.replicas and not (self.min_replicas <= self.replicas <= self.max_replicas):
            raise ValueError('replicas must be between minReplicas and maxReplicas')
        suspicious = ('KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'CONNECTION_STRING')
        for key, value in self.env.items():
            if any(word in key.upper() for word in suspicious) or value.lower().startswith(('sk-', 'eyj', 'postgres://')):
                raise ValueError(f'{key} belongs in secretRefs, not env')
        for name, ref in self.secret_refs.items():
            if not ref.startswith('keyvault:') or '=' in ref:
                raise ValueError(f'secretRef {name} must reference keyvault:<secret-name>')
        return self

good = {'name':'rag-api-prod','image':'acr.azurecr.io/rag-api','tag':'2026.07.18.shaabc','cpu':1.0,'memory':'2Gi','replicas':2,'minReplicas':1,'maxReplicas':10,'ingress':True,'env':{'ENVIRONMENT':'prod','PROMPT_VERSION':'rag-v12'},'secretRefs':{'AZURE_OPENAI_KEY':'keyvault:aoai-key','DB_PASSWORD':'keyvault:pg-password'},'liveness':{'path':'/healthz'},'readiness':{'path':'/readyz'},'scaleRules':[{'name':'http','type':'http','metadata':{'concurrentRequests':'50'}}]}
print('accepted:', DeploymentManifest.model_validate(good).name)
for label, patch in [('raw secret in env', {'env': {'AZURE_OPENAI_KEY': 'sk-live-secret'}}), ('min > max', {'minReplicas': 8, 'maxReplicas': 3, 'replicas': 4}), ('bad probe path', {'readiness': {'path': 'ready now'}})]:
    try:
        DeploymentManifest.model_validate({**good, **patch})
    except ValidationError as exc:
        print('rejected', label, '->', exc.errors()[0]['msg'])
```


Related: [[03 Permanent Notes/AI Week 20a Container and Kubernetes Cheat Sheet for AI Services]]
