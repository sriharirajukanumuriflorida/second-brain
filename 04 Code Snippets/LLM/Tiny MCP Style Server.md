# Tiny MCP Style Server

> Domain 5 · MCP (Model Context Protocol). Expose resources tools and prompts

```python
class Server:
    resources={"file://note":"hello"}
    tools={"echo":lambda text:text.upper()}
    prompts={"summarize":"Summarize resource"}
    def list(self): return {"resources":list(self.resources),"tools":list(self.tools),"prompts":list(self.prompts)}
print(Server().list())
```


Related: [[04 Code Snippets/LLM/MCP Client Call Sketch]]
