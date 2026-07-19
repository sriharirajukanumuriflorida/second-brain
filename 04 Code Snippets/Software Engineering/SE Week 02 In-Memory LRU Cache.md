# SE Week 02 In-Memory LRU Cache

> Week 02 · System Design Fundamentals. A tiny LRU cache showing eviction, hit/miss accounting, and cache-aside usage.

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key, loader):
        if key in self.data:
            self.hits += 1
            self.data.move_to_end(key)
            return self.data[key]
        self.misses += 1
        value = loader(key)
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)
        return value

cache = LRUCache(capacity=2)
load = lambda key: f"value-for-{key}"
for key in ["a", "b", "a", "c", "b"]:
    print(key, "->", cache.get(key, load), "keys=", list(cache.data))
print("hits", cache.hits, "misses", cache.misses)
```


Related: [[03 Permanent Notes/SE Week 02 Caching Strategies and Invalidation]]
