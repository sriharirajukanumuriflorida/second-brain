# Structured Tool Error Return

> Domain 5 · Tool / Function Calling. Make tool failures legible to the model

```python
def safe_run(call):
    try: return {"ok":True,"result":run(call)}
    except Exception as e: return {"ok":False,"error":type(e).__name__,"message":str(e)}
print(safe_run({"name":"add","arguments":{"a":"2","b":3}}))
```


Related: [[04 Code Snippets/LLM/Validated Function Call Executor]]
