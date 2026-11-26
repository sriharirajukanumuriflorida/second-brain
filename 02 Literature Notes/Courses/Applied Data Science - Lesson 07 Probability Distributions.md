# Applied Data Science - Lesson 07 Probability Distributions

## Source
- Course: Applied Data Science
- Lesson / Chapter: Lesson 07 - Probability Distributions
- Resource: [[07 Resources Library/Applied Data Science/Slides/Lesson_07_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Applied Data Science/Notebooks/7.01_Probability_Distribution.ipynb]]

## Summary
- Introduces probability and common probability distributions.
- Explains how distributions model uncertainty in data.

## Key Ideas
- Probability basics and random variables.
- Common distributions (normal, binomial, Poisson) and their uses.
- How distributions inform statistical inference and modeling.

## Important Details
- Probability underlies statistical testing and many ML methods.

## Questions
- Which probability concepts should become permanent notes?

## Interview Q&A

**Q: Why does it matter whether a random variable is discrete or continuous — how does this actually change how you'd model or reason about it?**
A: A discrete random variable can only take specific, separate, countable values (the number of customer-support calls in a day: 0, 1, 2, 3... — never 2.5), while a continuous random variable can take any value within a range (a customer's exact time-to-checkout: 3.2 seconds, 3.247 seconds, any real number in between). This isn't just a labeling distinction — it determines what kind of probability question even makes sense to ask.

For a discrete variable, it's meaningful to ask "what's the probability of exactly 3 calls today" — a specific value has a genuine, non-zero probability attached to it, described by a probability *mass* function. For a continuous variable, asking "what's the probability the checkout time is exactly 3.247000... seconds" is actually meaningless — there are infinitely many possible exact values, so any single exact value has probability zero. Instead, continuous variables are described by a probability *density* function, and meaningful questions are always about *ranges* ("what's the probability checkout takes between 3 and 4 seconds"), computed as the area under the density curve over that range.

Getting this distinction wrong leads to real modeling mistakes — treating a genuinely continuous quantity as if specific exact values carry meaningful individual probability, or choosing a discrete distribution (like Poisson, built for counts) to model something that's actually continuous (like a duration), where a continuous distribution would be the structurally correct fit.

*One-liner: discrete variables take specific countable values where exact values have real, nonzero probability (mass functions); continuous variables take any value in a range where only ranges (not exact values) have meaningful nonzero probability (density functions) — picking the wrong family for the underlying data type isn't just imprecise, it's structurally the wrong tool.*

**Q: Why is the normal distribution so central in statistics and data science — is it actually common in real data, or just mathematically convenient?**
A: Both, and they're connected. Empirically, many real-world quantities that result from the additive combination of many small, independent random factors do genuinely tend to look approximately normal (human height is influenced by many independent genetic and environmental factors, each contributing a small push up or down; measurement error is often the sum of many small independent sources of noise). This isn't a coincidence — it's a direct consequence of the Central Limit Theorem, which states that the sum (or average) of many independent random variables tends toward a normal distribution regardless of the shape of each individual variable's own distribution.

This is precisely why the normal distribution shows up so often in statistical *inference*, even when the underlying data itself isn't normal: the sampling distribution of a sample mean (if you took many samples and computed the mean of each) tends toward normal as sample size grows, by the same Central Limit Theorem — which is the mathematical foundation that makes many standard hypothesis tests and confidence intervals valid, even for underlying data that isn't normally distributed itself.

So the normal distribution's centrality isn't just mathematical convenience chosen for its own sake — it's genuinely the distribution that emerges from aggregating many independent small effects, which describes an enormous number of real-world phenomena and, separately, describes the behavior of sample means themselves, which is exactly why it underpins so much of classical statistical inference.

*One-liner: the normal distribution is central both because many real phenomena genuinely are sums of many small independent effects (which the Central Limit Theorem shows tends toward normal) and because sample means themselves tend toward normal by the same theorem — which is the actual mathematical reason it underpins so much of statistical inference, not just mathematical convenience for its own sake.*

**Q: When would you use a binomial distribution versus a Poisson distribution — they both model counts, so what actually distinguishes them?**
A: Both describe counts of discrete events, but they answer structurally different questions. The binomial distribution models the number of successes in a *fixed number of independent trials*, each with the same success probability — how many heads in 20 coin flips, how many customers out of a fixed batch of 100 convert. The key ingredients it needs: a known, fixed number of trials (n), and a fixed per-trial probability of success (p).

The Poisson distribution instead models the number of events occurring in a *fixed interval of time or space*, when events happen independently at some constant average rate, but there's no natural "number of trials" to count — how many customer support calls arrive in an hour, how many typos appear per page. There's no fixed n here; events could in principle happen any number of times in the interval, which is a fundamentally different setup than "count successes out of n fixed attempts."

The practical discriminator: if your situation has a genuine, countable number of discrete trials each with a pass/fail outcome, binomial is the structurally correct model. If your situation is instead "count how many times something happens over a continuous span," with no natural fixed number of attempts to point to, Poisson is the structurally correct model — picking based on which setup actually matches your data, not just because both happen to produce whole-number counts.

*One-liner: binomial counts successes across a fixed, known number of independent yes/no trials (n flips, n customers); Poisson counts events occurring at a constant rate over a continuous interval with no natural fixed "number of trials" at all — the choice follows from whether your situation genuinely has a countable set of fixed trials or is instead "how many times did something happen over a span."*

## Links
- Related course note: [[02 Literature Notes/Courses/Applied Data Science]]
- Related map: [[06 Maps of Content/Applied Data Science Concepts]]
- Related permanent note:
- Related code snippet:
- Related project:
