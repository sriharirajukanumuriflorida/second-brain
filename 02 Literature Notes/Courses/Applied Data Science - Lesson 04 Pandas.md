# Applied Data Science - Lesson 04 Pandas

## Source
- Course: Applied Data Science
- Lesson / Chapter: Lesson 04 - Pandas
- Resource: [[07 Resources Library/Applied Data Science/Slides/Lesson_04_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Applied Data Science/Notebooks/4.01_Introduction_to_Pandas.ipynb]]
  - [[07 Resources Library/Applied Data Science/Notebooks/4.02_Pandas_DataFrame.ipynb]]
  - [[07 Resources Library/Applied Data Science/Notebooks/4.03_Date_and_TimeDelta_in_Pandas.ipynb]]
  - [[07 Resources Library/Applied Data Science/Notebooks/4.04_Working_with_Text_Data.ipynb]]

## Summary
- Introduces Pandas for tabular data manipulation and analysis.
- Covers Series/DataFrame, time data, and text data handling.

## Key Ideas
- Series and DataFrame structures for labeled tabular data.
- Selecting, filtering, grouping, and aggregating data.
- Working with dates/timedeltas and text data.

## Important Details
- Pandas is the core tool for cleaning and exploring structured data.
- Notebooks progress from basics to time and text handling.

## Questions
- Which Pandas concepts should become permanent notes?
- Which DataFrame idioms are worth saving as snippets?

## Interview Q&A

**Q: What's the actual relationship between a Pandas DataFrame and a NumPy array — is a DataFrame just "NumPy with labels"?**
A: That's a reasonable first approximation, but it undersells what the labeling actually buys you. Under the hood, a DataFrame's columns are typically backed by NumPy arrays (or Pandas' own array-like extensions for special types), so you do get NumPy's vectorized speed for numeric operations within a column. But a DataFrame adds a genuinely different capability on top: every row and column has a *label* (an index value, a column name), and operations are defined in terms of those labels, not just raw positions.

This labeling changes how you reason about alignment. If you add two DataFrames together, Pandas aligns them by matching index labels first, then adds — not by matching raw position like NumPy would. This is enormously useful for real data work: if you're joining a customer table with a transactions table, you want rows to align by customer ID (a label), not by whatever row order each table happened to be in — a NumPy array has no concept of this at all.

So the honest answer is: a DataFrame is NumPy's numerical engine wrapped in a labeled, heterogeneous-column, alignment-aware structure purpose-built for real-world tabular data — the labels aren't cosmetic, they change the actual semantics of how operations combine data.

*One-liner: a DataFrame uses NumPy arrays under the hood for speed, but the labels (row index, column names) aren't cosmetic — they change the actual semantics of how data aligns and combines across operations, which is the real reason DataFrames exist rather than just using NumPy arrays directly for tabular data.*

**Q: When would you use `.loc` versus `.iloc` to select data from a DataFrame, and why does the distinction matter?**
A: `.loc` selects by *label* — the actual index value or column name, whatever that happens to be (a string, a date, a non-sequential integer you assigned as an ID). `.iloc` selects by *integer position* — the 0th row, the 3rd column — regardless of what label is actually attached to that position. The distinction matters because, after any filtering, sorting, or reindexing operation, a DataFrame's labels and its positions can diverge completely — row position 0 might now hold the label "customer_4821" rather than "0."

Using the wrong one silently produces a different (and often wrong) selection rather than an obvious error, which is exactly what makes this a common, hard-to-spot bug: `df.loc[0]` asks for the row *labeled* 0, which may not exist (or may be a completely different row than you expect) after the DataFrame has been filtered or sorted, while `df.iloc[0]` always means "whatever is currently first," regardless of its label.

The practical discipline: use `.loc` when you're reasoning in terms of meaningful identifiers (a specific customer ID, a specific date), and `.iloc` when you're genuinely reasoning about position (the first N rows, the last column) — and be suspicious of code using bare `df[0]`-style indexing or mixing the two conventions without being explicit, since that ambiguity is exactly where this class of bug hides.

*One-liner: `.loc` selects by label (the actual index/column value) and `.iloc` by raw integer position — after filtering or sorting, a row's label and its position can diverge completely, so using the wrong one doesn't error, it silently returns a different (and often wrong) row.*

**Q: Why does Pandas give dates and times their own dedicated types (Timestamp, Timedelta) instead of just storing them as strings?**
A: A string like `"2024-03-15"` looks like a date to a human, but to the computer it's just a sequence of characters — there's no built-in way to ask "how many days until this other date-string" or "what's 3 months after this one" without first parsing it into something that actually understands calendar arithmetic. Storing dates as plain strings pushes all of that parsing and arithmetic work onto you, manually, every single time you need it, and opens the door to inconsistent formats silently breaking comparisons (`"2024-3-15"` vs `"2024-03-15"` look different as strings but should be the same date).

Pandas' `Timestamp` and `Timedelta` types encode genuine calendar and duration semantics: a `Timestamp` knows how to correctly compute "add one month" even across varying month lengths and leap years, and a `Timedelta` represents a genuine duration you can add, subtract, and compare directly. This is what makes operations like "resample this time series to monthly totals" or "filter to the last 30 days" a single, correct, built-in operation instead of a manually-written, easy-to-get-wrong parsing exercise.

The broader principle, which shows up again with feature engineering later in this course: giving data the *correct, semantically rich type* (a real date type instead of a string, a real category type instead of a string, a boolean instead of 0/1) up front is what unlocks correct, built-in operations on it — a string can represent a date, but it can't *behave* like one.

*One-liner: a date stored as a string can't do calendar arithmetic (add a month, compute days-between) without being parsed first, every time — Pandas' Timestamp/Timedelta types encode real calendar semantics so operations like resampling or date-range filtering work correctly out of the box, which is the same "give data its correct type, not just a string that looks right" principle that matters again later in feature engineering.*

**Q: What's the difference between merging/joining DataFrames and simply concatenating them — when would you reach for each?**
A: Concatenation (`pd.concat`) stacks DataFrames together along an axis — adding more rows (stacking two DataFrames with the same columns on top of each other) or more columns (placing two DataFrames with the same rows side by side) — without any logic about matching values between them. It's the right tool when you already know the pieces belong together in a fixed arrangement, like combining monthly sales files that each have the same columns into one yearly dataset.

Merging/joining (`pd.merge`) is fundamentally different: it combines two DataFrames based on matching values in a shared key column (or columns), the same logic as a SQL join — for every row in one table, find the row(s) in the other table where a specified key column matches, and combine them. This is the right tool whenever you have two genuinely different tables that relate to each other through a shared identifier — customers and their orders, products and their categories — where there's no guarantee the rows are already in any particular corresponding order.

The practical signal for which to use: if the two pieces of data are "the same kind of thing split into chunks" (more rows or more columns of the *same* entities), concatenate. If they're "two different kinds of things that relate to each other through a shared key" (and you need the join logic to figure out which rows actually correspond), merge.

*One-liner: concatenate when you're stacking pieces of the same kind of data that already belong together in a fixed arrangement (more rows or columns of the same entities); merge/join when you're combining two genuinely different tables that relate through a shared key column, the same logic as a SQL join, needed whenever row correspondence isn't already guaranteed by position.*

## Links
- Related course note: [[02 Literature Notes/Courses/Applied Data Science]]
- Related map: [[06 Maps of Content/Applied Data Science Concepts]]
- Related permanent note:
- Related code snippet:
- Related project:
