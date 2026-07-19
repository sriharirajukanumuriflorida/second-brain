# SE Week 03+ Bloom Filter False Positive Demo

> Week 03+ · Applied Data Structures for Backend and AI. A small Bloom filter with double hashing and an empirical false-positive rate compared to the theoretical formula.

```python
import hashlib, math, random

class BloomFilter:
    def __init__(self, bits, hashes):
        self.bits = bits
        self.hashes = hashes
        self.array = bytearray((bits + 7) // 8)

    def _indexes(self, item):
        digest = hashlib.sha256(str(item).encode()).digest()
        h1 = int.from_bytes(digest[:8], 'big')
        h2 = int.from_bytes(digest[8:16], 'big') or 1
        for i in range(self.hashes):
            yield (h1 + i * h2) % self.bits

    def add(self, item):
        for idx in self._indexes(item):
            self.array[idx // 8] |= 1 << (idx % 8)

    def __contains__(self, item):
        return all(self.array[idx // 8] & (1 << (idx % 8)) for idx in self._indexes(item))

n, m, k = 5_000, 80_000, 7
bf = BloomFilter(bits=m, hashes=k)
for i in range(n):
    bf.add(f'user:{i}')

trials = 20_000
false_pos = sum(1 for i in range(n, n + trials) if f'user:{i}' in bf)
empirical = false_pos / trials
theoretical = (1 - math.exp(-k * n / m)) ** k
print(f'empirical={empirical:.4f} theoretical={theoretical:.4f}')
print('false negatives:', sum(1 for i in range(n) if f'user:{i}' not in bf))
```


Related: [[03 Permanent Notes/SE Week 03+ Probabilistic Data Structures Cheat Sheet]]
