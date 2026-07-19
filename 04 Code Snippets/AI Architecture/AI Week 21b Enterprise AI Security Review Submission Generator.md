# AI Week 21b Enterprise AI Security Review Submission Generator

> Week 21b · Security, Governance & Responsible AI — Applied. Pydantic v2 SRBSubmission model tree that renders a full enterprise security review document for the insurance-underwriter Azure AI assistant, including OWASP LLM and STRIDE control rows.

```python
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Status = Literal['green', 'amber', 'red']

class SystemContext(BaseModel):
    name: str
    business_owner: str
    technical_owner: str
    purpose: str
    azure_topology: list[str]
    prohibited_uses: list[str]

class DataClass(BaseModel):
    field: str
    classification: Literal['public', 'internal', 'confidential', 'pii', 'sensitive']
    examples: str
    control: str

class ThreatRow(BaseModel):
    tag: str
    threat: str
    control: str
    owner: str
    evidence_link: str
    status: Status

class RiskAcceptance(BaseModel):
    risk: str
    residual_exposure: str
    approver: str
    expiry: str
    compensating_controls: list[str]

class Commitment(BaseModel):
    name: str
    owner: str
    evidence: str

class SRBSubmission(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str
    system_context: SystemContext
    data_classification: list[DataClass]
    trust_boundaries: list[str]
    threat_model_rows: list[ThreatRow] = Field(min_length=1)
    residual_risks: list[RiskAcceptance]
    monitoring_commitments: list[Commitment]
    incident_commitments: list[Commitment]

    def render_srb_markdown(self) -> str:
        lines = [f'# {self.title}', '', '## 1. System context']
        ctx = self.system_context
        lines += [f'- Name: {ctx.name}', f'- Business owner: {ctx.business_owner}', f'- Technical owner: {ctx.technical_owner}', f'- Purpose: {ctx.purpose}', '- Azure topology:']
        lines += [f'  - {item}' for item in ctx.azure_topology]
        lines += ['- Prohibited uses:'] + [f'  - {item}' for item in ctx.prohibited_uses]
        lines += ['', '## 2. Data classification', '| Field | Class | Examples | Control |', '|---|---|---|---|']
        for d in self.data_classification:
            lines.append(f'| {d.field} | {d.classification} | {d.examples} | {d.control} |')
        lines += ['', '## 3. Trust boundaries'] + [f'- {b}' for b in self.trust_boundaries]
        lines += ['', '## 4. Threat model and control matrix', '| Tag | Threat | Control | Owner | Evidence | Status |', '|---|---|---|---|---|---|']
        for row in self.threat_model_rows:
            lines.append(f'| {row.tag} | {row.threat} | {row.control} | {row.owner} | {row.evidence_link} | {row.status.upper()} |')
        lines += ['', '## 5. Residual risk and acceptance requests']
        for r in self.residual_risks:
            lines += [f'### {r.risk}', f'- Exposure: {r.residual_exposure}', f'- Approver: {r.approver}', f'- Expiry: {r.expiry}', '- Compensating controls:']
            lines += [f'  - {c}' for c in r.compensating_controls]
        lines += ['', '## 6. Monitoring commitments']
        for c in self.monitoring_commitments:
            lines.append(f'- **{c.name}** — owner: {c.owner}; evidence: {c.evidence}')
        lines += ['', '## 7. Incident response commitments']
        for c in self.incident_commitments:
            lines.append(f'- **{c.name}** — owner: {c.owner}; evidence: {c.evidence}')
        return '\n'.join(lines)

def build_submission() -> SRBSubmission:
    return SRBSubmission(
        title='SRB Submission — Insurance Underwriter AI Assistant',
        system_context=SystemContext(
            name='Underwriter AI Assistant', business_owner='Director of Underwriting', technical_owner='FDE + Azure Platform Team',
            purpose='Decision-support RAG assistant that summarizes authorized policy, memo, precedent, and regulatory evidence with citations.',
            azure_topology=['Azure Front Door Premium WAF', 'Azure Container Apps FastAPI RAG service with managed identity', 'Azure OpenAI over Private Endpoint with BYOK/CMK posture', 'Azure Database for PostgreSQL Flexible Server with pgvector, RLS, TDE and CMK', 'Blob Storage immutable WORM audit with CMK', 'Key Vault, Entra ID, Application Insights with redacted OTel spans'],
            prohibited_uses=['Bind coverage or approve exceptions autonomously', 'Deny a claim or change price without human judgment', 'Retrieve data outside user region/line entitlements', 'Write to Policy Admin without senior-underwriter approval']),
        data_classification=[
            DataClass(field='policy wording', classification='internal', examples='approved forms and endorsements', control='authorized retrieval, citations, source freshness'),
            DataClass(field='claimant/insured names', classification='pii', examples='Jane Doe, Robert Smith', control='[NAME] before embedding; prompt-side redaction'),
            DataClass(field='date of birth', classification='pii', examples='DOB 03/14/1980', control='[DOB] before embedding; output PII scan'),
            DataClass(field='policy and claim numbers', classification='pii', examples='PA-104455, CLM-99201', control='keyed hash for equality; mask in prompts/logs'),
            DataClass(field='medical notes in claims memos', classification='sensitive', examples='MRI, disability, injury description', control='minimize retrieval; senior-review route for sensitive answers'),
            DataClass(field='regulatory bulletins', classification='public', examples='published state filing updates', control='source integrity and freshness checks')],
        trust_boundaries=['Browser to Front Door over TLS 1.2+', 'Front Door to Container App private origin', 'Container App managed identity to Key Vault/Postgres/OpenAI/Blob/App Insights Private Endpoints', 'ACL-filtered retrieval to prompt boundary', 'Azure OpenAI output to JSON/PII/canary validation boundary', 'Blob audit and App Insights telemetry boundary'],
        threat_model_rows=[
            ThreatRow(tag='LLM01', threat='Direct prompt injection asks for system prompt or canary token', control='classifier, instruction hierarchy, canary-token check, refusal path', owner='AppSec/FDE', evidence_link='RT-01 direct injection eval', status='green'),
            ThreatRow(tag='LLM01', threat='Indirect injection hidden in poisoned policy PDF', control='PDF sanitizer, retrieved_untrusted wrapper, canary check, red-team fixture', owner='AppSec', evidence_link='RT-04 retest clean', status='green'),
            ThreatRow(tag='LLM02', threat='Model emits unsafe tool payload or malformed JSON', control='Pydantic schema validation and tool allowlist', owner='FDE', evidence_link='unit output_schema_gate', status='green'),
            ThreatRow(tag='LLM03', threat='Poisoned corpus chunk changes underwriting guidance', control='ingestion provenance, source owner approval, eval regression before index promotion', owner='Data Owner', evidence_link='index-2026-07-18 manifest', status='green'),
            ThreatRow(tag='LLM04', threat='Long-context DoS exhausts Azure OpenAI quota', control='Front Door WAF, per-user rate limits, max chunks/tokens, Week 22b cost alerts', owner='SRE', evidence_link='load test LT-21b', status='green'),
            ThreatRow(tag='LLM05', threat='Vulnerable container dependency or prompt package', control='Trivy scan, SBOM, signed ACR images, prompt registry approvals', owner='Platform', evidence_link='trivy-scan-2026-07-18', status='green'),
            ThreatRow(tag='LLM06', threat='Names/DOBs leak via embeddings', control='redact-before-embed with [NAME]/[DOB] and keyed hashes', owner='DPO/Data Eng', evidence_link='ingestion manifest pii-redaction', status='green'),
            ThreatRow(tag='LLM06', threat='Raw PII leaks into App Insights traces', control='redact-at-tracer boundary and sampled trace review', owner='SRE', evidence_link='trace sample audit AI-778', status='green'),
            ThreatRow(tag='LLM07', threat='Tool schema permits unauthorized Policy Admin updates', control='tool authorization catalog, exact schemas, HITL threshold', owner='Product Owner', evidence_link='tool-catalog-v3', status='amber'),
            ThreatRow(tag='LLM08', threat='Assistant takes excessive agency on regulated decision', control='decision-support UX, no autonomous binding, senior-underwriter approval for writes', owner='CRO', evidence_link='model card limitation section', status='green'),
            ThreatRow(tag='LLM09', threat='Junior underwriter overrelies on unsupported answer', control='citations, confidence, refusal, human review queue, training copy', owner='Underwriting Ops', evidence_link='UAT checklist', status='green'),
            ThreatRow(tag='LLM10', threat='Prompt/model extraction through repeated probes', control='auth, throttling, anomaly detection, no raw system prompt in logs', owner='CISO', evidence_link='Front Door WAF policy', status='green'),
            ThreatRow(tag='STRIDE-Spoofing', threat='Forged or wrong-audience Entra token', control='issuer/audience/expiry/scope validation and conditional access', owner='IAM', evidence_link='auth test jwt-aud', status='green'),
            ThreatRow(tag='STRIDE-Tampering', threat='Blob audit record or prompt manifest altered', control='immutable WORM Blob, CMK, hash chain, limited RBAC', owner='Platform', evidence_link='storage immutability policy', status='green'),
            ThreatRow(tag='STRIDE-DoS', threat='Front Door request flood or adversarial prompt expansion', control='WAF managed rules, rate limits, token budgets, circuit breaker', owner='SRE', evidence_link='WAF config FD-22', status='green')],
        residual_risks=[
            RiskAcceptance(risk='PII detector misses messy OCR medical note', residual_exposure='A sensitive fragment could reach the prompt despite redaction.', approver='DPO', expiry='2026-10-01', compensating_controls=['sensitive-document sampling', 'output PII scan', 'human review for medical-note answers']),
            RiskAcceptance(risk='Azure OpenAI abuse monitoring disabled', residual_exposure='Less provider-side abuse detection due to data residency requirement.', approver='CISO', expiry='2026-10-01', compensating_controls=['customer-side safety telemetry', 'canary-token detection', 'Front Door anomaly detection']),
            RiskAcceptance(risk='EU AI Act classification uncertainty', residual_exposure='Regulatory obligations may expand if system is deemed high-risk.', approver='CRO', expiry='2026-09-15', compensating_controls=['treat as high-risk posture', 'technical documentation', 'human oversight', 'post-market monitoring'])],
        monitoring_commitments=[Commitment(name='Hourly Week 22b golden canaries', owner='FDE/SRE', evidence='App Insights dashboard ai-canary'), Commitment(name='RLS bypass and retrieval anomaly alert', owner='Data Platform', evidence='KQL alert rls-deny spike'), Commitment(name='PII/canary output scan metrics', owner='AppSec', evidence='safety-flags dashboard')],
        incident_commitments=[Commitment(name='Suspected prompt injection security incident', owner='CISO/AppSec', evidence='runbook IR-LLM-01'), Commitment(name='PII exposure escalation to DPO', owner='DPO', evidence='privacy incident runbook'), Commitment(name='Prompt/model/index rollback lane', owner='FDE/SRE', evidence='Week 22b rollback drill')])

submission = build_submission()
print(submission.render_srb_markdown())
```


Related: [[03 Permanent Notes/AI Week 21b Enterprise AI Security Review Submission Template]]
