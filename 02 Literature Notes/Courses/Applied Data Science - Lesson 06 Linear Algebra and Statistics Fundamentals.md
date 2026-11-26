# Applied Data Science - Lesson 06 Linear Algebra and Statistics Fundamentals

## Source
- Course: Applied Data Science
- Lesson / Chapter: Lesson 06 - Linear Algebra and Statistics Fundamentals
- Resource: [[07 Resources Library/Applied Data Science/Slides/Lesson_06_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Applied Data Science/Notebooks/6_01_Linear_Algebra.ipynb]]
  - [[07 Resources Library/Applied Data Science/Notebooks/6.02_Statistics_Fundamentals.ipynb]]

## Summary
- Introduces the linear algebra and statistics that underpin data science and ML.
- Covers vectors/matrices and core descriptive statistics.

## Key Ideas
- Vectors, matrices, and operations used in modeling.
- Descriptive statistics: mean, variance, distributions, correlation.
- How these fundamentals support later modeling work.

## Important Details
- Mathematical foundation for probability, statistics, and ML models.
- Two notebooks split linear algebra and statistics fundamentals.

## Questions
- Which math/statistics concepts should become permanent notes?

## Interview Q&A

**Q: Why does machine learning lean so heavily on linear algebra specifically — what's actually being represented as vectors and matrices?**
A: A single example in a dataset (one customer, one house, one image) is, almost universally, represented as a vector — an ordered list of numbers, one per feature (age, square footage, pixel intensity). A whole dataset of many examples is then naturally a matrix — one row per example, one column per feature. This isn't an arbitrary choice of notation; it's what lets an entire dataset's worth of computation be expressed and executed as a small number of matrix operations instead of looping over examples one at a time.

A linear model's prediction (a weighted sum of features) is literally a dot product between a feature vector and a weight vector — `prediction = w · x`. Scaling this up to predict for an entire dataset at once, instead of one example at a time, is a single matrix-vector multiplication (`predictions = X @ w`), which is both dramatically more concise to express and (per NumPy's vectorization, covered earlier in this course) dramatically faster to actually execute than an equivalent Python loop.

Beyond simple linear models, this representation is foundational to how neural networks work (every layer is fundamentally a matrix multiplication followed by a non-linearity) and how many classical ML algorithms are actually implemented under the hood — understanding vectors/matrices isn't an abstract math requirement bolted onto ML, it's the literal data structure the whole field computes with.

*One-liner: individual examples are vectors and whole datasets are matrices because that's what lets an entire dataset's computation (a linear model's predictions, a neural network layer) be expressed and executed as a handful of fast matrix operations, instead of looping over examples one at a time — linear algebra isn't abstract decoration on ML, it's the literal computational substrate.*

**Q: What's the actual difference between correlation and causation, and why does this distinction matter so much in applied data science?**
A: Correlation measures whether two variables tend to move together — as one goes up, does the other tend to go up (or down) too, measured numerically (a correlation coefficient). Causation is a much stronger claim: that a change in one variable actually *produces* the change in the other, that if you intervened and changed variable A, variable B would change as a direct result. Correlation can exist without causation in several ways: a third, unmeasured variable could be driving both (ice cream sales and drowning deaths both rise with summer heat — the heat causes both, ice cream doesn't cause drowning), or the correlation could simply be coincidental.

This distinction matters enormously in applied work because the whole point of most business analysis is to inform a *decision* — "if we did X, would Y improve" — and that's fundamentally a causal question. A purely correlational finding ("customers who use feature X also tend to have higher retention") does NOT, by itself, tell you that pushing more customers to use feature X will *cause* their retention to improve — maybe already-engaged customers (who were always going to retain) are simply the ones who naturally discover feature X, with no causal arrow running from the feature to retention at all.

The practical discipline: be explicit, in any analysis, about whether you're making a correlational observation or a causal claim, and be honest that establishing genuine causation usually requires more than observational correlation alone — a controlled experiment (A/B test), or careful causal-inference techniques designed specifically to account for confounding variables that a simple correlation can't rule out.

*One-liner: correlation means two variables move together; causation means one change actually produces the other — a correlation can arise from a shared underlying cause (a confounder) with no real causal link at all, which matters because most business decisions are implicitly causal questions ("if we did X, would Y improve"), and a purely correlational finding can't honestly answer that without a controlled experiment or real causal-inference reasoning.*

**Q: Why does variance (not just the mean) matter so much when summarizing a dataset — what would you miss if you only reported averages?**
A: The mean tells you where a dataset is centered, but says nothing about how spread out the values actually are around that center — and two datasets with identical means can look wildly different in practice. A customer satisfaction score averaging 7/10 where every customer actually scored close to 7 describes a genuinely different (and more reassuring) situation than an average of 7/10 produced by half the customers scoring 10 and half scoring 4 — same mean, completely different reality, and a decision-maker who only sees "average satisfaction: 7" has no way to tell these apart.

Variance (and its square root, standard deviation) quantifies exactly this spread — how far, on average, individual values deviate from the mean. High variance signals that the mean is a less reliable single summary of "what's typical," since individual cases can diverge from it substantially; low variance means the mean is a genuinely representative stand-in for most of the actual data points.

This matters directly for decision-making and risk assessment: two investment options with the same average return but very different variance represent very different risk profiles, even though "average return" alone makes them look identical — which is exactly the kind of distinction a mean-only summary would hide, and precisely why statistical summaries in applied work should essentially never report a mean without also reporting some measure of spread.

*One-liner: two datasets can share an identical mean while looking completely different in practice (uniformly near the average vs. polarized around it) — variance/standard deviation quantifies that spread, which is why a mean reported alone can hide real risk or disagreement in the underlying data that a decision-maker genuinely needs to know about.*

## Links
- Related course note: [[02 Literature Notes/Courses/Applied Data Science]]
- Related map: [[06 Maps of Content/Applied Data Science Concepts]]
- Related permanent note:
- Related code snippet:
- Related project:
