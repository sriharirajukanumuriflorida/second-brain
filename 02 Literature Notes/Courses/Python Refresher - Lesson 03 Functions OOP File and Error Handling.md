# Python Refresher - Lesson 03 Functions OOP File and Error Handling

## Source
- Course: Python Refresher
- Lesson / Chapter: Lesson 03 - Functions, OOP, File and Error Handling
- Resource: [[07 Resources Library/Python Refresher/PDFs/Lesson_03_Functions_OOPs_File_and_Error_Handling (1).pdf]]
- Related Notebooks / Practice:
  - [[07 Resources Library/Python Refresher/Guided Practices/lesson_3_guided_project_1.ipynb]]

## Summary
- Introduces reusable and structured code through functions and object-oriented programming.
- Adds robustness with file input/output and error/exception handling.

## Key Ideas
- Defining and calling functions, arguments, return values, and scope.
- Object-oriented programming: classes, objects, attributes, and methods.
- Reading and writing files, plus try/except error handling for resilient code.

## Important Details
- Functions and OOP enable reusable, maintainable code used across notebooks and projects.
- Error handling and file I/O are essential for real data pipelines.

## Questions
- Which OOP or error-handling concepts should become permanent notes?
- Which function/class patterns are worth saving as reusable snippets?

## Interview Q&A

**Q: Why do functions matter beyond "avoiding repeated code" — what's the deeper design benefit?**
A: Avoiding repetition is a real benefit, but the deeper one is that a well-designed function creates a boundary — a clear contract of "given these inputs, I produce this output" — that lets you reason about a piece of logic in isolation, without having to hold the entire surrounding program in your head at once. Once you trust a function's contract, you can call it from anywhere and reason about the caller's logic without re-deriving how the function itself works internally every time.

This matters enormously as programs grow: without functions, a program is one long, undifferentiated sequence of steps where understanding any one part requires tracing through everything around it. With well-scoped functions, you get composable units — each one testable, debuggable, and replaceable on its own — which is what actually makes larger programs tractable to build and maintain, not just shorter to write.

*One-liner: functions aren't just about avoiding copy-paste — they create an isolated contract (given these inputs, this output) that lets you reason about, test, and debug one piece of logic without having to hold the entire surrounding program in your head, which is what makes larger programs tractable at all.*

**Q: What's the actual difference between a function's local scope and the global scope, and where does this cause real bugs?**
A: A variable created *inside* a function only exists within that function's local scope — it's created when the function is called and disappears once the function returns; code outside the function has no access to it at all, even by the same name. A variable created at the top level of a script lives in the global scope and is visible everywhere, including inside functions (which can *read* global variables by default).

The real bug shows up around modification, not just visibility: if a function tries to simply assign to a variable with the same name as a global one, Python treats that as creating a new *local* variable, shadowing the global one, rather than modifying the original — so the global variable outside the function remains completely unchanged, often surprising someone who expected the function to have updated it. (Python requires an explicit `global` keyword inside the function to actually reassign the outer variable, specifically because this default protects against accidentally clobbering global state.)

*One-liner: a function can read a global variable by default, but a plain assignment inside the function creates a new local variable instead of modifying the global one — this is a deliberate safety default, and forgetting it is exactly where "I updated the variable but it didn't actually change outside the function" bugs come from.*

**Q: What problem does object-oriented programming (classes/objects) actually solve that plain functions and data structures don't?**
A: Plain functions and data structures (say, a dictionary of user info plus a few functions that operate on it) can get you quite far, but nothing enforces that the data and the functions that are supposed to operate on it stay correctly paired together — any function anywhere could receive a malformed version of that dictionary and nothing would stop it. OOP bundles the data (attributes) and the behavior that's specifically meant to operate on that data (methods) into one single unit (a class), so the relationship between "this data" and "these specific operations on it" is explicit and enforced by the language, not just a convention everyone has to remember to follow.

This matters specifically as the number of related operations and pieces of data grows — a `BankAccount` class with a `balance` attribute and a `withdraw()` method can enforce its own invariant (never let balance go negative) *inside* the method itself, every single time it's called, rather than relying on every single piece of calling code elsewhere in the program to remember to check that condition correctly and consistently.

*One-liner: OOP bundles data and the operations meant to act on that data into one enforced unit (a class), so invariants (like "balance can never go negative") can live inside the class itself and be enforced every time, rather than depending on every single piece of calling code elsewhere remembering to check that correctly on its own.*

**Q: Why use `try/except` for error handling instead of just checking conditions beforehand with `if` statements?**
A: For many failure cases, checking beforehand is genuinely impossible to do completely and reliably — you can check "does this file path look valid" before opening a file, but you can't fully predict every possible way a file operation could still fail at the exact moment you try it (permissions changed, the disk is now full, another process deleted the file a millisecond after your check ran). This is sometimes called a TOCTOU gap (time-of-check to time-of-use) — the world can change between your check and your actual attempt.

`try/except` instead says: attempt the operation, and if it fails for *any* reason that raises an exception, handle that failure in one consistent place — rather than trying to anticipate and pre-check every possible way it could go wrong. This is also why error handling and file I/O are taught together: file operations are one of the most common sources of "this can fail in ways you genuinely can't fully predict ahead of time" in real programs, making `try/except` the more robust of the two approaches for that specific class of risk.

*One-liner: beforehand checks can't catch everything that could still go wrong between the check and the actual operation (a TOCTOU gap) — `try/except` instead attempts the operation directly and handles whatever actually goes wrong in one place, which is why it's the more robust approach specifically for operations like file I/O where failure modes are hard to fully predict in advance.*

## Links
- Related course note: [[02 Literature Notes/Courses/Python Refresher]]
- Related map: [[06 Maps of Content/Python Concepts]]
- Related permanent note:
- Related code snippet:
- Related project:
