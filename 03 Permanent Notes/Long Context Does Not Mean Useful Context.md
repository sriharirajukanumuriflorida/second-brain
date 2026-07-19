# Long Context Does Not Mean Useful Context

A large context window is capacity, not quality. Irrelevant tokens can distract, raise cost, and bury the evidence the model needs. Liu et al.'s lost-in-the-middle result is the practical warning: facts near the middle of long contexts may be used less reliably than facts near the beginning or end.

The fix is selective assembly: retrieve fewer better chunks, order them intentionally, place critical evidence near attention-friendly positions, and summarize or deduplicate aggressively.

> One-liner: **more context is not better context; relevant, well-ordered context is better context.**


Related: [[02 Literature Notes/LLM Engineering/Context Engineering]] · [[04 Code Snippets/LLM/Lost In The Middle Probe]]
