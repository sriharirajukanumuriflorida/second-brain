# Applied Data Science - Lesson 02 Introduction to Data Science

## Source
- Course: Applied Data Science
- Lesson / Chapter: Lesson 02 - Introduction to Data Science
- Resource: [[07 Resources Library/Applied Data Science/Slides/Lesson_02_Introduction_to_Data_Science.pdf]]

## Summary
- Establishes what data science is and the end-to-end data science lifecycle.
- Introduces roles, tools, and the typical project workflow.

## Key Ideas
- The data science lifecycle: collect, clean, explore, model, communicate.
- Types of data and common problem framings.
- Tools and libraries used across the course.

## Important Details
- Conceptual foundation for the applied lessons that follow.

## Questions
- Which lifecycle concepts should become permanent notes?

## Interview Q&A

**Q: Why does the data science lifecycle insist on "collect, clean, explore" before anyone touches modeling — why not just jump straight to building the model?**
A: A model is only as good as the understanding of the data it's trained on, and that understanding doesn't exist yet at the start of a project — you don't know what's missing, what's mislabeled, what's duplicated, or whether the data even measures the thing you think it measures. Jumping straight to modeling means building on an unknown foundation: you might train a sophisticated model on data riddled with quality problems, and the model will faithfully learn those problems right along with (or instead of) the real signal.

The "clean" and "explore" stages exist specifically to surface these problems while they're still cheap to fix. Discovering during exploration that a column is 40% missing, or that two supposedly distinct categories actually mean the same thing due to inconsistent labeling, is a five-minute fix at that stage. Discovering the same problem *after* you've built and evaluated a model is much more expensive — you now have to question every result you've already produced, because you don't know how much the data quality issue actually affected them.

Exploration also builds the human intuition a data scientist needs to make modeling decisions well — what does the distribution of this feature actually look like, are there suspicious outliers, is there an obvious relationship between two variables that modeling should capture. Skipping straight to modeling throws away this intuition, leaving you to debug a underperforming model with no mental model of what "normal" data even looks like.

*One-liner: collect/clean/explore exist to surface data-quality problems and build intuition about the data while both are still cheap to act on — skipping to modeling means discovering the same problems later, after they've already silently shaped your results.*

**Q: What's the actual difference between a data scientist's job and a software engineer's job, given that both write code?**
A: The core difference is what each role is fundamentally uncertain about, and therefore what kind of work dominates their day. A software engineer typically knows the desired behavior precisely (a function should return the correct sum, a button should trigger the right API call) and the challenge is implementing that known behavior correctly, efficiently, and maintainably. The correctness bar is usually binary and well-defined ahead of time.

A data scientist is usually starting from genuine uncertainty about the answer itself — does this feature actually predict churn, what does "typical" customer behavior even look like, is this pattern real or just noise in a small sample. Writing code is a tool for answering that uncertainty (a script to explore a distribution, a quick regression to test a hypothesis), but the hard part is the analytical judgment about what question to ask and how to interpret an ambiguous result, not the code's correctness in the software-engineering sense.

In practice the roles blend heavily — a data scientist needs real engineering discipline to make their work reproducible and production-ready, and a software engineer building ML-adjacent systems needs real statistical literacy to not misuse a model. But the center of gravity differs: one role is centered on resolving uncertainty about the world through data, the other on correctly implementing already-understood behavior.

*One-liner: a software engineer mostly implements known-correct behavior; a data scientist mostly resolves genuine uncertainty about the data itself — code is a shared tool, but the center of gravity (implementation correctness vs. analytical judgment under uncertainty) is different.*

**Q: Why does the lifecycle end with "communicate" as its own explicit stage, rather than treating the analysis itself as the deliverable?**
A: An analysis that sits in a notebook, however rigorous, has zero business impact until a decision-maker who isn't a data scientist actually understands and acts on it. The "communicate" stage is the bridge between "I found something true" and "someone changed a decision because of it" — and that bridge doesn't build itself just because the underlying analysis was correct.

The specific skill here is translation: a stakeholder doesn't need (and often can't evaluate) the statistical machinery behind a finding — they need the finding itself, stated in terms of the decision it should inform, with enough honest caveats that they don't over-trust a result that has real uncertainty attached to it. A technically correct analysis that's communicated poorly (buried in jargon, missing the "so what") is, from a business-impact standpoint, close to useless compared to a slightly simpler analysis communicated clearly enough that someone actually acts on it.

This is also why the lifecycle treats communication as its own stage rather than an afterthought tacked onto modeling — it requires a distinct skill set (knowing your audience, choosing the right level of technical detail, visual storytelling) that doesn't automatically come bundled with strong modeling or statistical skills.

*One-liner: an analysis has no business impact until a non-technical decision-maker understands and acts on it, so "communicate" is treated as its own lifecycle stage requiring a distinct translation skill — not an afterthought, since a correct analysis communicated poorly produces close to the same business impact as no analysis at all.*

## Links
- Related course note: [[02 Literature Notes/Courses/Applied Data Science]]
- Related map: [[06 Maps of Content/Applied Data Science Concepts]]
- Related permanent note:
- Related code snippet:
- Related project:
