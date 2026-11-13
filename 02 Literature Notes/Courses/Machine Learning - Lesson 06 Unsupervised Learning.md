# Machine Learning - Lesson 06 Unsupervised Learning

> Depth goal: understand K-Means' actual iterative mechanism, why DBSCAN handles non-spherical clusters K-Means can't, how PCA finds its components mathematically, and how to evaluate clustering without ground-truth labels.

## Source
- Course: Machine Learning
- Lesson / Chapter: Lesson 06 - Unsupervised Learning Algorithms
- Resource: [[07 Resources Library/Machine Learning/Slides/Lesson_6_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Machine Learning/Notebooks/6.1_Unsupervised_Learning_Algorithms.ipynb]]
  - [[07 Resources Library/Machine Learning/Notebooks/6.2_Unsupervised_Learning_Algorithms.ipynb]]

---

## 1. Mental Model

**Unsupervised learning finds structure in data with no labels to learn from — the model has to decide for itself what "interesting structure" even means, with nobody telling it the right answer.** This splits into two major tasks: **clustering** (group similar data points together) and **dimensionality reduction** (compress many correlated features into fewer, information-preserving ones).

Because there are no labels, you can't use accuracy/precision/recall to evaluate results — evaluation has to come from properties of the structure itself (how tight are the clusters, how much variance did the compression preserve), which is a fundamentally different and harder evaluation problem than supervised learning's.

> Key intuition: **clustering asks "which points are alike?" with no predefined notion of a category; dimensionality reduction asks "what's the minimal set of numbers that still captures what matters about this data?"** Both are about discovering structure the data already has, not imposing structure you already knew.

---

## 2. How It Actually Works

### 2.1 K-Means clustering
K-Means partitions data into `k` clusters (you choose `k` upfront) through an iterative two-step process:
1. **Assignment**: assign each point to the nearest of `k` cluster centers (centroids), by distance.
2. **Update**: recompute each centroid as the mean of all points currently assigned to it.

Repeat until centroids stop moving meaningfully. This is a form of the general **Expectation-Maximization** pattern — alternate between assigning points given current centroids (the "E" step) and recomputing centroids given current assignments (the "M" step) — and it's mathematically guaranteed to converge (the total within-cluster distance can only decrease or stay the same each iteration), though it can converge to a locally-optimal, not globally-optimal, clustering depending on where the centroids started. This is why K-Means is typically run several times with different random starting centroids, keeping the best result.

K-Means fundamentally assumes clusters are roughly spherical (equally sized in all directions) and similar in size — because it's purely distance-to-centroid based, it struggles badly with clusters that are elongated, nested, or very different in density or size.

### 2.2 DBSCAN
**DBSCAN** (Density-Based Spatial Clustering) takes a completely different approach: instead of assuming a fixed number of roughly-spherical clusters, it defines clusters as regions of high point density, separated by regions of low density. A point is a "core point" if it has at least `min_samples` other points within distance `eps` of it; clusters are formed by chaining together core points that are within `eps` of each other, and points reachable from a core point but not core themselves become "border points."

This directly solves two things K-Means can't handle: it finds clusters of *arbitrary shape* (since it's following density connectivity, not fitting to a centroid), and it has a built-in notion of **noise** — points that don't belong to any dense region are explicitly labeled as outliers rather than being forced into the nearest cluster regardless of fit, which is exactly what K-Means does to every single point, whether it genuinely belongs anywhere or not.

### 2.3 Hierarchical clustering
Hierarchical (agglomerative) clustering starts with every point as its own cluster, then repeatedly merges the two closest clusters, building up a tree (**dendrogram**) of nested clusters from the bottom up. Unlike K-Means, you don't have to choose `k` upfront — you can cut the dendrogram at any height to get however many clusters that cut produces, letting you explore multiple granularities of clustering from one computation.

### 2.4 Principal Component Analysis (PCA)
PCA compresses many (possibly correlated) features into fewer **principal components** — new, synthetic features that are linear combinations of the original ones, chosen specifically to capture as much of the data's total variance as possible using as few components as possible. The first principal component is the single direction in feature space along which the data varies the most; the second component is the direction of next-most variance, *constrained to be orthogonal (uncorrelated) to the first* — and so on.

