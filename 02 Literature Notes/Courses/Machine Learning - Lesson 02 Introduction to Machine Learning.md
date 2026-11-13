# Machine Learning - Lesson 02 Introduction to Machine Learning

> Depth goal: hold the core ML vocabulary (features, labels, train/test split, generalization, overfitting, the three paradigms) solidly enough to explain it from first principles, not just name-drop it.

## Source
- Course: Machine Learning
- Lesson / Chapter: Lesson 02 - Introduction to Machine Learning
- Resource: [[07 Resources Library/Machine Learning/Slides/Lesson_2_Introduction_to_Machine_Learning.pdf]]

---

## 1. Mental Model

**Machine learning is the practice of having a program improve at a task by learning patterns from data, instead of being told the exact rules by hand.** A traditional program is: human writes exact rules, program follows them. An ML program is: human provides examples (and sometimes a goal), the program finds the rules itself, by searching for patterns that explain the examples well.

The whole field splits cleanly into three paradigms based on what information you give the model to learn from:

- **Supervised learning** — you provide labeled examples (input, correct answer). The model learns a mapping from input to answer, then applies it to new inputs it hasn't seen.
- **Unsupervised learning** — you provide only inputs, no answers. The model finds structure in the data on its own (groups, patterns, compressed representations) with nobody telling it what the "right" structure is.
- **Reinforcement learning** — an agent takes actions in an environment and gets back a reward signal; it learns, through trial and error, which actions lead to better long-term reward.

> Key intuition: **the paradigm is determined entirely by what you're allowed to show the model.** Have correct answers for every example? Supervised. Have examples with no answers at all? Unsupervised. Have an environment you can act in and get feedback from? Reinforcement.

---

## 2. How It Actually Works

### 2.1 Features and labels
A **feature** is one measurable input variable describing an example — a customer's age, a house's square footage, a pixel's brightness. A **label** is the correct answer you're trying to predict, present only in supervised learning. A dataset is a table: each row is one example, each column (except the label) is a feature.

The practical skill here is recognizing that feature *quality* often matters more than model choice — a model can only learn patterns that are actually present and visible in the features you give it. If you're trying to predict house price but never include square footage as a feature, no model, however sophisticated, can recover that missing signal.

### 2.2 The train/test split
If you train a model and then evaluate it on the exact same data it was trained on, you learn nothing useful — the model can simply memorize the answers rather than actually learning a generalizable pattern, and would report a misleadingly perfect score. The fix: split your data into a **training set** (used to fit the model) and a **test set** (held out, never seen during training, used only to measure how well the model actually generalizes to new data).

This single idea — never evaluate on data the model was trained on — is the foundation of every rigorous ML evaluation practice. Violating it, even accidentally (a subtle form of this is **data leakage**, where information from the test set sneaks into training through a shared preprocessing step), silently invalidates your reported performance.

### 2.3 Generalization and overfitting
**Generalization** is a model's ability to perform well on genuinely new, unseen data — not just the specific examples it was trained on. This is the actual goal of machine learning; a model that only performs well on its training data is useless in practice, since the whole point is to use it on new, real-world inputs it hasn't seen before.

**Overfitting** is the specific failure mode where a model learns the training data too well — including its noise and idiosyncrasies, not just its genuine underlying pattern — so it performs great on training data but poorly on new data. This happens when a model has too much flexibility (too many parameters, too little data, or too long a training run) relative to how much genuine signal is actually present. The model ends up fitting the specific quirks of this one training sample rather than the broader pattern that would also hold for new data.

The opposite failure, **underfitting**, is when a model is too simple to capture the real pattern at all — it performs poorly on both training and test data, because it never learned enough to begin with.

### 2.4 Supervised learning's two sub-types
Within supervised learning, the type of label determines the sub-problem: if the label is a continuous number (price, temperature), it's **regression**; if the label is a discrete category (spam/not-spam, which of 5 classes), it's **classification**. The same underlying supervised-learning logic (learn input→output from labeled examples) applies to both — only the shape of the output, and therefore the evaluation metrics, differ.

---

## 3. Implementation

Assumed stack: `scikit-learn`, `numpy`, `pandas`. Snippet demonstrates the core train/test workflow.

### Train/Test Split and Baseline Comparison
```python
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

rng = np.random.RandomState(0)
X = rng.rand(200, 1) * 10          # one feature
y = 3 * X.squeeze() + 5 + rng.randn(200) * 2   # true pattern + noise

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

model = LinearRegression().fit(X_train, y_train)

train_mse = mean_squared_error(y_train, model.predict(X_train))
test_mse = mean_squared_error(y_test, model.predict(X_test))
print(f"train MSE: {train_mse:.2f}  test MSE: {test_mse:.2f}")
# Similar train/test MSE -> good generalization.
# Much lower train MSE than test MSE -> overfitting signal.
```

### Demonstrating Overfitting with Model Complexity
```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

for degree in [1, 4, 15]:
    poly_model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
    poly_model.fit(X_train, y_train)
    tr = mean_squared_error(y_train, poly_model.predict(X_train))
    te = mean_squared_error(y_test, poly_model.predict(X_test))
    print(f"degree={degree:>2}  train={tr:6.2f}  test={te:6.2f}")
# Low degree: both errors high (underfit).
# Very high degree: train error keeps dropping, test error rises (overfit).
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Train/test split ratio** | 70/30 or 80/20 is typical; use more test data for small, noisy datasets. |
| **Random vs stratified split** | Stratify by label for classification, especially with imbalanced classes. |
| **Model complexity** | Start simple; add complexity only if validation error justifies it. |
| **When labels are unavailable** | Default to unsupervised approaches, or invest in labeling a subset. |
| **Reinforcement learning fit** | Only reach for RL when you have a genuine sequential-decision/reward setup, not just any prediction task. |

---

## 5. Failure Modes & Gotchas

- Evaluating on training data and reporting that as real performance.
- Data leakage: fitting a scaler/encoder on the full dataset before splitting, letting test-set statistics leak into training.
- Treating a tiny test set's single score as a reliable estimate of true performance.
- Assuming more complex models are always better — ignoring the overfitting risk.
- Mislabeling a problem's paradigm (e.g., trying to force unlabeled data into a supervised framing without labels).

---

## 6. Self-Check

1. What distinguishes supervised, unsupervised, and reinforcement learning?
2. Why can't you evaluate a model on its own training data?
3. What is overfitting, mechanically, and what causes it?
4. What's the difference between regression and classification?
5. What is data leakage, and give one concrete way it happens.

---

## 7. Interview Q&A

**Q: Why can't you trust a model's performance on its own training data as a measure of how good it really is?**
A: Think about what "learning" actually means for a model with enough flexibility: given enough parameters, a model can simply memorize the specific examples it was shown, including whatever noise or random quirks happened to be in that particular sample, rather than learning the genuine, underlying pattern that would also hold true for new data. If you then evaluate it on those same examples, you're really just checking "did it memorize what I showed it," which it can trivially do well — that tells you nothing about how it handles something genuinely new.

The entire reason you build a model in the first place is to use it on new, future data it hasn't seen — a loan applicant you haven't evaluated yet, a sensor reading from tomorrow. The held-out test set is a stand-in for that future, unseen data. Performance on it is actually informative specifically because the model never got to see or adjust to these exact examples during training — so doing well here is real evidence the model learned something that generalizes, not just something it memorized.

*One-liner: training data performance can be trivially gamed by memorization, since the model got to adjust itself based on seeing those exact examples — a held-out test set is only meaningful because the model never got to adjust to it, making good performance there actual evidence of real generalization, not memorization.*

**Q: What is overfitting, mechanically — not just "it's bad," but what's actually happening inside the model?**
A: A real dataset is made up of two things mixed together: a genuine underlying pattern (the actual relationship you want the model to learn) and noise (random variation specific to this one sample — measurement error, natural randomness, quirks that wouldn't repeat if you collected the data again). A model with enough capacity (enough parameters, enough flexibility) can fit both of these simultaneously — it can bend and twist its predictions to match not just the real pattern but also the specific random noise points in this one training set.

The problem: the noise in your training set is, by definition, specific to that one sample — it won't repeat in exactly the same way in a new, different sample of data. So a model that has shaped itself around this training set's specific noise has learned something that doesn't transfer — when you show it new data (with different random noise, or no noise at that particular point), the predictions it makes based on "memorized" noise patterns are now wrong, since that specific noise isn't there anymore. This is why an overfit model shows a large gap between training performance (great, because it fit the noise too) and test performance (worse, because the noise-fitting doesn't transfer).

*One-liner: overfitting happens when a model has enough flexibility to fit both the genuine underlying pattern and the random noise specific to one training sample — since that specific noise won't repeat the same way in new data, the model's noise-fitting doesn't transfer, producing a large gap between great training performance and worse real-world performance.*

**Q: How would you decide whether a given problem is supervised, unsupervised, or reinforcement learning?**
A: Don't start from "which algorithm sounds appropriate" — start from "what information do I actually have access to." If you have a dataset where every example comes with a known, correct answer (you know which past loan applicants actually defaulted, you know which past emails were actually spam), that's supervised learning — you can directly teach the model the correct input-to-output mapping using these known answers.

If you have a dataset but no correct answers at all — just a pile of customer records with no pre-existing "segment" labels, for instance — that's unsupervised learning; there's no ground truth to supervise against, so the best you can do is find structure (clusters, patterns) the data itself suggests, without anyone having pre-labeled what that structure should be.

If instead of a static dataset, you have an agent that takes actions in some environment, and you get back a reward signal reflecting how good a sequence of actions turned out to be (not a single "correct answer" per action, but delayed feedback on a whole trajectory of decisions) — that's reinforcement learning, which is a genuinely different problem shape from either of the other two, since it's about learning a decision policy through trial-and-error interaction, not about learning from a fixed, pre-collected dataset at all.

*One-liner: the paradigm follows directly from what information is actually available — known correct answers for every example means supervised, no answers at all means unsupervised, and an agent interacting with an environment and getting back delayed reward feedback means reinforcement learning — the question is never "which algorithm," it's "what do I actually have to learn from."*

**Q: Why is regression evaluated with error metrics like MSE/RMSE, while classification is evaluated with accuracy/precision/recall — why can't you just use one evaluation approach for both?**
A: The core reason: a regression output and a classification output are fundamentally different kinds of things, and "how wrong was this prediction" means something different for each. A regression prediction is a number on a continuous scale — predicting a house price of $302,000 when the true price was $300,000 is a small, nearly-correct error; predicting $150,000 would be a much larger error. Metrics like MSE (mean squared error) and RMSE directly measure *how far off*, numerically, the prediction was — they need a continuous output to even make sense, since "distance between two numbers" is what they're computing.

A classification prediction is a discrete category — there's no meaningful sense in which predicting "cat" when the true answer was "dog" is a "smaller" or "larger" error than predicting "car" when the true answer was "dog" — they're just both simply wrong, with no numerical distance between categories to measure. This is why classification uses a fundamentally different kind of metric: accuracy (what fraction of predictions were exactly correct), precision/recall (specifically about correctly identifying a particular class versus mixing it up with others), rather than any kind of numeric "distance from the right answer."

*One-liner: regression outputs are continuous numbers where "how far off" is a meaningful, measurable distance (which MSE/RMSE directly compute), while classification outputs are discrete categories with no meaningful numeric distance between them (predicting the wrong category is just wrong, not "a little wrong" or "a lot wrong") — which is why each needs evaluation metrics suited to the actual shape of its output.*

**Q: Give a concrete example of data leakage, and explain why it specifically invalidates your reported test performance.**
A: A concrete example: you have a dataset of house prices, and before splitting into train/test, you compute the average price *across the entire dataset* and use it to fill in some missing values, or you fit a feature scaler (like standardizing features to have mean 0, variance 1) on the *entire* dataset before splitting. Then you split into train/test and train your model.

The problem: that average, or that scaler's learned mean/variance, was computed using information from *every* row, including the rows that are now sitting in your "held-out" test set. So your test set is no longer genuinely unseen information from the model's perspective — a piece of information derived from the test set (its contribution to that global average, or to the scaler's learned statistics) has already leaked into the training process, before training even began. The model has indirectly "seen" something about the test set's values, even though it never saw the test set's actual rows directly.

This specifically invalidates your reported test performance because the entire point of a test set is to measure performance on information the model has never been influenced by in any way — once even a small amount of test-set information has leaked into training (through a shared preprocessing step, in this case), the test set is no longer a clean, uncontaminated measure of genuine generalization; your reported performance will likely be overly optimistic compared to how the model would actually perform on truly fresh, never-before-touched data.

*One-liner: fitting a preprocessing step (like a scaler or an imputation value) on the full dataset before splitting into train/test means the test set's own values influenced that preprocessing, so the model was indirectly shaped by test-set information before training even began — this breaks the test set's entire purpose (measuring performance on information the model was never influenced by), making reported performance overly optimistic versus how the model would actually do on truly fresh data.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Machine Learning]]
- Related map: [[06 Maps of Content/Machine Learning Concepts]]
- Downstream: [[02 Literature Notes/Courses/Machine Learning - Lesson 03 Supervised Learning and Regression]]
</content>
