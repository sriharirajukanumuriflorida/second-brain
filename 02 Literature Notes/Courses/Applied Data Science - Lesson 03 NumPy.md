# Applied Data Science - Lesson 03 NumPy

## Source
- Course: Applied Data Science
- Lesson / Chapter: Lesson 03 - NumPy
- Resource: [[07 Resources Library/Applied Data Science/Slides/Lesson_03_Knowledge_Check.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Applied Data Science/Notebooks/3.01_Numpy_Introduction.ipynb]]
  - [[07 Resources Library/Applied Data Science/Notebooks/3.02_Attributes_and_Functions_in_Python.ipynb]]
  - [[07 Resources Library/Applied Data Science/Notebooks/3.03_NumPy_Arithmetic_Statistical_and_String_Functions.ipynb]]
  - [[07 Resources Library/Applied Data Science/Notebooks/3.04_Indexing.ipynb]]
  - [[07 Resources Library/Applied Data Science/Notebooks/3.05_Slicing.ipynb]]

## Summary
- Introduces NumPy for efficient numerical computing with arrays.
- Covers array creation, attributes, arithmetic, indexing, and slicing.

## Key Ideas
- The ndarray and why vectorized operations are fast.
- Arithmetic, statistical, and string functions over arrays.
- Indexing and slicing to access and manipulate array data.

## Important Details
- NumPy is the numerical foundation for Pandas and modeling libraries.
- Notebooks progress from basics to indexing and slicing.

## Questions
- Which NumPy concepts should become permanent notes?
- Which array idioms are worth saving as snippets?

## Interview Q&A

**Q: Why is a vectorized NumPy operation so much faster than the equivalent Python for-loop over a list?**
A: A Python for-loop over a list processes one element at a time, and for every single element, the interpreter has to do real work just to figure out "what type of object is this, what does `+` even mean for it" — this type-checking and dynamic dispatch overhead happens freshly on every iteration, because Python lists can hold arbitrarily different types of objects at every position, so the interpreter can't assume anything in advance.

A NumPy array, by contrast, stores elements of one fixed, known type in one contiguous block of memory. Because the type is fixed and known ahead of time, a vectorized operation (`array + 5`, `array1 * array2`) can skip the per-element type-checking overhead entirely and instead run as a tight, compiled loop in C — often further accelerated by CPU-level optimizations (SIMD instructions that apply one operation to multiple numbers simultaneously) that a general-purpose Python loop has no way to access.

The practical consequence: the speedup isn't from NumPy being "smarter" about the math — it's the same math — it's from eliminating the repeated, per-element interpretive overhead that a Python-level loop can't avoid, by doing the looping in compiled code operating over a uniform, contiguous block of memory instead.

*One-liner: a Python loop re-pays per-element type-checking overhead on every iteration because a list can hold mixed types; a NumPy array's fixed dtype and contiguous memory let the same operation run as a compiled C loop (with CPU-level parallelism) that never has to repeat that check — that eliminated overhead, not smarter math, is where the speedup comes from.*

**Q: What is broadcasting, and why does it let you write `array + 5` instead of writing a loop to add 5 to every element?**
A: Broadcasting is NumPy's rule for applying an operation between two arrays of *different* shapes by implicitly expanding the smaller one to match the larger one's shape, without actually copying any data to do it. `array + 5` is the simplest case: `5` is treated as if it were "stretched" into an array the same shape as `array`, so the addition can proceed element-wise, even though you only wrote one scalar value.

The reason this matters beyond convenience: broadcasting follows the same compiled, vectorized execution path as any other array operation — the "expansion" of the smaller array is conceptual/virtual (NumPy computes it without allocating the expanded version in memory), so you get the full speed benefit of vectorization without having to manually reshape or repeat data yourself. Without broadcasting, you'd either have to write a Python loop (losing the speed benefit) or manually construct a same-shaped array of 5s before adding (wasting memory and still being more code).

