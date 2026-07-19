# Distillation KL Between Toy Distributions

> Domain 7 · Distillation & Small-Model Strategies. Minimize KL from teacher probabilities to student probabilities.

```python
import numpy as np
def softmax(z,T=1):
    z=np.array(z)/T; e=np.exp(z-z.max()); return e/e.sum()
teacher=softmax([4,2,0],T=2); student=softmax([2,1,1],T=2)
kl=float(np.sum(teacher*(np.log(teacher)-np.log(student))))
print(round(kl,4))
```


Related: [[04 Code Snippets/LLM/Small Model Escalation Router]]
