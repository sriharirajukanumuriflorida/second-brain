# Validated Function Call Executor

> Domain 5 · Tool / Function Calling. Validate args before invoking allowlisted tools

```python
def add(a,b): return a+b
TOOLS={"add":({"a":int,"b":int},add)}
def run(call):
    schema,fn=TOOLS[call["name"]]
    args=call["arguments"]
    for k,t in schema.items():
        if not isinstance(args.get(k),t): raise TypeError(k)
    return fn(**args)
print(run({"name":"add","arguments":{"a":2,"b":3}}))
```


Related: [[04 Code Snippets/LLM/Structured Tool Error Return]]