Broadcasting rules generalize beyond scalars too — a 1D array can broadcast against each row of a 2D array, which is what lets you do things like subtracting a per-column mean from every row of a dataset in one vectorized expression, instead of looping over rows.

*One-liner: broadcasting lets NumPy apply an operation between differently-shaped arrays by virtually (not literally) expanding the smaller one to match, so expressions like `array + 5` or "subtract this row from every row of a matrix" stay fully vectorized and fast, without you manually writing a loop or pre-building a same-shaped array yourself.*

**Q: What's the practical difference between slicing a NumPy array and indexing it with a boolean mask or a list of integers — why would you choose one over the other?**
A: Basic slicing (`array[2:5]`) selects a contiguous range by position and, critically, returns a *view* into the original array's memory — no data is copied, so modifying the slice modifies the original array too. This makes slicing extremely cheap, but it only works when what you want is expressible as a contiguous range (or a regular stride) of positions.

Boolean-mask indexing (`array[array > 10]`) and integer-array indexing (`array[[0, 3, 7]]`) are both forms of "fancy indexing," and they solve a different problem: selecting elements based on a *condition* or an *arbitrary, non-contiguous set of positions* — something a simple slice range can't express at all. The tradeoff is that fancy indexing always returns a *copy*, not a view, since the selected elements generally aren't contiguous in memory anymore and have to be gathered into a new array.

The practical choice, then, isn't really "which is faster" in isolation — it's "what are you actually trying to select." If the selection is a genuine contiguous range, slicing is both the natural expression and the cheaper one (view, no copy). If the selection depends on a condition on the data itself (values greater than some threshold) or an arbitrary set of indices, fancy indexing is the only tool that can express it at all, and the copy it makes is simply the necessary cost of that flexibility.

*One-liner: slicing selects a contiguous range cheaply as a view (no copy, shares memory with the original); boolean/integer "fancy indexing" selects based on a condition or arbitrary positions that a slice range can't express, at the cost of always producing a copy — the choice is driven by what you're actually selecting, not a raw speed preference.*

**Q: Why would you choose a NumPy array over a plain Python list for numerical data, beyond just "it's faster"?**
A: Speed is the headline reason, but there are two others worth naming explicitly. First, memory efficiency: a Python list of numbers actually stores a list of *pointers* to separate Python integer/float objects scattered in memory, each carrying its own object overhead (type info, reference count) — a NumPy array stores the raw numeric values themselves, contiguously, with none of that per-element object overhead, which matters a lot once you're working with real-sized datasets rather than toy examples.

Second, the vectorized API itself is a genuine ergonomic and correctness win, independent of speed — expressing "compute the mean of every row" or "find all values above the 95th percentile" as a single NumPy expression is both less code and less error-prone than hand-writing the equivalent loop, where it's easy to introduce an off-by-one bug or mishandle an edge case (empty array, single row) that NumPy's built-in functions already handle correctly.

The tradeoff, worth being honest about: a NumPy array requires a single fixed dtype for all its elements, which is less flexible than a Python list's "anything goes" nature — if you genuinely need a mixed-type collection, NumPy's rigidity is a real cost, not a win. The right tool depends on whether you're doing numerical computation (NumPy's whole reason to exist) or general-purpose heterogeneous storage (a plain list or a different structure).

*One-liner: beyond raw speed, NumPy arrays save real memory (no per-element Python object overhead) and their vectorized API reduces both code volume and loop-logic bugs versus hand-written Python loops — the real tradeoff is NumPy's fixed-dtype rigidity versus a list's flexibility, so the right choice depends on whether the data is genuinely uniform numerical data or needs to stay heterogeneous.*

## Links
- Related course note: [[02 Literature Notes/Courses/Applied Data Science]]
- Related map: [[06 Maps of Content/Applied Data Science Concepts]]
- Related permanent note:
- Related code snippet:
- Related project:
