# AI Week 19b One Page Architecture Generator

> Week 19b · AI Solution Architecture — Applied. Pydantic v2 model tree for an enterprise AI architecture, rendering a Markdown one-pager and Mermaid C4 Container diagram for the insurance-underwriter scenario.

```python
from pydantic import BaseModel, Field

class Container(BaseModel):
    name: str
    kind: str
    technology: str
    responsibility: str

class Integration(BaseModel):
    source: str
    target: str
    description: str

class ADR(BaseModel):
    title: str
    context: str
    decision: str
    consequences: str
    alternatives_rejected: list[str]

class Risk(BaseModel):
    failure_mode: str
    mitigation: str

class Capacity(BaseModel):
    users: int
    questions_per_user_day: int
    prompt_tokens: int
    response_tokens: int
    vector_storage_gb: float
    monthly_llm_cost_usd: float

class Architecture(BaseModel):
    title: str
    context: str
    containers: list[Container] = Field(default_factory=list)
    integrations: list[Integration] = Field(default_factory=list)
    adrs: list[ADR] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    capacity: Capacity


def render_mermaid(arch: Architecture) -> str:
    aliases = {c.name: f"c{i}" for i, c in enumerate(arch.containers, 1)}
    lines = ["C4Container", f"    title {arch.title}", "    Person(u, \"Underwriter\", \"Uses embedded AI panel\")", "    System_Boundary(s, \"Insurance Azure tenant\") {"]
    for c in arch.containers:
        lines.append(f"      Container({aliases[c.name]}, \"{c.name}\", \"{c.technology}\", \"{c.responsibility}\")")
    lines.append("    }")
    lines.append(f"    Rel(u, {aliases['Underwriter Web App']}, \"asks question\")")
    for integ in arch.integrations:
        if integ.source in aliases and integ.target in aliases:
            lines.append(f"    Rel({aliases[integ.source]}, {aliases[integ.target]}, \"{integ.description}\")")
    return "\n".join(lines)


def render_one_pager(arch: Architecture) -> str:
    out = [f"# {arch.title}", "", "## Context", arch.context, "", "## Containers"]
    for c in arch.containers:
        out.append(f"- **{c.name}** ({c.technology}): {c.responsibility}")
    out += ["", "## Mermaid", "```mermaid", render_mermaid(arch), "```", "", "## ADRs"]
    for adr in arch.adrs:
        out.append(f"- **{adr.title}**: {adr.decision} Consequences: {adr.consequences}")
    out += ["", "## Risks"]
    for r in arch.risks:
        out.append(f"- **{r.failure_mode}** -> {r.mitigation}")
    cap = arch.capacity
    out += ["", "## Capacity", f"{cap.users} users x {cap.questions_per_user_day} questions/day, {cap.prompt_tokens}+{cap.response_tokens} tokens/query, vector storage about {cap.vector_storage_gb:.2f} GB, monthly LLM cost about ${cap.monthly_llm_cost_usd:,.0f}."]
    return "\n".join(out)

arch = Architecture(
    title="Insurance Underwriting RAG Assistant",
    context="Assistant embedded in the underwriter web app answers policy, memo, and regulatory questions with citations, auditability, and Azure-only data handling.",
    containers=[
        Container(name="Underwriter Web App", kind="web", technology="Existing app", responsibility="Embedded AI panel and feedback"),
        Container(name="AI Assistant API", kind="api", technology="FastAPI", responsibility="AuthZ, retrieval, prompt assembly, streaming"),
        Container(name="Prompt Registry", kind="config", technology="Git", responsibility="Versioned prompts and schemas"),
        Container(name="Azure Postgres pgvector", kind="db", technology="Postgres", responsibility="Chunks, embeddings, metadata filters"),
        Container(name="Azure OpenAI GPT-4o", kind="model", technology="Azure OpenAI", responsibility="Grounded answer generation"),
        Container(name="Audit Log", kind="storage", technology="Blob Storage", responsibility="Immutable prompt, chunks, answer, trace id"),
    ],
    integrations=[
        Integration(source="Underwriter Web App", target="AI Assistant API", description="HTTPS question with user token"),
        Integration(source="AI Assistant API", target="Prompt Registry", description="load prompt version"),
        Integration(source="AI Assistant API", target="Azure Postgres pgvector", description="retrieve cited chunks"),
        Integration(source="AI Assistant API", target="Azure OpenAI GPT-4o", description="generate answer"),
        Integration(source="AI Assistant API", target="Audit Log", description="write audit event"),
    ],
    adrs=[ADR(title="Use RAG first", context="Documents change weekly", decision="RAG with citations before fine-tuning", consequences="Fresh and auditable; retrieval quality matters", alternatives_rejected=["fine-tune only"])],
    risks=[Risk(failure_mode="Provider outage", mitigation="Cached answers and human review fallback"), Risk(failure_mode="Low groundedness", mitigation="Refuse and escalate")],
    capacity=Capacity(users=50, questions_per_user_day=40, prompt_tokens=1500, response_tokens=800, vector_storage_gb=2.46, monthly_llm_cost_usd=517),
)
print(render_one_pager(arch))
```


Related: [[03 Permanent Notes/AI Week 19b Enterprise AI One-Pager Architecture Template]]
