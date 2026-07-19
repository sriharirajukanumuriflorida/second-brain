# Benchmark Contamination Probe

> Domain 6 · Benchmark Literacy. N-gram overlap probe for suspected benchmark memorization in local corpora.

```python
def ngrams(text, n=5):
    w=text.lower().split()
    return {tuple(w[i:i+n]) for i in range(max(0, len(w)-n+1))}
def overlap_probe(item, corpus_docs, n=5):
    target=ngrams(item,n); hits=[]
    for name, doc in corpus_docs.items():
        ov=len(target & ngrams(doc,n))
        if ov: hits.append((name, ov))
    return sorted(hits, key=lambda x:x[1], reverse=True)
print(overlap_probe("solve the refund policy word problem carefully", {"doc":"refund policy word problem carefully appears here"}, n=3))
```


Related: [[02 Literature Notes/LLM Engineering/Benchmark Literacy]]
