# Generated SQL Is Untrusted Input Not a Trusted Query

**A model-generated SQL query is the model's "arguments" for a tool call, not a trusted statement to execute as-is.** Parse it, confirm it only touches an allowlisted set of tables/columns, reject anything that isn't a read unless writes are explicitly authorized, and execute it through read-only, row-limited credentials regardless of what the validator catches.

> One-liner: validate the generated query like any other untrusted tool argument, then enforce the same boundary again at the database connection — a parsing-based gate can have gaps, so the execution layer needs its own independent guardrail.

Related: [[02 Literature Notes/LLM Engineering/Tool and Function Calling]]
