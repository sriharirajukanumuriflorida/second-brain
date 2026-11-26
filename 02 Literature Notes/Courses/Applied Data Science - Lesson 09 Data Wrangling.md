# Applied Data Science - Lesson 09 Data Wrangling

## Source
- Course: Applied Data Science
- Lesson / Chapter: Lesson 09 - Data Wrangling
- Resource: [[07 Resources Library/Applied Data Science/Slides/Lesson_09_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Applied Data Science/Notebooks/9.01_Data_Wrangling.ipynb]]

## Summary
- Covers cleaning and transforming raw data into analysis-ready form.
- Addresses missing values, formatting, and reshaping.

## Key Ideas
- Handling missing, duplicate, and inconsistent data.
- Merging, joining, reshaping, and transforming datasets.
- Data quality as a prerequisite for reliable modeling.

## Important Details
- Wrangling is often the most time-consuming part of real projects.

## Questions
- Which wrangling techniques should become permanent notes?
- Which cleaning workflows are worth saving as snippets?

## Interview Q&A

**Q: Why is "just drop every row with a missing value" usually the wrong default strategy for handling missing data?**
A: Dropping a row discards every other piece of information that row contained, not just the one missing value — if a dataset has, say, 20 columns and one column is missing in 15% of rows, blanket-dropping those rows throws away a large chunk of otherwise-complete, usable data for the sake of handling a single column's gaps. At scale, if missingness is spread across different columns in different rows, this compounding effect can silently eliminate a much larger fraction of the dataset than the raw per-column missingness rate would suggest.

More subtly, whether dropping is even a sound strategy depends on *why* the data is missing, not just how much is missing. If data is missing completely at random, dropping rows mostly just costs you sample size without introducing bias. But if missingness is *related* to the value itself or to another variable (customers who didn't disclose income tend to be in a specific income bracket, sensor readings are more likely to be missing during extreme conditions), dropping those rows systematically removes a non-random slice of the data — which can bias every subsequent analysis in a way that's not obvious just from looking at the remaining "clean" data.

The more careful default: understand the missingness pattern and mechanism first (is it random, or does it correlate with something), then choose a strategy proportional to that understanding — which might be imputation (filling with a reasoned estimate), might be creating an explicit "was this missing" indicator feature, or might indeed be dropping, but as a deliberate choice rather than a reflexive default.

*One-liner: dropping a row with any missing value discards every other column's data in that row too, and if the missingness isn't genuinely random (it correlates with the value itself or another variable), dropping systematically removes a non-random slice of the data and can quietly bias every downstream analysis — understand why data is missing before deciding how to handle it, rather than defaulting to dropping.*

**Q: What's the actual risk of using the column mean to fill in missing values, even though it's the most common quick fix?**
A: Filling missing values with the column mean preserves the dataset's overall average (by construction, you're inserting the average value exactly where data was missing), which is why it looks like a safe, neutral choice at first glance. But it does this at a real cost: it artificially shrinks the dataset's *variance*, specifically at the positions that were originally missing — every imputed value is now exactly the average, with none of the natural spread real (non-missing) values would have had.

This matters because many downstream statistical methods and models are sensitive to variance, not just the mean — a model or statistical test that relies on a feature's genuine variability to detect a relationship can have its signal artificially diluted if a meaningful fraction of that feature's values are all identically set to the mean, especially if the original missingness wasn't random (per the previous question) and the true, unobserved values at those positions would have been systematically different from the mean anyway.

More sophisticated imputation strategies — filling based on a related column's value (median income by region rather than a single global mean), or a model-based imputation that predicts the likely missing value from other features — exist specifically to avoid this variance-flattening and to make a more informed guess than "just use the overall average everywhere." The simple column-mean approach is a reasonable fast baseline for a small amount of plausibly-random missingness, not a universally safe default for any missingness situation.

*One-liner: mean-imputation preserves the overall average but artificially shrinks variance exactly at the imputed positions (every missing value becomes identical), which can dilute the genuine signal a model or test relies on — it's a reasonable fast baseline for a small amount of plausibly-random missingness, not a universally safe default.*

**Q: Why is data wrangling often described as the most time-consuming part of a real data science project, more than the actual modeling?**
A: Real-world data almost never arrives already in the clean, consistent, analysis-ready shape that a modeling algorithm expects — it comes from multiple systems with inconsistent formatting (dates stored as strings in three different formats across different source systems), genuine data-entry errors, duplicate records from merges across systems, and columns that mix types in ways that weren't enforced at collection time. Untangling all of this into one clean, trustworthy table is inherently a long tail of individually-small, individually-annoying problems, each of which needs to be noticed and handled correctly.

By contrast, once data is actually clean and well-structured, fitting a standard model is often comparatively fast — calling `.fit()` on a well-prepared DataFrame takes far less wall-clock effort than the investigative work of figuring out why a join produced more rows than expected, or why a date column silently contains three different formats. The modeling step assumes clean data as an input; wrangling is the (often much longer) process of actually getting there.

This is also why data wrangling skill is a genuine differentiator in practice, not a lesser or more "junior" task than modeling — a sophisticated model trained on poorly-wrangled data will produce confidently wrong results, while even a simple model trained on carefully, correctly wrangled data can be genuinely trustworthy; the wrangling quality sets a ceiling on how trustworthy any downstream modeling result can actually be.

*One-liner: real data arrives messy from multiple inconsistent sources, and untangling that into clean, trustworthy data is a long tail of individually small problems that takes real investigative time — modeling a well-prepared dataset is comparatively fast, which is why wrangling quality sets the ceiling on how trustworthy any downstream model's results can actually be, regardless of how sophisticated the model itself is.*

## Links
- Related course note: [[02 Literature Notes/Courses/Applied Data Science]]
- Related map: [[06 Maps of Content/Applied Data Science Concepts]]
- Related permanent note:
- Related code snippet:
- Related project:
