# FDE Week 24b Capstone Interview and Handoff Scripts

Reusable scripts for the final capstone conversation.

**90-second pitch:** I built an Enterprise AI SDLC Assistant that turns requirements documents into cited, schema-valid epics, features, PBIs, and tests. It targets Product/Engineering/QA leads who spend 3-5 days preparing backlog from PRDs. The measured goal is 4 hours, about $0.15/PBI all-in, and 90%+ groundedness on a 250-item golden set. The hardest part was preventing plausible but unsupported backlog items; I solved it with citations on every generated item, strict Pydantic schemas, human review, and eval gates. The main tradeoff was cutting automatic Jira submission from v1 to preserve trust.

**Three hardest problems:** overgenerated fluff PBIs; citation gaps at chunk boundaries; cost blowups on large docs. **Three tradeoffs:** Streamlit vs Next.js; bespoke RAG boundaries vs LangChain; Azure OpenAI vs direct OpenAI/Bedrock. **Three failure modes:** hallucinated tests, schema drift, biased eval set. **What I would do differently:** involve independent PM/QA reviewers earlier, automate rollback drills sooner, and create per-tenant cost attribution in v1 instead of v1.1.

**Demo walk-through:** setup: manual 40-page PRD decomposition; confrontation: 90-second cited schema-valid generation; resolution: reviewed backlog in 4 hours with eval/cost evidence and human-approved export.

> One-liner: **tell the capstone as outcome, evidence, hard problems, tradeoffs, failures, and handoff.**


Related: [[02 Literature Notes/FDE Delivery/Capstone FDE Portfolio Project — Applied]] · [[04 Code Snippets/FDE Delivery/FDE Week 24b Capstone Evaluation Harness Regression Report]]
