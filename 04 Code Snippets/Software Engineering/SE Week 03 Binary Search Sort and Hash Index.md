# SE Week 03 Binary Search Sort and Hash Index

> Week 03 · Data Structures, Algorithms & Complexity. Compare linear scan, binary search over sorted data, and a hash-map index for repeated lookup.

```python
from bisect import bisect_left

rows = [("u3", "Chen"), ("u1", "Ada"), ("u4", "Diaz"), ("u2", "Grace")]

def linear_find(rows, user_id):
    for uid, name in rows:
        if uid == user_id:
            return name
    return None

sorted_rows = sorted(rows)
ids = [uid for uid, _ in sorted_rows]

def binary_find(user_id):
    i = bisect_left(ids, user_id)
    if i < len(ids) and ids[i] == user_id:
        return sorted_rows[i][1]
    return None

index = dict(rows)
print(linear_find(rows, "u2"), binary_find("u2"), index["u2"])
print("one-off tiny input: scan is fine; repeated lookup: build an index")
```


Related: [[03 Permanent Notes/SE Week 03 Big-O Complexity Cheat Sheet]]
