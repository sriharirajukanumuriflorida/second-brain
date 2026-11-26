# Python Refresher - Lesson 01 Python Fundamentals and Setup

## Source
- Course: Python Refresher
- Lesson / Chapter: Lesson 01 - Introduction to Python Fundamentals and Setup
- Resource: [[07 Resources Library/Python Refresher/PDFs/Lesson_01_Introduction_to_Python_Fundamentals_and_Setup.pdf]]
- Related Notebooks / Practice:
  - [[07 Resources Library/Python Refresher/Guided Practices/Lesson_01_Guided_Practice_Introduction_to_Python_Fundamentals_and_Setup.pdf]]

## Summary
- Sets up the Python environment and introduces the core language fundamentals used throughout the program.
- Establishes the baseline skills (syntax, variables, basic types) needed before data structures and modeling work.

## Key Ideas
- Installing and configuring Python and a working development environment.
- Core syntax: variables, data types, operators, and basic input/output.
- How the Python interpreter and scripts fit into a data science workflow.

## Important Details
- This is the entry point for the refresher; everything later assumes a working setup.
- Focus is on getting comfortable running code, not yet on data structures or libraries.

## Questions
- Which setup or environment concepts should become permanent notes?
- Which fundamentals are worth capturing as reusable snippets?

## Interview Q&A

**Q: Python is dynamically typed — what does that actually mean mechanically, and why does it matter for how you write and debug code?**
A: In a statically typed language, you declare a variable's type up front (`int x = 5`), and the compiler checks and locks that type in before the program ever runs — if you later try to assign a string to `x`, the compiler catches it immediately. Python does the opposite: a variable is just a name that points at an object, and the object itself carries its type, not the variable. You can write `x = 5` and then later `x = "hello"` in the same program, and Python won't complain — the name `x` simply now points at a different kind of object.

This matters practically in two opposite directions. It makes Python fast to write and flexible — you don't spend time declaring types, and the same function can often work on multiple types without extra code. But it also means type-related mistakes that a compiler would catch instantly in a static language instead surface only at runtime, often several steps away from where the actual mistake was made — you might pass a string where a function expected a number, and nothing complains until that value actually gets used in a way that breaks (e.g., trying to add it to an integer).

*One-liner: dynamic typing means the type lives on the object, not the variable name, which makes Python fast and flexible to write but pushes type-mismatch errors from compile-time (caught immediately) to runtime (caught only when the bad value is actually used), often far from where the real mistake happened.*

**Q: What's actually the difference between a Python script being "interpreted" versus a compiled language, and why does that matter in practice?**
A: A compiled language (like C) is translated entirely into machine code ahead of time by a separate compilation step — you get an executable file, and running it executes that machine code directly, with no translation happening at runtime. Python instead reads and executes your code line by line (technically, it compiles to an intermediate bytecode first, then an interpreter runs that bytecode) — there's no separate "build an executable" step before you can run it.

The practical consequence: Python code can fail partway through execution, after having already run and had real effects from the earlier lines — if line 50 has a syntax error but lines 1-49 already printed output or wrote to a file, that already happened before the interpreter even reached the broken line (actually, Python does parse the whole file for syntax errors before running any of it — but a *runtime* error, like calling a function that doesn't exist, will only surface when execution actually reaches that line, after everything before it has already run). This is different from a compiled language, where many of those same mistakes are caught before the program runs at all, not partway through.

*One-liner: Python executes line by line rather than building a complete standalone executable ahead of time, which means many runtime mistakes only surface when execution actually reaches that specific line — after everything before it has already run with real effects — unlike a compiled language where more classes of error are caught before the program starts running at all.*

**Q: Why does a Python development environment typically involve virtual environments — what problem are they actually solving?**
A: Without a virtual environment, every Python project on your machine shares one single, global set of installed packages. If Project A needs `numpy` version 1.20 and Project B needs `numpy` version 1.26, and you can only have one version installed globally at a time, you genuinely cannot satisfy both projects' requirements simultaneously without something breaking.

A virtual environment creates an isolated, project-specific copy of the Python interpreter and its installed packages, so each project gets its own independent set of dependencies at whatever versions it actually needs, with zero interference between projects. This is why "which packages are installed" becomes a per-project question rather than a single global answer — switching into a different project's virtual environment switches your entire available package set along with it.

*One-liner: a virtual environment gives each project its own isolated copy of installed packages, which is what actually lets two different projects on the same machine depend on two different, mutually incompatible versions of the same library without either one breaking.*

**Q: What's the practical difference between a Python variable holding an int versus a float, and where does this actually bite people?**
A: An `int` is a whole number with no fractional component (`5`), while a `float` represents a number with a decimal component (`5.0`, `3.14`) — and critically, floats are stored using a binary floating-point representation that cannot exactly represent every decimal value, the same way `1/3` can't be written exactly in decimal. This means float arithmetic can produce small, surprising rounding errors — `0.1 + 0.2` in Python does not evaluate to exactly `0.2` as a float object, but something extremely close to it.

This bites people specifically when they compare floats for exact equality (`if result == 0.3:` can silently fail even when `result` is mathematically "0.3", because the actual stored binary value is off by a tiny fraction) or when they expect integer division to behave like float division (in Python 3, `/` always returns a float, while `//` does floor/integer division — mixing these up produces subtly wrong results rather than an obvious crash).

*One-liner: floats use a binary representation that can't exactly store every decimal value, so float arithmetic carries small rounding error — which is why comparing floats with exact equality (`==`) is a common, quiet bug, and why Python deliberately keeps `/` (float division) and `//` (floor division) as two distinct operators rather than one.*

## Links
- Related course note: [[02 Literature Notes/Courses/Python Refresher]]
- Related map: [[06 Maps of Content/Python Concepts]]
- Related permanent note:
- Related code snippet:
- Related project:
