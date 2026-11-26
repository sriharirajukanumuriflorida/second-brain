# A Right Answer Can Hide A Broken Trajectory

**Score a multi-step agent at response, step, and trajectory level, not response-level alone.** An agent can reach the correct final answer via a wrong tool call that happened not to matter, or via a redundant, inefficient path — both look identical to a pass under response-level scoring alone.

> One-liner: response-level scoring only sees the end result; step-level catches a bad individual action; trajectory-level catches a bad overall path made of individually-valid steps.

Related: [[02 Literature Notes/LLM Engineering/Eval Fundamentals]] · [[02 Literature Notes/LLM Engineering/Agent Loops and Planning]]
