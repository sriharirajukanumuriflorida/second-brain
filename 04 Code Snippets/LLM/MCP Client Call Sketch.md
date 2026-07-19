# MCP Client Call Sketch

> Domain 5 · MCP (Model Context Protocol). Invoke a discovered server tool

```python
srv=Server()
def call_tool(name,args):
    if name not in srv.tools: raise ValueError("unknown")
    return srv.tools[name](**args)
print(call_tool("echo", {"text":"mcp"}))
```


Related: [[04 Code Snippets/LLM/Tiny MCP Style Server]]
