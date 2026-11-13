# Machine Learning - Lesson 03 Supervised Learning and Regression

> Depth goal: derive linear regression from first principles (the loss function, how it's fit, what the coefficients mean), know the error metrics cold, and recognize when regression assumptions break.

## Source
- Course: Machine Learning
- Lesson / Chapter: Lesson 03 - Supervised Learning and Regression
- Resource: [[07 Resources Library/Machine Learning/Slides/Lesson_3_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Machine Learning/Notebooks/3.1_Supervised_Learning.ipynb]]
  - [[07 Resources Library/Machine Learning/Notebooks/3.2_Supervised_Learning_Regression_and_Its_Applications.ipynb]]

---

## 1. Mental Model

**Regression is the task of predicting a continuous number from input features, by fitting a function that minimizes how wrong its predictions are, on average, across the training data.** The simplest and most foundational version, linear regression, assumes the true relationship between inputs and output is (approximately) a straight line (or hyperplane, in multiple dimensions): `y ≈ w·x + b`.

"Fitting" the model means choosing the weights `w` and bias `b` that make this line match the training data as closely as possible — and "as closely as possible" is defined precisely by a **loss function**, almost always **mean squared error (MSE)** for regression, which penalizes big errors much more than small ones (because the error gets squared).

> Key intuition: **regression finds the single line (or hyperplane) through your data that minimizes total squared prediction error.** Every other regression technique — polynomial regression, regularized regression, even some non-linear models — is a variation on this same "minimize prediction error" theme, just with a different function shape or a different penalty added.

---

## 2. How It Actually Works

### 2.1 The linear model and the loss function
Linear regression predicts: `ŷ = w₁x₁ + w₂x₂ + ... + wₙxₙ + b`. Training means finding the `w` and `b` that minimize the **mean squared error** over the training set:

$$\text{MSE} = \frac{1}{n}\sum_{i=1}^{n}(y_i - \hat y_i)^2$$

Squaring the error does two things: it makes all errors positive (so they don't cancel out when summed), and it penalizes large errors disproportionately more than small ones — a prediction off by 10 contributes 100 to the sum, while a prediction off by 1 only contributes 1. This disproportionate penalty is a deliberate design choice, not an accident — it makes the model specifically avoid being wildly wrong on any single point, even at the cost of being slightly less accurate on many other points.

### 2.2 How the weights are actually found
For linear regression specifically, there's a closed-form solution (the **normal equation**) that directly computes the optimal weights without any iterative search — but in practice, especially for larger datasets, **gradient descent** is more commonly used: start with random weights, compute how much the loss would change if each weight moved slightly (the gradient), and nudge each weight in the direction that reduces loss, repeating until the loss stops improving meaningfully.

### 2.3 Error metrics
- **MSE** (mean squared error) — the training objective itself; large errors dominate due to squaring. Hard to interpret directly since it's in squared units (e.g., squared dollars).
- **RMSE** (root mean squared error) — the square root of MSE, which brings the units back to the original scale (dollars, not squared dollars), making it directly interpretable as "typical error size."
- **R² (R-squared)** — the fraction of the variance in the target that the model explains, ranging from 0 (model explains nothing, no better than always predicting the mean) to 1 (model explains all variance, perfect fit). An R² of 0.85 means the model accounts for 85% of the variability in the target.

$$R^2 = 1 - \frac{\sum (y_i - \hat y_i)^2}{\sum (y_i - \bar y)^2}$$

The numerator is your model's total squared error; the denominator is the total squared error of the simplest possible baseline (always predicting the mean). R² asks: how much better is your model than just guessing the average every time?

### 2.4 Assumptions and when they break
Linear regression assumes: the true relationship is approximately linear, errors are roughly normally distributed and have constant variance across the range of predictions (**homoscedasticity**), and features aren't highly correlated with each other (**multicollinearity** otherwise makes individual coefficients unstable and hard to interpret). When the true relationship is curved, plain linear regression systematically underfits — this is addressed by adding polynomial features, or switching to a non-linear model entirely.

### 2.5 Regularization (a preview)
Plain linear regression, especially with many features, can overfit by assigning extreme weights that fit training noise. **Ridge** (L2 penalty) and **Lasso** (L1 penalty) regression add a penalty term to the loss that discourages large weights, trading a small amount of training fit for better generalization — Lasso specifically can shrink some weights to exactly zero, effectively performing feature selection.

---

## 3. Implementation

Assumed stack: `scikit-learn`, `numpy`.

### Linear Regression from Scratch (Gradient Descent)
```python
import numpy as np

def fit_linear_regression(X, y, lr=0.01, epochs=1000):
    n, d = X.shape
    w, b = np.zeros(d), 0.0
    for _ in range(epochs):
        y_pred = X @ w + b
        error = y_pred - y
        grad_w = (2/n) * X.T @ error
        grad_b = (2/n) * error.sum()
        w -= lr * grad_w
        b -= lr * grad_b
    return w, b

rng = np.random.RandomState(0)
X = rng.rand(200, 1) * 10
y = 3 * X.squeeze() + 5 + rng.randn(200) * 1.5
w, b = fit_linear_regression(X, y)
print(f"learned: y = {w[0]:.2f}x + {b:.2f}   (true: y = 3x + 5)")
```

### Error Metrics and Regularized Variants
```python
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

for name, model in [("Linear", LinearRegression()), ("Ridge", Ridge(alpha=1.0)), ("Lasso", Lasso(alpha=0.1))]:
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, pred) ** 0.5
    r2 = r2_score(y_test, pred)
    print(f"{name:>6}  RMSE={rmse:.3f}  R2={r2:.3f}")
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **MSE vs MAE** | MSE penalizes large errors heavily (sensitive to outliers); MAE (mean absolute error) is more robust to outliers. |
| **Plain vs regularized** | Use Ridge/Lasso when you have many features or suspect overfitting; plain linear regression for simple, well-understood relationships. |
| **Ridge vs Lasso** | Ridge shrinks all weights smoothly; Lasso can zero out weights entirely, useful for feature selection. |
| **Linear vs polynomial** | Check residual plots for curvature before assuming linearity; don't over-fit with high polynomial degree. |
| **R² interpretation** | A high R² on training data alone doesn't prove good generalization — always check on a held-out test set. |

---

## 5. Failure Modes & Gotchas

- Assuming a linear relationship when the true pattern is clearly curved (check residual plots, not just R²).
- Reporting MSE without converting to RMSE, making the error hard to interpret in real units.
- Ignoring multicollinearity, leading to unstable, hard-to-interpret coefficients.
- Outliers dragging the fitted line disproportionately due to MSE's squared penalty.
- Using R² alone as "goodness," without checking whether the model also makes sense on new, held-out data.

---

## 6. Self-Check

1. Write the MSE formula and explain why errors are squared rather than just summed as-is.
2. What does an R² of 0.0 versus 1.0 actually mean?
3. Why does Lasso, but not Ridge, perform feature selection?
4. What assumption breaks when your residual plot shows a clear curve?
5. Why is RMSE more interpretable than MSE?

---

## 7. Interview Q&A

**Q: Why does linear regression square the errors instead of just averaging the raw (signed) differences?**
A: If you just averaged the raw, signed differences (prediction minus actual), positive errors (over-predictions) and negative errors (under-predictions) would partially cancel each other out — a model that's wildly over-predicting on half the data and wildly under-predicting on the other half could show an average error near zero, looking deceptively good, even though every single prediction is actually quite wrong.

Squaring fixes this in two ways at once. First, squaring a negative number makes it positive, so errors in opposite directions no longer cancel out — every error contributes positively to the total, regardless of which direction it was wrong in. Second, squaring disproportionately penalizes large errors relative to small ones: an error of 2 contributes 4, but an error of 10 contributes 100 — twenty-five times more, even though the raw error is only five times larger. This deliberately makes the fitting process prioritize avoiding any single wildly-wrong prediction over being very slightly off on many predictions, which is usually the sensible behavior you actually want.

*One-liner: averaging raw signed errors lets positive and negative errors cancel out, hiding a model that's wrong in both directions; squaring makes every error positive (so they can't cancel) and disproportionately penalizes large errors over small ones, which is why MSE specifically discourages a model from being wildly wrong on any single point.*

**Q: What does an R² of 0.0 actually mean, and what does an R² of 1.0 mean — and what's the baseline R² is actually comparing against?**
A: R² is answering a specific comparative question: "how much better is my model than the simplest possible baseline, which is just always predicting the average of the target?" An R² of 0.0 means your model is doing exactly as well as that trivial baseline — despite whatever features and complexity your model has, it's providing zero additional predictive value over just guessing the mean every single time, regardless of the input.

An R² of 1.0 means your model's predictions perfectly match the actual values for every single example — zero error at all, explaining 100% of the variability in the target using your features. In practice, an R² of exactly 1.0 on real-world data is either a sign of an extremely clean, nearly-deterministic relationship, or (far more often) a red flag for something like data leakage or an unrealistically easy synthetic dataset, since real-world data almost always has some genuine, irreducible noise no model can perfectly predict away.

Values in between represent partial improvement over the baseline — an R² of 0.85 means your model's errors are collectively 85% smaller (in sum-of-squares terms) than the baseline "always guess the mean" model's errors would have been.

*One-liner: R² of 0.0 means the model provides zero predictive benefit over just guessing the target's average every time; R² of 1.0 means perfect prediction with zero error — the baseline it's always compared against is that trivial "always predict the mean" model, so R² literally measures how much better than guessing the average your model actually is.*

**Q: Why does Lasso regression perform feature selection (zeroing out some weights entirely), while Ridge regression doesn't?**
A: Both add a penalty term to the loss function that discourages large weights, but the specific *shape* of each penalty is different, and that shape difference is exactly what determines whether weights get driven all the way to zero or just shrunk smaller.

Ridge's penalty is based on the sum of squared weights — and because of how squaring works, the penalty gets smaller and smaller (in terms of how much further reduction it rewards) as a weight gets closer to zero; there's no strong additional reward for pushing a weight from "very small" all the way to "exactly zero." So Ridge tends to shrink all weights toward smaller values smoothly, without usually driving any of them to be exactly zero.

Lasso's penalty is based on the sum of the *absolute values* of the weights, not their squares — and the absolute-value penalty's rate of reduction stays constant all the way down to zero, rather than tapering off like the squared penalty does. This geometric difference means Lasso's optimization process genuinely has an incentive to push some weights all the way to exactly zero (rather than just very small), effectively eliminating those features from the model entirely — which is exactly what "feature selection" means here: the model itself decides some features aren't contributing enough to be worth keeping, and sets their influence to precisely zero.

*One-liner: Ridge's squared-weight penalty tapers off near zero (no strong extra incentive to go all the way to exactly zero), while Lasso's absolute-value penalty keeps a constant incentive all the way down — which is why Lasso's optimization can drive some weights to exactly zero (eliminating those features entirely), while Ridge only shrinks weights smaller without usually zeroing any out.*

**Q: You look at a residual plot and see a clear U-shaped curve rather than a random scatter — what does that tell you, and what's the fix?**
A: A residual plot shows the error (actual minus predicted) for each data point, typically plotted against the predicted value or against a feature. If the model's linear assumption were actually correct, the residuals should look like random, unstructured scatter around zero — no visible pattern, since whatever's left over after the linear model's predictions should just be genuine, unpredictable noise.

A clear U-shaped (or any systematically-shaped) pattern in the residuals means there's still real, predictable signal left over that the linear model failed to capture — specifically, a U-shape typically indicates the true relationship between the feature and the target is curved (quadratic-like), not actually a straight line, and the linear model is systematically under-predicting at the extremes and over-predicting in the middle (or vice versa) because it's forcing a straight line through data that doesn't actually follow one.

The fix: either add polynomial features (e.g., include `x²` as an additional feature alongside `x`, letting the model fit a curve rather than being restricted to a straight line), or switch to a model family that doesn't assume linearity at all (a tree-based model, for instance). The key diagnostic lesson here: a decent R² score alone doesn't guarantee the linear assumption is actually valid — checking the residual plot for structure is what actually reveals whether the model's core assumption about the relationship's shape is being violated.

*One-liner: a U-shaped residual pattern means real, predictable signal is left over that the model missed — specifically indicating the true relationship is curved, not linear, since the model is systematically over- or under-predicting at different ranges — the fix is adding polynomial features or switching to a non-linear model family, and this is exactly why checking residual plots (not just R²) matters for verifying the linearity assumption actually holds.*

**Q: Why is RMSE generally more useful to report to a non-technical stakeholder than raw MSE?**
A: MSE's units are the square of whatever your target's original units were — if you're predicting house prices in dollars, MSE is measured in squared dollars, which isn't a unit anyone has an intuitive feel for. A stakeholder hearing "our MSE is 4,000,000" has no immediate sense of whether that's a good or bad result, since squared dollars isn't something anyone reasons about naturally in everyday terms.

RMSE fixes this by taking the square root of MSE, which converts the units back to the original scale — in this example, back to plain dollars. An RMSE of 2,000 (the square root of 4,000,000) directly and intuitively means "our predictions are typically off by about $2,000" — a number anyone can immediately compare against the actual price range of the houses being predicted and judge whether that's a meaningfully small or large error for this specific context.

*One-liner: MSE's units are squared (squared dollars, squared degrees, and so on), which nobody has an intuitive feel for — RMSE takes the square root, converting back to the original, directly interpretable unit ("typically off by about $2,000"), which is why it's the more useful number to actually communicate to a stakeholder.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Machine Learning]]
- Related map: [[06 Maps of Content/Machine Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Machine Learning - Lesson 02 Introduction to Machine Learning]] · Downstream: [[02 Literature Notes/Courses/Machine Learning - Lesson 04 Classification and Its Applications]]
</content>
