# LoRA Parameter Savings Calculator

> Domain 7 · LoRA / QLoRA / PEFT. Compare full dense update size with adapter size.

```python
def lora_params(din,dout,r):
    dense=din*dout; adapter=r*(din+dout); return dense,adapter,adapter/dense
for r in [4,8,16,64]:
    print(r, lora_params(4096,4096,r))
```


Related: [[04 Code Snippets/LLM/LoRA Forward Pass in Numpy]]