Mechanically, PCA is computed via the eigenvectors of the data's covariance matrix: the eigenvector with the largest eigenvalue is the first principal component (the eigenvalue itself represents how much variance that direction captures). Projecting data onto the top few components compresses it while retaining most of its genuine variability — useful for visualization (compressing to 2-3 dimensions for plotting), noise reduction, and as a preprocessing step before a supervised model, especially when the original feature count is very high.

### 2.5 Evaluating unsupervised results (no ground truth available)
Without labels, you evaluate clustering using internal structural properties: **silhouette score** measures, for each point, how much closer it is to its own cluster's other points versus the nearest different cluster (ranging from -1, badly misclassified, to +1, well-clustered) — averaged across all points, it gives one number summarizing overall cluster quality. **Inertia** (within-cluster sum of squared distances to centroid) is used in the **elbow method** for choosing `k` in K-Means: plot inertia against increasing `k` and look for the point where adding more clusters stops producing much further improvement — the "elbow" of the curve.

---

## 3. Implementation

Assumed stack: `scikit-learn`.

### K-Means with the Elbow Method and Silhouette Score
```python
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.datasets import make_blobs

X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.8, random_state=0)

inertias, silhouettes = [], []
for k in range(2, 8):
    km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X, km.labels_))
    print(f"k={k}  inertia={km.inertia_:8.1f}  silhouette={silhouettes[-1]:.3f}")
# Look for the inertia "elbow" and the k with highest silhouette score.
```

### DBSCAN on Non-Spherical Clusters
```python
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_moons

X_moons, _ = make_moons(n_samples=300, noise=0.05, random_state=0)

km_labels = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(X_moons)
db_labels = DBSCAN(eps=0.2, min_samples=5).fit_predict(X_moons)
print("K-Means found clusters based on centroids (will split the moons incorrectly).")
print("DBSCAN cluster labels (−1 = noise):", set(db_labels))
```

