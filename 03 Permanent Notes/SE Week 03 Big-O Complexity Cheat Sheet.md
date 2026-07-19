# SE Week 03 Big-O Complexity Cheat Sheet

Big-O is a growth vocabulary for engineering budgets.

- `O(1)`: constant lookup or push when the structure supports it.
- `O(log n)`: repeated halving, as in binary search or balanced trees.
- `O(n)`: one full scan.
- `O(n log n)`: typical comparison sorting.
- `O(n^2)`: all pairs or nested scans.
- `O(V+E)`: graph traversal over vertices and edges.

Always pair time complexity with space complexity and constants. A hash map may make lookup average `O(1)` but spends memory; sorting may cost `O(n log n)` upfront but enables many cheap searches. Big-O rejects designs that cannot grow; benchmarking verifies the current scale.

> One-liner: **Big-O tells you how pain scales; profiling tells you where pain is today.**


Related: [[02 Literature Notes/Software Engineering/Data Structures, Algorithms & Complexity]] · [[04 Code Snippets/Software Engineering/SE Week 03 Binary Search Sort and Hash Index]]
