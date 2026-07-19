# A Prompt Is an API Contract Not a Sentence

Production prompts should be designed like API contracts: a stable structure with defined inputs, outputs, and error behavior — not prose you tweak by feel. Use message **roles** deliberately (system = identity + hard rules, developer = task + schema, user = runtime data), **pin an output schema** you can validate, provide **few-shot exemplars** for format and edge cases, and specify a **refusal path** for the unhappy case. Wrap untrusted content as data and assert precedence.

When the contract is explicit, the model behaves like a component you can build software on, and its behavior becomes versionable and testable.

> One-liner: **design prompts as interfaces** — roles, schema, examples, refusal — and the LLM stops being a slot machine.


Related: [[02 Literature Notes/LLM Engineering/Prompt Contracts]] · [[02 Literature Notes/LLM Engineering/Structured Generation]]
