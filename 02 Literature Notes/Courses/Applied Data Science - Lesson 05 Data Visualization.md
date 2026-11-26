# Applied Data Science - Lesson 05 Data Visualization

## Source
- Course: Applied Data Science
- Lesson / Chapter: Lesson 05 - Data Visualization
- Resource: [[07 Resources Library/Applied Data Science/Slides/Lesson_05_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Applied Data Science/Notebooks/5.01_Introduction_to_Data_Visualization.ipynb]]
  - [[07 Resources Library/Applied Data Science/Notebooks/5.02_Seaborn_Plotly_Visualization_Basics_to_Advanced.ipynb]]

## Summary
- Covers data visualization for exploring and communicating insights.
- Introduces plotting libraries from basics to advanced interactive charts.

## Key Ideas
- Principles of effective visualization and chart selection.
- Matplotlib fundamentals; Seaborn for statistical plots.
- Plotly for interactive, advanced visualizations.

## Important Details
- Visualization supports both exploratory analysis and stakeholder communication.
- Notebooks move from basic to advanced Seaborn/Plotly charts.

## Questions
- Which visualization principles should become permanent notes?
- Which plotting patterns are worth saving as snippets?

## Interview Q&A

**Q: How do you actually decide which chart type to use for a given dataset, rather than defaulting to whatever chart you're most comfortable building?**
A: The decision should start from the *question* you're trying to answer or the *relationship* you're trying to show, not from chart familiarity — different chart types are structurally suited to showing different kinds of relationships, and picking the wrong one can actively obscure the thing you're trying to communicate even if the data itself is plotted correctly.

If you're comparing a single metric across discrete categories (revenue by region), a bar chart is suited to this because it's easy to visually compare bar heights/lengths — a line chart here would be actively misleading, since a line implies a continuous trend connecting points that don't actually have a continuous relationship to each other (there's no meaningful "in-between" value connecting "North" and "South"). If you're showing how a metric changes over a continuous dimension like time, a line chart is the right fit specifically because it does imply continuity, which is now actually true of the data. If you're examining the relationship between two continuous numeric variables, a scatter plot is suited to revealing correlation or clustering that neither a bar nor a line chart could show at all.

The general discipline: ask "what relationship am I actually trying to show — comparison across categories, change over a continuous dimension, or relationship between two numeric variables" before touching a plotting library, since that answer determines the correct chart family, and only after that should style/library choice (Matplotlib vs. Seaborn vs. Plotly) even enter the conversation.

*One-liner: chart choice should follow from the relationship you're actually trying to show (categorical comparison → bar, change over a continuous dimension → line, relationship between two numeric variables → scatter) — a chart type's implied structure (like a line's implied continuity) can actively mislead if it doesn't match what the data actually represents.*

**Q: Why would you reach for Seaborn over plain Matplotlib, given that Seaborn is built on top of Matplotlib anyway?**
A: Matplotlib is a low-level, general-purpose plotting library — it gives you precise control over every element of a figure, but that control comes at the cost of needing to specify a lot of detail yourself for things that are extremely common in statistical/exploratory work (grouping by a categorical variable and plotting each group with a distinct color, adding a regression line to a scatter plot, computing and plotting a distribution's confidence interval).

Seaborn is built specifically for statistical visualization, and its API reflects that: many of these common statistical patterns are a single function call (`sns.boxplot(x=category, y=value, data=df)` groups and plots in one line, with sensible defaults for color, spacing, and labeling already handled) rather than the multi-step Matplotlib code needed to assemble the same chart manually. It also integrates directly with Pandas DataFrames, so you typically pass column names rather than manually extracting and reshaping arrays first.

The practical tradeoff: Seaborn's defaults and statistical helpers make common exploratory-analysis charts dramatically faster to produce and harder to get subtly wrong, at the cost of less fine-grained control than raw Matplotlib for genuinely custom or unusual visualizations — which is why Seaborn is typically the first choice for standard statistical exploration, with a drop down to Matplotlib (which Seaborn is built on and fully interoperates with) when you need to customize something Seaborn doesn't expose directly.

*One-liner: Seaborn wraps Matplotlib with statistical-visualization-specific defaults and DataFrame integration, turning common exploratory patterns (grouped comparisons, distributions, regression lines) into one function call instead of several lines of manual Matplotlib setup — the tradeoff is less fine-grained control, which is why you drop to raw Matplotlib specifically when you need to customize something Seaborn's API doesn't expose.*

**Q: Why would you choose an interactive library like Plotly over a static Matplotlib/Seaborn chart — when does interactivity actually matter?**
A: Interactivity matters specifically when the *audience* needs to explore the data themselves, rather than just receive a conclusion you've already drawn. A static chart is a finished argument — you've already decided what to highlight, what range to show, what to annotate — which is exactly right when you want to make one clear point to a stakeholder in a report or a slide. A static chart can't answer a follow-up question like "what does this look like if I zoom into just March" without you going back and making a new chart.

An interactive Plotly chart lets the viewer hover for exact values, zoom into a specific range, or toggle categories on/off, which matters when the audience's questions aren't fully known in advance, or when the use case is a dashboard someone will return to repeatedly with different questions each time — a sales dashboard a manager checks weekly needs to support "let me drill into this specific region" on demand, not just show one fixed view.

The tradeoff to be honest about: interactivity adds real complexity (and, for Plotly specifically, generally needs to be viewed in a browser/notebook context rather than a static image in a printed report or email), so it's not a strict upgrade — a static chart embedded in a one-time written report, where the point is to make one specific argument clearly, is often the better choice precisely because it can't be "explored away" from the point you're making.

*One-liner: interactivity earns its complexity when the audience needs to explore the data themselves with questions not fully known in advance (a recurring dashboard) — a static chart is the right choice when you're making one specific, already-decided point to an audience that doesn't need to go digging further, since a static chart can't be "explored away" from your intended takeaway.*

## Links
- Related course note: [[02 Literature Notes/Courses/Applied Data Science]]
- Related map: [[06 Maps of Content/Applied Data Science Concepts]]
- Related permanent note:
- Related code snippet:
- Related project:
