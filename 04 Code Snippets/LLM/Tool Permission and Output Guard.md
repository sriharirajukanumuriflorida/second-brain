# Tool Permission and Output Guard

> Domain 9 · Guardrail Frameworks & Indirect Prompt Injection. Authorize proposed tool calls outside the model and block sensitive generated output.

```python
ALLOWED_TOOLS = {
    "analyst": {"search_docs", "summarize"},
    "admin": {"search_docs", "summarize", "delete_doc"},
}
SENSITIVE_OUTPUT = ["api_key", "password", "BEGIN RSA PRIVATE KEY", "system prompt"]

def authorize_tool(user, tool, args):
    if tool not in ALLOWED_TOOLS.get(user["role"], set()):
        return False, f"{user['role']} cannot call {tool}"
    if tool == "delete_doc" and not args.get("ticket"):
        return False, "destructive action requires ticket"
    return True, "ok"

def guard_output(text):
    lowered = text.lower()
    if any(s.lower() in lowered for s in SENSITIVE_OUTPUT):
        return "[BLOCKED: sensitive output]"
    return text

user = {"id":"u7", "role":"analyst"}
print(authorize_tool(user, "delete_doc", {"doc":"x"}))
print(guard_output("The password is hunter2"))
```


Related: [[04 Code Snippets/LLM/Indirect Prompt Injection Detector]]
