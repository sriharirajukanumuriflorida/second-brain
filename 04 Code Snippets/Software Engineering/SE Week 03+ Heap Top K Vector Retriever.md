# SE Week 03+ Heap Top K Vector Retriever

> Week 03+ · Applied Data Structures for Backend and AI. Use heapq.nlargest over numpy similarity scores so retrieval keeps only k winners instead of sorting every candidate.

```python
import heapq
import numpy as np

rng = np.random.default_rng(7)
doc_ids = np.array([f'doc-{i}' for i in range(50_000)])
scores = rng.random(len(doc_ids))
k = 5

def topk_heap(ids, scores, k):
    pairs = zip(scores.tolist(), ids.tolist())
    return [(doc_id, score) for score, doc_id in heapq.nlargest(k, pairs)]

def topk_sort(ids, scores, k):
    order = np.argsort(scores)[-k:][::-1]
    return [(ids[i], float(scores[i])) for i in order]

heap_result = topk_heap(doc_ids, scores, k)
sort_result = topk_sort(doc_ids, scores, k)
print(heap_result)
print('same ids:', [d for d, _ in heap_result] == [d for d, _ in sort_result])
print('heap keeps O(k) winners; full sort orders all n candidates')
```


Related: [[03 Permanent Notes/SE Week 03+ B-Tree vs LSM-Tree Decision Guide]]
