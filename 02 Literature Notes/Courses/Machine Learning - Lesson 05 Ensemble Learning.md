# Machine Learning - Lesson 05 Ensemble Learning

> Depth goal: understand mechanically why bagging reduces variance and boosting reduces bias, implement a simple version of each, and know when ensembles are (and aren't) worth the interpretability cost.

## Source
- Course: Machine Learning
- Lesson / Chapter: Lesson 05 - Ensemble Learning
- Resource: [[07 Resources Library/Machine Learning/Slides/Lesson_5_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Machine Learning/Notebooks/5.1_Ensemble_Learning.ipynb]]

---

## 1. Mental Model

**An ensemble combines many individually-imperfect models into one collectively-better model, on the principle that independent errors tend to average out.** If you have several models that each make mistakes, but their mistakes aren't all the same mistakes (they err somewhat independently), averaging or voting across them cancels out a good portion of each individual model's noise, leaving a more stable, more accurate consensus prediction than any single model achieves alone.

There are two fundamentally different ensemble strategies, targeting two different sources of error:

- **Bagging** (Bootstrap Aggregating) — train many models independently and in parallel, each on a different random subset of the data, then average their predictions. This specifically reduces **variance** (how much a model's predictions swing around depending on exactly which training data it happened to see).
- **Boosting** — train models sequentially, where each new model specifically focuses on correcting the mistakes the previous models made. This specifically reduces **bias** (how systematically wrong a model's predictions are, even with plenty of data).

> Key intuition: **bagging averages away noise from unstable models; boosting corrects the systematic mistakes of weak models.** They attack genuinely different problems, which is why both exist rather than one simply being "better."

---

## 2. How It Actually Works

### 2.1 Bagging and Random Forests
Bagging trains `N` copies of the same base model (often a decision tree), each on a different **bootstrap sample** — a random sample of the training data drawn *with replacement*, meaning the same row can appear multiple times in one bootstrap sample while other rows don't appear at all. Each of these `N` models, trained on a slightly different view of the data, ends up slightly different from the others — some overfit in one direction, some in another. Averaging their predictions (or taking a majority vote, for classification) cancels out a lot of this individual, uncorrelated overfitting, since each model's specific noise is unlikely to be shared by the others.

**Random Forest** adds one more trick on top of plain bagging: at each split in each tree, it only considers a random subset of features (not all of them) as candidates for the best split. This deliberately decorrelates the trees further — without this, all the trees in the "forest" would tend to make very similar splits on the strongest features, ending up highly correlated with each other, which would reduce how much their errors actually cancel out when averaged.

### 2.2 Why bagging reduces variance (the math intuition)
If you average `N` independent, identically-distributed random variables each with variance `σ²`, the variance of their average is `σ²/N` — averaging genuinely shrinks variance, and shrinks it more as `N` grows. Individual decision trees (especially deep, unpruned ones) have high variance — small changes in training data can produce quite different trees. Bagging exploits the variance-reduction-through-averaging math directly: average many high-variance-but-roughly-unbiased trees, and the ensemble's variance drops substantially while its bias stays about the same as a single tree's.

### 2.3 Boosting (AdaBoost and Gradient Boosting)
Boosting builds models one at a time, sequentially — each new model is trained specifically to focus on the mistakes the ensemble so far has made. **AdaBoost** does this by re-weighting training examples: after each round, examples the current ensemble got wrong get higher weight, so the next model trained pays specifically more attention to those hard cases. **Gradient Boosting** generalizes this: each new model is trained to predict the *residual error* (how far off the current ensemble's predictions still are) rather than the original target directly, so each new addition specifically patches the ensemble's remaining mistakes.

Because each model specifically targets what previous models got wrong, boosting can reduce **bias** — systematically correcting a simple base model's blind spots — in a way bagging's "average many similar models" strategy can't, since bagging's models are all trained independently and don't know about each other's mistakes at all.

### 2.4 XGBoost and modern gradient boosting
**XGBoost** (and similar libraries like LightGBM, CatBoost) are highly optimized, regularized implementations of gradient boosting — adding explicit regularization terms to control tree complexity, efficient handling of missing values, and substantial engineering for speed at scale. They're frequently the strongest performers on structured/tabular data in practice, which is why they dominate many real-world tabular ML competitions and production systems.

### 2.5 The interpretability tradeoff
A single decision tree is directly readable — you can trace the exact path of yes/no questions that led to a specific prediction. An ensemble of hundreds of trees (whether bagged or boosted) has no single readable decision path — the final prediction is an aggregate of many trees' votes or weighted contributions, which is much harder for a human to directly interpret, even though the ensemble's raw predictive accuracy is usually meaningfully better. This tradeoff (accuracy vs. interpretability) is a real, deliberate choice, not a side effect — techniques like feature importance scores and SHAP values exist specifically to partially recover interpretability from otherwise-opaque ensembles.

---

## 3. Implementation

Assumed stack: `scikit-learn`, `xgboost`.

### Comparing a Single Tree, Random Forest, and Gradient Boosting
```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

X, y = make_classification(n_samples=1000, n_features=15, n_informative=8, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

models = {
    "Single Tree": DecisionTreeClassifier(max_depth=None, random_state=0),
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=0),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=200, random_state=0),
}
for name, model in models.items():
    scores = cross_val_score(model, X_train, y_train, cv=5)
    print(f"{name:>18}  CV accuracy: {scores.mean():.3f} (+/- {scores.std():.3f})")
```

### Illustrating Variance Reduction via Bagging
```python
import numpy as np
from sklearn.tree import DecisionTreeRegressor

rng = np.random.RandomState(0)
X_full = rng.rand(300, 1) * 10
y_full = np.sin(X_full).squeeze() + rng.randn(300) * 0.3

# Train 50 trees, each on a different bootstrap sample; compare single-tree
# variance to the bagged ensemble's variance at a fixed test point.
x_test_point = np.array([[5.0]])
single_tree_preds, bagged_preds = [], []
for seed in range(50):
    idx = rng.choice(len(X_full), len(X_full), replace=True)   # bootstrap sample
    tree = DecisionTreeRegressor(max_depth=None, random_state=seed).fit(X_full[idx], y_full[idx])
    single_tree_preds.append(tree.predict(x_test_point)[0])
bagged_pred = np.mean(single_tree_preds)
print(f"individual tree prediction variance: {np.var(single_tree_preds):.4f}")
print(f"bagged (averaged) prediction: {bagged_pred:.4f}")
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Bagging vs boosting** | Bagging (Random Forest) when base models overfit easily (high variance); boosting when base models underfit (high bias, e.g. shallow trees). |
| **Number of trees** | More trees generally help bagging without overfitting risk (diminishing returns); boosting can overfit with too many rounds — use early stopping. |
| **Learning rate (boosting)** | Lower learning rate + more rounds is typically more robust than high learning rate + few rounds. |
| **Interpretability need** | Use a single tree or linear model if stakeholders need to see the exact decision logic; use ensembles when raw accuracy matters most. |
| **XGBoost vs plain GBM** | Prefer XGBoost/LightGBM for production tabular tasks — better regularization, speed, and missing-value handling out of the box. |

---

## 5. Failure Modes & Gotchas

- Using bagging on an already-low-variance, high-bias model — it won't help, since bagging only addresses variance.
- Boosting for too many rounds without early stopping, eventually overfitting to training noise.
- Treating Random Forest's feature importance as causal rather than correlational.
- Expecting ensemble predictions to be as interpretable as a single tree's decision path.
- Not tuning the learning rate in gradient boosting, leading to either slow convergence or overfitting.

---

## 6. Self-Check

1. Why does averaging many independent models reduce variance — what's the underlying math?
2. Why does bagging not help with bias, while boosting does?
3. What does Random Forest add on top of plain bagging, and why does it matter?
4. How does gradient boosting's sequential training differ from bagging's parallel training?
5. What's the actual tradeoff you're making when choosing an ensemble over a single interpretable model?

---

## 7. Interview Q&A

**Q: Why does averaging predictions from many independent models reduce variance — what's the actual mathematical reason, not just "it works"?**
A: Start from a basic statistics fact: if you have several independent random variables, each with the same variance `σ²`, and you average `N` of them together, the variance of that average is `σ²/N` — it shrinks as you average more of them together, specifically because averaging cancels out each variable's own random fluctuations, leaving behind more of their shared, common signal and less of their individual, independent noise.

A single decision tree trained on a particular random sample of data has real variance — train it on a slightly different sample (a different bootstrap draw), and you'd get a somewhat different tree, with somewhat different predictions on the same test point, purely due to which specific training examples it happened to see. This variability is exactly the "noise" in the statistics sense above. If you train many such trees, each on an independently-drawn bootstrap sample, their individual prediction errors (relative to the true underlying pattern) are at least partially independent of each other — one tree's specific overfitting quirks aren't the same as another tree's, since they saw different random samples.

Averaging these many trees' predictions directly applies the `σ²/N` shrinkage: much of each individual tree's specific, independent noise cancels out in the average, while the genuine, shared signal (the actual underlying pattern all the trees are, on average, correctly approximating) survives and dominates the averaged result. This is precisely why the ensemble's variance ends up lower than any single tree's variance, without needing to sacrifice the individual trees' relatively low bias.

*One-liner: averaging N independent random variables shrinks variance by a factor of N (from basic statistics) — since different trees trained on different bootstrap samples have at least partially independent prediction noise, averaging their predictions cancels out much of that individual noise while preserving the shared, genuine signal, which is the literal mathematical reason bagging reduces variance.*

**Q: Why does bagging not help with bias, while boosting specifically does?**
A: Bias is a model's *systematic*, consistent error — the kind of mistake it makes reliably, regardless of which specific training sample it happened to see, because the model itself (its assumptions, its simplicity) isn't capable of capturing the true underlying pattern. Variance is the *inconsistent* part — how much the model's predictions swing around from one training sample to another.

Bagging trains many copies of the *same* base model, each on a different random sample, and averages them. But if the base model has a systematic bias — say, it's too simple to capture a genuinely non-linear relationship — then *every single one* of those bagged copies will share that exact same systematic bias, since it comes from the model's inherent limitation, not from which specific random sample it saw. Averaging many models that all share the same systematic mistake doesn't cancel that mistake out at all — averaging only cancels out the *independent, random* part of each model's error (the variance), not the *shared, consistent* part (the bias). This is exactly why bagging helps with variance but does essentially nothing for bias.

Boosting works completely differently — it doesn't average independently-trained copies at all; it trains models *sequentially*, where each new model is specifically built to correct whatever the previous models' combined predictions were still getting systematically wrong. Since each new addition directly targets the ensemble's remaining systematic errors (the bias), rather than just averaging away independent noise, boosting can genuinely reduce bias in a way bagging's independent-averaging approach structurally cannot.

*One-liner: bias is a model's systematic error shared across every training sample, so averaging many copies of the same biased model (bagging) only cancels out their independent, random variance — not their shared systematic bias, which survives the averaging untouched; boosting instead trains each new model specifically to correct the previous models' remaining systematic mistakes, which is exactly how it reduces bias where bagging can't.*

**Q: What does Random Forest add on top of plain bagging of decision trees, and why does that addition actually matter?**
A: Plain bagging just trains many decision trees, each on a different bootstrap sample of the data, and averages their predictions. Random Forest adds one more specific trick: at every single split within every single tree, instead of considering all available features as candidates for the best split, it only considers a random subset of the features.

Here's why this matters: without this extra randomness, if there's one or two features that are genuinely very strong predictors, *every* tree in the bagged ensemble would tend to pick those same strong features for its early, most important splits, regardless of which bootstrap sample it was trained on — because those features are just genuinely the best splitting choice, almost every time, for almost any sample of the data. This would make the trees highly correlated with each other — structurally similar, differing mainly in minor details further down each tree, rather than being genuinely different from each other in a meaningful way.

Recall that variance reduction through averaging works best when the things being averaged have *independent* errors — highly correlated trees don't actually provide much independent information to average away, since they're all making largely the same decisions and likely the same mistakes. By forcing each split to only consider a random subset of features, Random Forest deliberately prevents every tree from converging on the exact same dominant-feature splitting strategy, producing genuinely more diverse, less-correlated trees — which means there's more independent noise to actually cancel out when their predictions are averaged, strengthening the core variance-reduction benefit bagging is trying to achieve in the first place.

*One-liner: Random Forest adds random feature subsetting at every split, specifically to prevent every tree from converging on the same dominant-feature splitting strategy (which would make the trees highly correlated) — since variance reduction through averaging works best with independent errors, this deliberate decorrelation is what makes Random Forest's averaging genuinely more effective than plain bagging of standard decision trees.*

**Q: How does gradient boosting's sequential training process actually differ from bagging's parallel training, step by step?**
A: Bagging trains all its models completely independently of each other — model 1 doesn't know anything about model 2's existence or performance; you could train all `N` bagged trees simultaneously, in parallel, on different machines, with no coordination needed between them at all, since each one is just independently fitting a different random bootstrap sample. The final ensemble combines them only at prediction time, by averaging or voting.

Gradient boosting is structurally sequential and cannot be parallelized across its stages the same way: you start with an initial, simple prediction (often just the average of the target). Then, you train a second model whose job is specifically to predict the *residual error* — how far off the current ensemble's predictions still are from the true values. You add this second model's predictions (scaled by a learning rate) to the running ensemble, which now makes somewhat better predictions, but still has some residual error left. You train a third model specifically to predict *this new, updated residual error*, and add it in — repeating this process, with each new model genuinely depending on knowing what all the previous models in the sequence got wrong, which is information you only have *after* training those previous models, making this process inherently sequential, step by step, rather than something you can parallelize across the stages.

*One-liner: bagging trains all its models completely independently and in parallel (no model knows about any other), combining them only at prediction time via averaging — gradient boosting trains sequentially, where each new model is specifically trained to predict the current ensemble's residual error, meaning each stage genuinely depends on knowing what the previous stages got wrong, which makes the process inherently sequential rather than parallelizable.*

**Q: You've trained a Random Forest and a single decision tree on the same tabular dataset; the forest has meaningfully better accuracy. What tradeoff did you actually make to get that improvement, and when would you choose the single tree anyway?**
A: The tradeoff is interpretability for accuracy. A single decision tree has a genuinely readable, traceable decision path — for any specific prediction, you can point to the exact sequence of yes/no feature-threshold questions that led to that specific output, something a human stakeholder (a loan officer, a doctor, a compliance reviewer) can directly inspect, verify, and explain to someone else in plain terms. A Random Forest's prediction is an aggregate — hundreds of individual trees voting or averaging together — and there's no single, simple decision path to point to for any one prediction; the "explanation" for why the forest predicted what it did is distributed across all those trees in a way that's much harder to directly communicate or verify by eye.

You'd choose the single, less-accurate tree specifically when the actual requirement isn't "maximize raw predictive accuracy" but "produce a decision that can be directly explained and justified to a human" — situations with real regulatory or compliance requirements for explainability (certain lending or hiring decisions, for instance, where you may be legally required to articulate a specific reason for a denial), or situations where trust and buy-in from domain experts genuinely depends on them being able to see and sanity-check the actual decision logic, not just trust a black-box accuracy number. In these cases, the accuracy gain from the ensemble may not be worth losing the ability to directly explain individual decisions — accuracy isn't the only thing that matters; sometimes directly inspectable, justifiable reasoning is itself a hard requirement, not a nice-to-have.

*One-liner: the tradeoff is interpretability for accuracy — a single tree gives a directly traceable decision path for any prediction, while a forest's prediction is an opaque aggregate across many trees with no single simple explanation — you'd choose the single tree when a direct, inspectable justification for each decision is a genuine requirement (regulatory, compliance, stakeholder trust), not just a nice-to-have, even at the cost of some raw accuracy.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Machine Learning]]
- Related map: [[06 Maps of Content/Machine Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Machine Learning - Lesson 04 Classification and Its Applications]] · Downstream: [[02 Literature Notes/Courses/Machine Learning - Lesson 06 Unsupervised Learning]]
</content>
