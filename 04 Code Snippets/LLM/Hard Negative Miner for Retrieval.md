# Hard Negative Miner for Retrieval

> Domain 7 · Embedding-Model Fine-Tuning. Select the most similar non-positive document as a hard negative.

```python
import numpy as np
scores=np.array([[.9,.7,.2],[.1,.8,.75]])
positives=[0,1]
for i,row in enumerate(scores):
    row=row.copy(); row[positives[i]]=-1
    print("hard negative", int(row.argmax()))
```


Related: [[04 Code Snippets/LLM/In Batch Negative Contrastive Loss]]
