# Machine Learning - Lesson 04 Classification and Its Applications

> Depth goal: understand the major classification algorithms' core mechanisms (not just their names), evaluation metrics and why accuracy misleads on imbalanced data, and how SMOTE actually fixes class imbalance.

## Source
- Course: Machine Learning
- Lesson / Chapter: Lesson 04 - Classification and Its Applications
- Resource: [[07 Resources Library/Machine Learning/Slides/Lesson_4_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Machine Learning/Notebooks/4.1_Classification_and_Its_Applications_Part_1.ipynb]]
  - [[07 Resources Library/Machine Learning/Notebooks/4.2_Classification_and_Its_Applications_Part_2.ipynb]]
  - [[07 Resources Library/Machine Learning/Notebooks/4.3_Classification_and_Its_Applications_Part_3.ipynb]]

---

## 1. Mental Model

**Classification predicts a discrete category (not a number) for each input — binary (fraud / not fraud) or multiclass (which of 5 product categories).** Where regression's output lives on a continuous number line, classification's output lives in a finite set of labeled buckets, and that structural difference drives everything downstream: a different loss function (probability-based, not distance-based), different model internals (decision boundaries instead of a fitted line), and different evaluation metrics (precision/recall instead of MSE/R²).

> Key intuition: **most classifiers don't just output a label — they output a probability for each class, then pick the most likely one.** This is why you can tune a classifier's threshold, why "confidence" is a meaningful concept here, and why accuracy alone is a dangerously incomplete way to judge one.

---

## 2. How It Actually Works

### 2.1 Logistic regression — the probabilistic baseline
Despite the name, logistic regression is a classification algorithm. It computes a linear combination of features (`w·x + b`), then squashes that through the **sigmoid function** to produce a probability between 0 and 1:

$$p = \sigma(w \cdot x + b) = \frac{1}{1 + e^{-(w \cdot x + b)}}$$

If `p > 0.5` (the default threshold), predict the positive class; otherwise predict the negative class. The sigmoid's S-shape means the model is highly confident (probability near 0 or 1) when the linear combination is far from zero in either direction, and uncertain (probability near 0.5) near the decision boundary. Training minimizes **log loss** (cross-entropy), which heavily penalizes confident-but-wrong predictions.

### 2.2 Decision trees
A decision tree asks a sequence of yes/no questions about feature values ("is income > $50k?"), splitting the data at each step into increasingly pure (single-class-dominant) groups, until it reaches a leaf that assigns a final class. Splits are chosen to maximize purity gain (using metrics like **Gini impurity** or **entropy**). Trees are easy to interpret (you can literally read off the decision path) but prone to overfitting if grown too deep — they'll keep splitting until each leaf has a single noisy training example, memorizing rather than generalizing.

### 2.3 k-Nearest Neighbors (k-NN)
k-NN has no real "training" step at all — it just stores the entire training set. To classify a new point, it finds the `k` closest training points (by some distance metric, usually Euclidean) and takes a majority vote among their labels. Simple and intuitive, but slow at prediction time (every prediction scans the whole dataset) and sensitive to feature scaling (distances are dominated by whichever feature has the largest numeric range, unless features are standardized first).

### 2.4 Support Vector Machines (SVM)
SVM finds the decision boundary (hyperplane) that maximizes the **margin** — the distance between the boundary and the nearest points of each class (the "support vectors"). A wider margin tends to generalize better. With the **kernel trick**, SVMs can also model non-linear decision boundaries by implicitly mapping data into a higher-dimensional space where a linear separator does exist, without ever explicitly computing that higher-dimensional transformation.

### 2.5 Naive Bayes
Naive Bayes applies Bayes' theorem, assuming (naively, hence the name) that all features are conditionally independent given the class — an assumption that's rarely exactly true, but the algorithm often still works surprisingly well in practice, especially for text classification (spam detection, sentiment analysis), because it's fast, needs little data, and the independence assumption's violations often don't hurt the final classification decision much.

### 2.6 Evaluation: why accuracy misleads
**Accuracy** (fraction of correct predictions) is the most intuitive metric, but it's dangerously misleading on **imbalanced** datasets — where one class vastly outnumbers another. A fraud-detection model that always predicts "not fraud" on a dataset that's 99% legitimate transactions gets 99% accuracy while catching exactly 0% of fraud, which is a completely useless model.

This is why **precision**, **recall**, and **F1** exist: given a confusion matrix of true positives (TP), false positives (FP), true negatives (TN), and false negatives (FN):

$$\text{Precision} = \frac{TP}{TP + FP} \qquad \text{Recall} = \frac{TP}{TP + FN} \qquad F1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

Precision answers "of everything I flagged as positive, how much was actually positive?" Recall answers "of everything that was actually positive, how much did I actually catch?" There's an inherent tradeoff between them (tuned by adjusting the classification threshold), and F1 is their harmonic mean — a single number balancing both, which punishes a model that's extremely strong on one but weak on the other more than a plain average would.

### 2.7 Class imbalance and SMOTE
Imbalanced classes (99:1 ratio, say) push a naive model toward always predicting the majority class, since that alone already achieves high accuracy. Fixes include: **class weighting** (penalize mistakes on the minority class more heavily during training), **random oversampling/undersampling** (duplicate minority examples or discard majority ones), and **SMOTE** (Synthetic Minority Oversampling Technique) — which specifically generates *new, synthetic* minority-class examples rather than duplicating existing ones, by picking a minority point, finding its nearest minority-class neighbors, and creating new synthetic points along the line segments between them. This adds genuine variety to the minority class (rather than just reinforcing identical duplicate points, which risks overfitting to those exact points), making the model learn a more general minority-class boundary.

---

## 3. Implementation

Assumed stack: `scikit-learn`, `imbalanced-learn`.

### Comparing Classifiers on the Same Data
```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report

X, y = make_classification(n_samples=500, n_features=10, weights=[0.9, 0.1], random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)

models = {
    "LogReg": LogisticRegression(),
    "Tree": DecisionTreeClassifier(max_depth=5),
    "kNN": KNeighborsClassifier(n_neighbors=5),
    "SVM": SVC(),
    "NaiveBayes": GaussianNB(),
}
for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    report = classification_report(y_test, preds, output_dict=True, zero_division=0)
    print(f"{name:>10}  precision={report['1']['precision']:.2f}  recall={report['1']['recall']:.2f}  f1={report['1']['f1-score']:.2f}")
```