### PCA for Dimensionality Reduction
```python
from sklearn.decomposition import PCA
from sklearn.datasets import load_digits

digits = load_digits()   # 64 features (8x8 pixel images)
pca = PCA(n_components=10).fit(digits.data)
print("variance explained by first 10 components:", pca.explained_variance_ratio_.sum().round(3))
# compressing 64 features down to 10 while retaining most of the variance
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **K-Means vs DBSCAN** | K-Means for roughly spherical, similarly-sized clusters with a known/estimable k; DBSCAN for arbitrary shapes, unknown cluster count, and outlier detection. |
| **Choosing k** | Use the elbow method (inertia) combined with silhouette score; don't rely on either alone. |
| **Hierarchical vs K-Means** | Hierarchical when you want to explore multiple granularities or don't want to commit to one k upfront; K-Means for speed at scale. |
| **PCA component count** | Choose based on cumulative explained variance (e.g., keep enough components to explain 90-95% of variance), not an arbitrary fixed number. |
| **Feature scaling** | Standardize features before K-Means, DBSCAN, and PCA — all are distance/variance-based and sensitive to feature scale. |

---

## 5. Failure Modes & Gotchas

- Running K-Means on non-spherical or very differently-sized clusters and getting a nonsensical partition.
- Forgetting to scale features before K-Means/DBSCAN/PCA, letting one large-magnitude feature dominate.
- Choosing `k` arbitrarily without checking the elbow curve or silhouette score.
- Setting DBSCAN's `eps` without exploring a range of values — too small finds too much noise, too large merges distinct clusters.
- Interpreting PCA components as having inherent real-world meaning rather than just directions of maximal variance.
- Using K-Means's forced cluster assignment as if it implies every point genuinely belongs somewhere, ignoring outliers.

---

## 6. Self-Check

1. Walk through K-Means' iterative assignment/update steps and explain why it's guaranteed to converge.
2. Why does K-Means struggle with non-spherical clusters, and why doesn't DBSCAN have this problem?
3. What is a principal component, mechanically — how is it actually computed?
4. How do you choose `k` for K-Means without ground-truth labels?
5. What's the difference between a core point, a border point, and noise in DBSCAN?

---

## 7. Interview Q&A

**Q: Walk through K-Means' iterative assignment/update process, and explain why it's mathematically guaranteed to converge.**
A: K-Means starts with `k` initial centroids (often placed randomly, or using a smarter initialization like k-means++). From there it alternates two steps repeatedly. Assignment: for every single data point, compute its distance to each of the `k` current centroids, and assign that point to whichever centroid is nearest. Update: for each cluster (the group of points just assigned to one centroid), recompute that centroid as the actual mean position of all the points now assigned to it — the centroid moves to sit at the center of its newly-assigned group.

Here's why this is guaranteed to converge: the algorithm's internal objective is the total within-cluster sum of squared distances (each point's squared distance to its assigned centroid, summed across all points) — call this the total "cost." The assignment step can only decrease or keep this cost the same, never increase it, because it's explicitly assigning each point to whichever centroid is nearest (minimizing that specific point's contribution to the cost, given the current centroids). The update step can also only decrease or keep the cost the same, because the mean of a set of points is mathematically the single point that minimizes total squared distance to all of them — moving the centroid to the mean of its assigned points is literally the best possible centroid position for that specific group, given the current assignment. Since both steps can only ever decrease (or hold steady) this total cost, and the cost can't go below zero, the process must eventually stop decreasing — at which point neither assignments nor centroid positions change anymore, and the algorithm has converged.

*One-liner: K-Means alternates assignment (each point joins its nearest centroid) and update (each centroid moves to the mean of its assigned points) — both steps can only decrease or hold steady the total within-cluster squared distance (never increase it), and since that cost can't go below zero, the process is mathematically guaranteed to eventually stop improving and converge, though possibly to a locally rather than globally optimal clustering.*

**Q: Why does K-Means struggle with non-spherical clusters, and why doesn't DBSCAN have this same problem?**
A: K-Means' entire mechanism is built around assigning each point to its *nearest centroid* — which implicitly assumes clusters are roughly circular/spherical blobs centered around a single point, since "distance to one central point" is only a meaningful way to define cluster membership when the cluster actually looks like a roughly round blob around that center. If the true clusters in your data are actually elongated, crescent-shaped, or one cluster wraps around another (nested), there's no single centroid position that correctly captures "belongs to this cluster" for shapes like these — K-Means will force a centroid-based partition onto the data regardless, producing a split that doesn't actually respect the data's true shape, since its underlying assumption (roughly spherical, centroid-definable clusters) simply doesn't hold.

DBSCAN doesn't have this problem because it never relies on centroids or any notion of "distance to a single central point" at all — it defines a cluster purely by *density connectivity*: a chain of points that are each close enough to their neighbors, regardless of what overall shape that chain traces out. A crescent-shaped cluster is handled perfectly fine by DBSCAN, because it's just following a dense, connected chain of nearby points along the crescent's shape — there's no assumption anywhere in the algorithm that a cluster needs to look like a blob around a center point. This is exactly why DBSCAN correctly separates genuinely non-spherical, interleaved shapes (like two interlocking crescents) that K-Means, with its centroid-distance assumption, cannot correctly separate.

*One-liner: K-Means assigns points by distance to a single centroid, which implicitly assumes clusters are roughly spherical blobs centered around one point — a non-spherical shape (a crescent, a ring) has no single centroid position that correctly captures membership; DBSCAN never uses centroids at all, instead following chains of densely-connected nearby points regardless of overall shape, which is exactly why it handles arbitrary cluster shapes K-Means structurally cannot.*

**Q: What is a principal component, mechanically — how is it actually computed, not just "the direction of most variance"?**
A: Start with the data's **covariance matrix** — a matrix capturing how every pair of features varies together across the dataset (how much feature A and feature B tend to increase or decrease together). This matrix fully describes the "shape" of how the data's variance is spread across all the original feature directions.

The principal components come from the **eigenvectors** of this covariance matrix — eigenvectors are special directions that, when you apply the covariance matrix's transformation to them, only get stretched or shrunk (not rotated) by some factor, called the corresponding **eigenvalue**. For a covariance matrix specifically, each eigenvector represents a direction in the original feature space, and its corresponding eigenvalue represents exactly how much of the data's total variance lies along that specific direction.

So, mechanically: compute the covariance matrix, find its eigenvectors and eigenvalues, then sort the eigenvectors by their eigenvalues in descending order. The eigenvector with the *largest* eigenvalue is the first principal component — literally the single direction in the original feature space along which the data's variance is greatest. The eigenvector with the second-largest eigenvalue, which is mathematically guaranteed to be orthogonal (at a perfect right angle, meaning completely uncorrelated) to the first, is the second principal component, and so on. Projecting your original data onto just the top few of these eigenvector directions (instead of keeping all the original features) gives you a compressed representation that retains as much of the data's genuine variability as mathematically possible for that number of dimensions.

*One-liner: principal components are the eigenvectors of the data's covariance matrix, ranked by their corresponding eigenvalues (which represent how much variance lies along each eigenvector's direction) — the eigenvector with the largest eigenvalue is the first component (the single direction of greatest variance), each subsequent component is the next-largest-variance direction that's mathematically guaranteed to be uncorrelated with all previous ones, and projecting data onto the top few of these components gives the best possible variance-preserving compression for that number of dimensions.*

**Q: How do you choose the number of clusters `k` for K-Means when you have no ground-truth labels to check against?**
A: Two complementary techniques, used together rather than relying on either alone. The elbow method: run K-Means across a range of candidate `k` values, and for each one, record the inertia (total within-cluster sum of squared distances). Inertia always decreases as `k` increases (more clusters means points are, on average, closer to their own assigned centroid) — but the *rate* of that decrease typically slows down sharply once `k` reaches somewhere near the genuine, natural number of clusters actually present in the data, since beyond that point you're just needlessly splitting genuinely coherent clusters into smaller artificial pieces for diminishing benefit. Plotting inertia against `k` and looking for the point where the curve bends from steep improvement to a flatter, slower improvement — the "elbow" — gives a candidate value for `k`.

Silhouette score provides a second, complementary check: for a given clustering, it measures, for each point, how much closer it is to the other points in its own assigned cluster versus the nearest different cluster, averaged across all points into one overall score (higher is better, ranging from -1 to +1). Computing this for each candidate `k` and picking the `k` with the highest silhouette score gives a second, independent signal for the right number of clusters, since it's measuring something genuinely different from inertia (cluster *separation and cohesion quality*, rather than just raw within-cluster distance, which inertia alone doesn't capture — inertia alone would always look "better" for a higher k, even when that higher k is actually producing worse, less-separated clusters).

Using both together — checking that a candidate `k` both sits near the elbow of the inertia curve *and* produces a strong silhouette score — gives more confidence than relying on either single metric in isolation, since each one captures a somewhat different aspect of cluster quality.

*One-liner: use the elbow method (plotting inertia against k, looking for where the rate of improvement sharply slows) combined with silhouette score (measuring actual cluster separation/cohesion quality, which inertia alone doesn't capture) — checking that a candidate k does well on both gives more confidence than relying on either single metric alone, since inertia keeps improving with higher k even when clusters are genuinely getting worse-separated.*

**Q: What's the difference between a core point, a border point, and a noise point in DBSCAN?**
A: A **core point** is a point that has at least `min_samples` other points (a parameter you choose) within distance `eps` (another chosen parameter) of it — it's sitting in a genuinely dense region of the data, surrounded by enough nearby neighbors to count as a solid, interior part of a cluster. Core points are the actual "skeleton" that clusters get built from — a cluster forms by connecting together core points that are within `eps` of each other, chaining through dense regions.

A **border point** doesn't itself have enough neighbors within `eps` to qualify as a core point on its own, but it does lie within `eps` of some core point — it's on the edge of a dense region, close enough to be legitimately pulled into that cluster, but not dense enough in its own immediate neighborhood to be a core, interior point itself. It gets assigned to whichever cluster its nearby core point belongs to.

**Noise** is any point that's neither a core point itself, nor close enough to any core point to be a border point — it's sitting in a genuinely sparse region, not meaningfully connected to any dense cluster at all. DBSCAN explicitly labels these points as noise/outliers (typically given a label like -1) rather than forcing them into the nearest cluster regardless of fit — a deliberate, built-in design choice that K-Means fundamentally lacks, since K-Means always assigns every single point to its nearest centroid, with no mechanism to say "this point doesn't really belong anywhere."

*One-liner: a core point has enough neighbors within `eps` to count as a solid, interior part of a dense region; a border point lacks enough neighbors of its own but is close enough to a core point to be pulled into that cluster's edge; noise is any point connected to neither, explicitly labeled an outlier rather than forced into a cluster it doesn't genuinely belong to — a built-in "doesn't belong anywhere" category K-Means structurally lacks.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Machine Learning]]
- Related map: [[06 Maps of Content/Machine Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Machine Learning - Lesson 05 Ensemble Learning]] · Downstream: [[02 Literature Notes/Courses/Machine Learning - Lesson 07 Recommendation Systems]]
</content>
