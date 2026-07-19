# In Batch Negative Contrastive Loss

> Domain 7 · Embedding-Model Fine-Tuning. Compute MNRL-style cross entropy over a cosine similarity matrix.

```python
import numpy as np
def normalize(x): return x/np.linalg.norm(x,axis=1,keepdims=True)
A=normalize(np.array([[1,0],[0,1],[1,1.]],float)); P=normalize(np.array([[.9,.1],[.1,.9],[.8,.7]],float))
sim=A@P.T; exp=np.exp(sim/.1); prob=exp/exp.sum(1,keepdims=True); loss=-np.log(np.diag(prob)).mean(); print(round(float(loss),3))
```


Related: [[04 Code Snippets/LLM/Hard Negative Miner for Retrieval]]
