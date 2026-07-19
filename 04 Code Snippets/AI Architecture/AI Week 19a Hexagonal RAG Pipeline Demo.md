# AI Week 19a Hexagonal RAG Pipeline Demo

> Week 19a · AI Solution Architecture — Reference Patterns. A port-and-adapter RAG pipeline with fake in-memory LLM, embedding, vector store, reranker, guardrail, and eval recorder implementations.

```python
from typing import Protocol
import numpy as np

class LLMProvider(Protocol):
    def complete(self, prompt: str) -> str: ...
class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> np.ndarray: ...
class VectorStore(Protocol):
    def add(self, doc_id: str, text: str, vector: np.ndarray): ...
    def search(self, vector: np.ndarray, k: int = 3) -> list[dict]: ...
class Reranker(Protocol):
    def rerank(self, query: str, docs: list[dict]) -> list[dict]: ...
class Guardrail(Protocol):
    def check(self, text: str) -> str: ...
class EvalRecorder(Protocol):
    def record(self, event: dict): ...

class FakeEmbedder:
    def embed(self, text: str) -> np.ndarray:
        words = set(text.lower().split())
        return np.array([len(words), int('refund' in words), int('policy' in words), int('password' in words)], dtype=float)

class MemoryVectorStore:
    def __init__(self): self.rows = []
    def add(self, doc_id, text, vector): self.rows.append({'id': doc_id, 'text': text, 'vector': vector})
    def search(self, vector, k=3):
        def score(row):
            denom = np.linalg.norm(vector) * np.linalg.norm(row['vector']) or 1.0
            return float(np.dot(vector, row['vector']) / denom)
        return sorted(({**r, 'score': score(r)} for r in self.rows), key=lambda r: r['score'], reverse=True)[:k]

class KeywordReranker:
    def rerank(self, query, docs):
        terms = set(query.lower().split())
        return sorted(docs, key=lambda d: len(terms & set(d['text'].lower().split())), reverse=True)

class SimpleGuardrail:
    def check(self, text):
        if 'ignore previous instructions' in text.lower():
            return 'REFUSE: prompt injection detected'
        return text

class FakeLLM:
    def complete(self, prompt):
        return 'Answer grounded in cited policy: refunds are allowed within 30 days. [doc:refund-policy]'

class ListEvalRecorder:
    def __init__(self): self.events = []
    def record(self, event): self.events.append(event)

class RAGPipeline:
    def __init__(self, llm, embedder, store, reranker, guardrail, evals):
        self.llm = llm; self.embedder = embedder; self.store = store; self.reranker = reranker; self.guardrail = guardrail; self.evals = evals
    def ingest(self, doc_id, text):
        clean = self.guardrail.check(text)
        self.store.add(doc_id, clean, self.embedder.embed(clean))
        self.evals.record({'stage': 'ingest', 'doc_id': doc_id})
    def answer(self, query):
        checked = self.guardrail.check(query)
        docs = self.reranker.rerank(checked, self.store.search(self.embedder.embed(checked)))
        context = '\n'.join(f"[{d['id']}] {d['text']}" for d in docs)
        response = self.llm.complete(f'Use only cited context.\n{context}\nQuestion: {checked}')
        self.evals.record({'stage': 'answer', 'query': query, 'docs': [d['id'] for d in docs]})
        return response

recorder = ListEvalRecorder()
pipeline = RAGPipeline(FakeLLM(), FakeEmbedder(), MemoryVectorStore(), KeywordReranker(), SimpleGuardrail(), recorder)
pipeline.ingest('doc:refund-policy', 'Refund policy allows refunds within 30 days with receipt.')
pipeline.ingest('doc:password-policy', 'Password policy requires MFA for administrators.')
print(pipeline.answer('What is the refund policy?'))
print([e['stage'] for e in recorder.events])
```


Related: [[03 Permanent Notes/AI Week 19a Reference AI Architectures Catalog]]
