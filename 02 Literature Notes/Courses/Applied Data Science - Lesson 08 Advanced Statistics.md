# Applied Data Science - Lesson 08 Advanced Statistics

## Source
- Course: Applied Data Science
- Lesson / Chapter: Lesson 08 - Advanced Statistics
- Resource: [[07 Resources Library/Applied Data Science/Slides/Lesson_08_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Applied Data Science/Notebooks/8.01_Advanced_Statistics.ipynb]]

## Summary
- Covers inferential and advanced statistics for drawing conclusions from data.
- Introduces hypothesis testing and related techniques.

## Key Ideas
- Sampling, confidence intervals, and hypothesis testing.
- p-values, significance, and common statistical tests.
- Interpreting statistical results responsibly.

## Important Details
- Advanced statistics supports rigorous, defensible data analysis.

## Questions
- Which inference concepts (hypothesis testing, p-values) should become permanent notes?

## Interview Q&A

**Q: What does a p-value actually tell you, and what's the most common way people misinterpret it?**
A: A p-value answers a specific, narrow question: *assuming the null hypothesis is true* (assuming there is genuinely no real effect/difference), what's the probability of seeing a result at least as extreme as what you actually observed, just by random chance? A small p-value means "this result would be quite surprising if there really were no effect" — which is evidence against the null hypothesis, not proof that the alternative is true.

The most common and consequential misinterpretation is treating the p-value as "the probability that the null hypothesis is true" or "the probability the result is due to chance" — neither is correct. The p-value is computed by *assuming* the null hypothesis is true in the first place; it can't simultaneously tell you the probability that assumption itself is true, any more than a conclusion derived by assuming it's raining can tell you the probability that it's actually raining. It's a statement about how surprising your data would be under the null, not a direct statement of probability about the null hypothesis itself.

This matters practically because treating a p-value of, say, 0.03 as "97% chance there's a real effect" overstates the evidence in a way that leads to overconfident conclusions — a small p-value is evidence against the null, filtered through the specific, narrow lens of "how surprising is this data under that assumption," not a direct probability statement about which hypothesis is correct.

*One-liner: a p-value is the probability of seeing data this extreme IF the null hypothesis were true — it is NOT the probability that the null hypothesis is true, and treating it as the latter (a very common mistake) overstates how much the data actually proves about which hypothesis is correct.*

**Q: Why does a confidence interval communicate more useful information than a single point estimate alone?**
A: A point estimate (a single number, like "average conversion rate: 4.2%") presents a sample-derived number as if it were the one true value, with no indication of how much that estimate could plausibly vary if you had drawn a different sample. In reality, any estimate computed from a finite sample carries real uncertainty — a different random sample from the same underlying population would almost certainly produce a slightly different number.

A confidence interval makes that uncertainty explicit by giving a *range* of plausible values, along with a stated confidence level (a 95% CI of [3.8%, 4.6%] communicates that, under repeated sampling, this method of constructing the interval would capture the true population value about 95% of the time). This is far more honest and more useful for decision-making than the bare point estimate — a decision-maker comparing two options with point estimates 4.2% and 4.4% might think option two is clearly better, but if both have wide, heavily overlapping confidence intervals, that apparent difference may not be a real, reliable distinction at all.

The practical discipline: report a confidence interval alongside any point estimate whenever the estimate will inform a real decision, specifically so that a decision-maker isn't misled by false precision — a single number look authoritative in a way that can hide how little the data actually pins down the true value.

*One-liner: a point estimate alone presents one sample-derived number as if it were certain; a confidence interval makes the genuine sampling uncertainty explicit as a range, which prevents a decision-maker from over-trusting an apparent difference between two estimates that may not actually be reliably distinguishable once that uncertainty is accounted for.*

**Q: What's the difference between statistical significance and practical (business) significance, and why do both matter?**
A: Statistical significance is purely a statement about whether an observed effect is unlikely to be due to random chance alone — a result can be statistically significant with an extremely large sample size even if the actual size of the effect is tiny and practically meaningless (a 0.01% improvement in conversion rate can be "statistically significant" with millions of observations, purely because a large enough sample makes even a tiny, real effect detectable against the noise floor).

Practical significance asks a completely different question: given the actual *size* of the effect, does it matter enough to justify acting on it — is the cost of implementing a change (engineering effort, user disruption, opportunity cost) actually worth a 0.01% conversion improvement? A result can be statistically significant and practically irrelevant at the same time, and conversely (less often, but it happens) a result might fail to reach statistical significance on a small sample while still representing an effect size that would be very much worth pursuing if confirmed with more data.

The practical discipline: always report and consider effect size (the actual magnitude of the difference/effect) alongside statistical significance, and make the business decision based on both together — statistical significance answers "is this probably real," while practical significance answers "does this real thing actually matter enough to act on," and a defensible business recommendation needs an honest answer to both questions, not just the first one.

*One-liner: statistical significance only tells you an effect is probably real (not due to chance), which large samples can achieve even for tiny, practically meaningless effects — practical significance asks whether the effect's actual size is large enough to be worth acting on, and a sound business decision needs both answers, not just statistical significance alone.*

## Links
- Related course note: [[02 Literature Notes/Courses/Applied Data Science]]
- Related map: [[06 Maps of Content/Applied Data Science Concepts]]
- Related permanent note:
- Related code snippet:
- Related project:
