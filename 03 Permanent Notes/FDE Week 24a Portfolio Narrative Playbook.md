# FDE Week 24a Portfolio Narrative Playbook

Use this to write the README top and prepare the capstone interview.

## 90-second README opening
1. **BLUF:** one-sentence business outcome and target user.
2. **Evidence table:** golden-set size, groundedness, hallucination rate, latency, cost/query, deploy status.
3. **Visual proof:** one GIF or screenshot plus a link to a three-minute video.
4. **Architecture:** generated C4 diagram near the top.
5. **Risk posture:** auth, PII/DLP, eval gate, risk register, known limitations.
6. **Run path:** `make setup && make test && make eval && make run`.

## Demo arc
- **Setup:** user's real pain and baseline metric.
- **Confrontation:** system handles a realistic hard case with citations, guardrails, trace, and UI/API proof.
- **Resolution:** measured outcome, eval result, cost, limitation, and next decision.

## Interview prep
Have ready: the five hardest problems you solved, the three tradeoffs you would revisit, the three ways the system fails, and the mitigation or roadmap item for each failure. Do not over-claim production readiness. Do not under-claim real value.

> One-liner: **tell the story as business claim, evidence, tradeoffs, failure modes, and handoff.**


Related: [[02 Literature Notes/FDE Delivery/Capstone FDE Portfolio Project — Reference Patterns]] · [[04 Code Snippets/FDE Delivery/FDE Week 24a Prompt Contract Eval Regression Renderer]]
