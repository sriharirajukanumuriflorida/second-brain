# LoRA Forward Pass in Numpy

> Domain 7 · LoRA / QLoRA / PEFT. Compute `W x + (alpha/r) B A x`.

```python
import numpy as np
rng=np.random.RandomState(0)
W=rng.normal(size=(4,5)); A=rng.normal(scale=.02,size=(2,5)); B=rng.normal(scale=.02,size=(4,2)); x=rng.normal(size=5)
y=W@x+(8/2)*(B@(A@x))
print(np.round(y,3))
```


Related: [[04 Code Snippets/LLM/LoRA Parameter Savings Calculator]]
