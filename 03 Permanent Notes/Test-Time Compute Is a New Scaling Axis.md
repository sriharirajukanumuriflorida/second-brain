# Test-Time Compute Is a New Scaling Axis

Beyond training bigger models, you can improve accuracy by **spending more compute at inference** — longer chains-of-thought, sampling many chains (self-consistency), or searching over reasoning states with a verifier. For hard, multi-step problems this reliably raises accuracy, and can let a smaller model beat a larger one. Reasoning models (o1/o3, DeepSeek-R1) bake this in via RL, learning to think at length before answering.

The catch: it's a *dial*, not free — latency and token cost scale with thinking, and easy tasks get little or no benefit.

> One-liner: **think longer to answer better** — inference compute is now a tunable accuracy lever, best spent on the hard minority.


Related: [[02 Literature Notes/LLM Engineering/Reasoning Models]] · [[03 Permanent Notes/Match Compute to Difficulty]]