### SMOTE for Imbalanced Classification
```python
from imblearn.over_sampling import SMOTE
from collections import Counter

print("before:", Counter(y_train))
X_resampled, y_resampled = SMOTE(random_state=0).fit_resample(X_train, y_train)
print("after :", Counter(y_resampled))

model = LogisticRegression().fit(X_resampled, y_resampled)
preds = model.predict(X_test)
print(classification_report(y_test, preds, zero_division=0))
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Which algorithm** | Logistic regression/SVM for linearly-separable or moderate data; trees/ensembles for structured, tabular data with non-linear patterns; Naive Bayes for fast text baselines. |
| **k-NN feature scaling** | Always standardize features before k-NN; unscaled features distort distance calculations. |
| **Metric to optimize** | Precision when false positives are costly (spam filter blocking real email); recall when false negatives are costly (missing a cancer diagnosis). |
| **Imbalance handling** | SMOTE for genuine synthetic diversity; class weighting as a simpler first attempt; avoid blind random oversampling (duplicates risk overfitting). |
| **Threshold tuning** | Default 0.5 threshold is arbitrary — tune it against your actual precision/recall priorities using a validation set. |

---

## 5. Failure Modes & Gotchas

- Reporting accuracy alone on an imbalanced dataset, hiding a model that never predicts the minority class.
- Running k-NN on unscaled features, letting one large-magnitude feature dominate distance calculations.
- Growing a decision tree to full depth with no pruning, memorizing training noise.
- Applying SMOTE before the train/test split, leaking synthetic points derived from test data into training.
- Assuming Naive Bayes' independence assumption is literally true rather than a useful approximation.
- Picking the model with the highest F1 without checking whether precision or recall actually matters more for the specific business problem.

---

## 6. Self-Check

1. Why is accuracy a misleading metric on imbalanced data — give a concrete example.
2. Write precision and recall and explain what each answers.
3. How does SMOTE differ from simple random oversampling?
4. Why must features be scaled before k-NN but not before a decision tree?
5. What is the kernel trick, and what does it let an SVM do?

---

## 7. Interview Q&A

**Q: Why is accuracy a misleading metric specifically on imbalanced datasets — walk through a concrete example?**
A: Accuracy just measures "what fraction of all predictions were correct" — and that single number treats every class equally, with no regard for how common each class actually is in the data. On a balanced dataset (roughly equal numbers of each class), this is a reasonable, intuitive measure. But on an imbalanced dataset, it becomes trivially gameable by a model that does something genuinely useless.

Concrete example: a fraud-detection dataset where 99% of transactions are legitimate and only 1% are actually fraudulent. A model that simply predicts "not fraud" for every single transaction, regardless of any actual pattern in the data, gets 99% accuracy — since it's correct on all the legitimate transactions (99% of the data) and only wrong on the fraudulent ones (1% of the data). That 99% accuracy sounds impressive, but this model has caught exactly zero fraud cases, which is the entire actual point of building it in the first place. The accuracy number is technically true but completely fails to reveal that the model is useless for its actual purpose.

This is exactly why precision and recall exist — they specifically look at how the model performs *on the minority class that actually matters*, rather than blending that performance into one number dominated by the much larger majority class.

*One-liner: accuracy blends performance across all classes into one number, which a model can game on imbalanced data by just always predicting the majority class — a fraud detector that always says "not fraud" gets 99% accuracy on a 99%-legitimate dataset while catching zero actual fraud, which is exactly why precision/recall (focused specifically on minority-class performance) are needed instead.*

**Q: Write precision and recall, and explain, in plain terms, what question each one is actually answering.**
A: Precision is `TP / (TP + FP)` — true positives divided by everything the model actually flagged as positive (true positives plus false positives). It's answering: "of everything I flagged as positive, how much of it was genuinely positive?" A low precision means the model is crying wolf a lot — flagging many things as positive that actually weren't, generating a lot of false alarms.

Recall is `TP / (TP + FN)` — true positives divided by everything that was actually, truly positive (true positives plus false negatives, the positives the model missed). It's answering: "of everything that was genuinely positive, how much did I actually catch?" A low recall means the model is missing a lot of real positive cases, letting them slip through undetected.

These pull in different directions because of how a classifier actually works: making a model flag *more* things as positive (lowering its threshold for calling something positive) will generally catch more of the true positives (raising recall) but also flag more false alarms along the way (lowering precision) — and vice versa. Which one matters more depends entirely on the real-world cost of each type of mistake: a spam filter wants high precision (don't block real, important email as a false alarm); a cancer screening test wants high recall (don't miss a real case, even if that means some unnecessary follow-up tests on healthy people).

*One-liner: precision asks "of what I flagged as positive, how much was actually positive" (low precision = too many false alarms); recall asks "of everything actually positive, how much did I catch" (low recall = missing real cases) — they trade off against each other as you adjust a classifier's threshold, and which one matters more depends on whether false alarms or missed cases are more costly for your specific problem.*

**Q: How does SMOTE differ from simply duplicating minority-class examples (random oversampling), and why does that difference matter?**
A: Random oversampling fixes class imbalance by literally duplicating existing minority-class rows until the classes are more balanced in count — but every duplicate is an exact copy of an existing point, adding no new information at all, just repeated weight on the exact same specific examples.

This creates a real risk: if the model is trained on many exact copies of the same few minority points, it can end up overfitting specifically to those exact points — learning to recognize those particular examples very precisely, rather than learning the broader, more general pattern that distinguishes the minority class from the majority class across the whole range of what minority-class examples could look like.

SMOTE instead generates genuinely new, synthetic minority-class points: it picks an existing minority point, finds its nearest minority-class neighbors (points similar to it, also minority class), and creates new synthetic points that sit somewhere along the straight line between the original point and its neighbors — new points that didn't exist before, but that plausibly represent the kind of minority-class example that could exist in that same region of the feature space. This adds genuine variety and coverage to the minority class, rather than just reinforcing identical copies of the exact same handful of points, which gives the model a better chance of learning the minority class's actual underlying pattern rather than memorizing a small set of specific examples.

*One-liner: random oversampling duplicates exact copies of existing minority points, risking overfitting to those specific examples since no new information is added — SMOTE instead generates genuinely new synthetic points along the line between existing minority points and their nearest minority neighbors, adding real variety and coverage to the minority class rather than just reinforcing identical duplicates.*

**Q: Why must features be scaled before using k-NN, but a decision tree doesn't have this same requirement?**
A: k-NN's entire mechanism depends directly on computing a distance (typically Euclidean distance) between data points — and that distance calculation treats every feature's raw numeric value as directly comparable to every other feature's raw numeric value. If one feature (say, income, ranging from $20,000 to $200,000) has a much larger numeric range than another feature (say, age, ranging from 20 to 80), the income feature will completely dominate the distance calculation purely because its raw numbers are bigger — not because income is actually more important for determining which points are "close" to each other in any meaningful sense. Without scaling (standardizing each feature to a comparable range, typically mean 0 and standard deviation 1), k-NN's notion of "nearest neighbors" ends up being distorted by which features happen to have larger raw numeric ranges, regardless of their actual relevance.

A decision tree works completely differently — at each split, it asks a question about one single feature at a time ("is income greater than $50,000?") and evaluates how well that specific split separates the classes, using a purity measure (like Gini impurity) that only depends on the resulting class proportions in each branch, not on the feature's raw numeric scale at all. Whether income is measured in dollars or in thousands of dollars, the question "is income above this specific threshold" and the resulting split quality are exactly the same — the tree's splitting logic is scale-invariant, since it only ever compares a feature against its own threshold, never against a different feature's raw numeric value the way a distance calculation does.

*One-liner: k-NN computes distances across all features together, so a feature with a larger raw numeric range dominates that distance calculation regardless of its actual relevance, requiring scaling to put every feature on a comparable footing — a decision tree only ever compares one feature against its own threshold at each split, never mixing raw values across different features, making its splitting logic scale-invariant and requiring no scaling at all.*

**Q: What is the "kernel trick" in an SVM, and what capability does it actually unlock?**
A: A plain, basic SVM finds a straight-line (or flat hyperplane, in higher dimensions) boundary that separates two classes — which only works well if the classes are actually separable by something close to a straight line in the original feature space. Many real datasets have classes that are tangled together in a way no straight line can cleanly separate — imagine one class forming a ring around the other; no single straight line in that 2D space could ever separate them correctly.

The kernel trick's insight: a problem that isn't linearly separable in its original space might become linearly separable if you transform the data into a higher-dimensional space first — in the ring example, if you add a new dimension representing distance from the center, the two classes might become cleanly separable by a flat plane in this new, higher-dimensional space, even though no line worked in the original 2D space. Explicitly computing this transformation for every data point could be extremely expensive for a sufficiently rich transformation, especially one mapping to very high (or infinite) dimensions.

The kernel trick lets you get the *effect* of this higher-dimensional separation, mathematically, without ever actually computing the explicit transformation — specific kernel functions (like the RBF/Gaussian kernel) can compute what the similarity between two points *would be* in that higher-dimensional space, directly from the original, lower-dimensional data, skipping the expensive explicit transformation step entirely while still getting its benefit: an SVM that can find non-linear decision boundaries in the original space, even though internally it's still just finding a linear separator, just in an implicitly-computed higher-dimensional space.

*One-liner: the kernel trick lets an SVM find non-linear decision boundaries by implicitly computing what similarity between points would look like in a higher-dimensional space (where a linear separator might actually exist), without ever having to explicitly compute that expensive higher-dimensional transformation directly — getting the benefit of non-linear separation at the computational cost of a linear one.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Machine Learning]]
- Related map: [[06 Maps of Content/Machine Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Machine Learning - Lesson 03 Supervised Learning and Regression]] · Downstream: [[02 Literature Notes/Courses/Machine Learning - Lesson 05 Ensemble Learning]]
</content>
