# SE Week 03 Choosing the Right Data Structure

Choose data structures from access patterns, not habit. Use arrays/lists for compact ordered data and fast scans; hash maps/sets for membership and key lookup; stacks for LIFO control; queues for FIFO work and BFS; heaps for priority; trees for hierarchy and ordered operations; graphs for relationships.

The design question is: which operation dominates, how large can the data get, how often does it mutate, and what correctness constraints exist around duplicates, ordering, cycles, and staleness? Most speedups spend memory or preprocessing to make later operations cheaper.

> One-liner: **make the common operation cheap, then name what became expensive.**


Related: [[02 Literature Notes/Software Engineering/Data Structures, Algorithms & Complexity]] · [[04 Code Snippets/Software Engineering/SE Week 03 Graph BFS DFS Traversal]]
