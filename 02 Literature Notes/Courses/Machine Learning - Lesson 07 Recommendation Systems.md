# Machine Learning - Lesson 07 Recommendation Systems

> Depth goal: understand collaborative vs content-based filtering mechanically (including matrix factorization), why cold-start happens and how hybrids address it, and how to evaluate a recommender properly.

## Source
- Course: Machine Learning
- Lesson / Chapter: Lesson 07 - Recommendation Systems
- Resource: [[07 Resources Library/Machine Learning/Slides/Lesson_7_Knowledge_Checks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Machine Learning/Notebooks/7.01_Recommendation_Systems.ipynb]]

---

## 1. Mental Model

**A recommender system predicts what a user will like next, using one of two fundamentally different kinds of evidence: patterns across users ("people like you also liked X") or features of the items themselves ("this is similar in content to things you already liked").** These are **collaborative filtering** and **content-based filtering**, respectively, and most production systems combine both into a **hybrid** approach, since each compensates for the other's specific weaknesses.

> Key intuition: **collaborative filtering needs no understanding of *why* items are similar — just behavioral patterns across many users; content-based filtering needs no behavioral history at all — just features of the items.** This is exactly why they fail in opposite situations: collaborative filtering fails on brand-new items/users with no history yet (the **cold-start problem**); content-based filtering fails to capture non-obvious, surprising similarities that only emerge from real user behavior patterns.

---

## 2. How It Actually Works

### 2.1 Collaborative filtering
Collaborative filtering assumes: if two users agreed on many things in the past, they'll likely agree on new things too. **User-based** collaborative filtering finds users similar to you (by comparing rating/interaction patterns) and recommends what those similar users liked that you haven't seen yet. **Item-based** collaborative filtering instead finds items similar to ones you've already liked (by comparing which users tend to like both items together), and recommends those similar items — item-based tends to be more stable in practice, since item-to-item similarity patterns change more slowly over time than any individual user's evolving taste.

### 2.2 Matrix factorization
The classic mathematical formulation: represent all user-item interactions (ratings, purchases, clicks) as a large, mostly-empty matrix `R` (rows = users, columns = items, most cells are empty since no user interacts with most items). **Matrix factorization** approximates this matrix as the product of two much smaller matrices: `R ≈ U · Vᵀ`, where `U` (users × latent factors) and `V` (items × latent factors) are learned such that their product reconstructs the known, observed entries of `R` as closely as possible.

The "latent factors" here are not hand-designed features — they're abstract dimensions the model discovers on its own that happen to be useful for predicting ratings (for movies, a latent factor might end up loosely correlating with something like "how much action vs. drama" without ever being explicitly labeled that way). Once `U` and `V` are learned, predicting a specific user's rating for a specific unseen item is just computing the dot product of that user's row in `U` and that item's row in `V` — filling in the previously-empty matrix cell with a predicted value.

### 2.3 Content-based filtering
Content-based filtering represents each item by its own intrinsic features (a movie's genre, director, cast, plot keywords; a product's category, price, brand) and recommends items whose feature vectors are similar to items a specific user has already liked — using a similarity measure like cosine similarity between feature vectors, exactly as covered for text embeddings. This approach needs zero behavioral data from *other* users at all — it only needs to know what a specific user liked and what the available items' features actually are.

### 2.4 The cold-start problem
Collaborative filtering has a structural weakness: it needs behavioral history (ratings, interactions) to find patterns, so it fundamentally cannot make good recommendations for a **brand-new user** (no interaction history to compare against other users) or a **brand-new item** (no other user has interacted with it yet, so there's no collaborative signal connecting it to anything). This is the cold-start problem, and it's not a bug to be fixed within collaborative filtering — it's a structural limitation of what collaborative filtering fundamentally needs to work at all.

Content-based filtering doesn't have this exact same problem for new *items* — a brand-new item still has its own intrinsic features from day one, so it can immediately be compared against a user's known preferences even with zero interaction history for that specific item. This is precisely why hybrid systems combine both: fall back to content-based recommendations (or simple popularity-based defaults) for new users/items where collaborative filtering has no data to work with, and lean on collaborative filtering's richer, often more surprising recommendations once enough behavioral data accumulates.

### 2.5 Evaluating a recommender
Standard regression/classification metrics (RMSE on predicted ratings) measure *rating prediction accuracy*, but that's often not actually what matters for a real recommender product — what usually matters is **ranking quality**: did the system put genuinely good items near the *top* of the list a user actually sees, not just "did it predict ratings accurately across the board." This is why recommender evaluation often borrows ranking metrics similar to those covered in Retrieval Evaluation (precision@k, recall@k, NDCG) — checking whether the handful of items actually shown to a user (the top of the recommendation list) are good ones, rather than how accurate the system's predictions are on average across its entire, mostly-irrelevant catalog.

---

## 3. Implementation

Assumed stack: `numpy`, `scikit-learn`, `surprise` (optional, for a dedicated recommender library).

### Item-Based Collaborative Filtering from Scratch
```python
import numpy as np

# rows = users, columns = items; 0 = no interaction
ratings = np.array([
    [5, 4, 0, 1],
    [4, 0, 0, 1],
    [1, 1, 5, 4],
    [0, 0, 4, 5],
])

def cosine_sim_matrix(M):
    norm = M / (np.linalg.norm(M, axis=0, keepdims=True) + 1e-9)
    return norm.T @ norm   # item-item similarity

item_sim = cosine_sim_matrix(ratings)

def recommend_for_user(user_idx, k=1):
    user_ratings = ratings[user_idx]
    scores = item_sim @ user_ratings          # weight similar items by user's existing ratings
    scores[user_ratings > 0] = -1             # exclude already-rated items
    return np.argsort(scores)[::-1][:k]

print("recommend for user 0:", recommend_for_user(0))
```

### Matrix Factorization with Gradient Descent (toy implementation)
```python
import numpy as np

def matrix_factorization(R, k=2, epochs=500, lr=0.01, reg=0.02):
    n_users, n_items = R.shape
    rng = np.random.RandomState(0)
    U = rng.rand(n_users, k) * 0.1
    V = rng.rand(n_items, k) * 0.1
    mask = R > 0   # only train on known (observed) ratings
    for _ in range(epochs):
        pred = U @ V.T
        error = (R - pred) * mask
        U += lr * (error @ V - reg * U)
        V += lr * (error.T @ U - reg * V)
    return U, V

U, V = matrix_factorization(ratings.astype(float))
predicted = U @ V.T
print("predicted ratings (including previously-empty cells):\n", np.round(predicted, 2))
```

### Content-Based Filtering
```python
items = {"item_a": [1, 0, 1], "item_b": [1, 0, 0], "item_c": [0, 1, 0]}  # feature vectors
def cosine(a, b): return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

liked = np.array(items["item_a"])
for name, vec in items.items():
    if name != "item_a":
        print(name, "similarity to liked item_a:", round(cosine(liked, np.array(vec)), 3))
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Collaborative vs content-based** | Collaborative for rich, established behavioral data; content-based for cold-start items/users. |
| **User-based vs item-based collaborative** | Prefer item-based — item similarity is more stable over time than individual user taste. |
| **Matrix factorization vs neighborhood methods** | Matrix factorization scales better and captures subtler latent patterns on large, sparse datasets. |
| **Hybrid weighting** | Weight content-based higher for new items/users, collaborative higher once enough interaction data accumulates. |
| **Evaluation metric** | Use ranking metrics (precision@k, NDCG) over raw rating-prediction RMSE if what matters is top-of-list quality. |

---

## 5. Failure Modes & Gotchas

- Relying purely on collaborative filtering and failing badly on new users/items (cold start).
- Evaluating with RMSE alone when what actually matters is whether the top few recommendations are good.
- Treating latent factors from matrix factorization as if they have a clean, pre-defined real-world meaning.
- Ignoring popularity bias — collaborative filtering can over-recommend already-popular items, starving niche items of exposure.
- Not retraining/updating the model as new interactions accumulate, letting recommendations go stale.

---

## 6. Self-Check

1. Why does collaborative filtering fail on brand-new users and items, mechanically?
2. What does matrix factorization actually learn, and how is a missing rating predicted?
3. Why is item-based collaborative filtering generally more stable than user-based?
4. Why might RMSE on predicted ratings be the wrong metric for evaluating a real recommender?
5. How does a hybrid system actually combine collaborative and content-based signals?

---

## 7. Interview Q&A

**Q: Why does collaborative filtering structurally fail on brand-new users and brand-new items — walk through the actual mechanism, not just "it needs data"?**
A: Collaborative filtering's entire predictive signal comes from patterns in *existing* interactions — "users who rated these items similarly to you also rated this other item highly." For this signal to exist at all for a specific user, that user needs to have already rated or interacted with *some* items, so the system has something to compare against other users' patterns. A brand-new user, by definition, has zero interaction history — there's nothing in their row of the user-item matrix for the system to compare against anyone else's row at all. There's no pattern to match, because there's no data to form a pattern from in the first place.

The same logic applies symmetrically to brand-new items: for item-based collaborative filtering to know "this item is similar to that other item," it needs to see that the *same users* tend to interact with both items together — but a brand-new item, by definition, has zero users who've interacted with it yet, so there's no column of data connecting it to anything else in the matrix. It's mathematically isolated — nothing links it to any other item's pattern, because no behavioral signal involving it exists yet at all.

This is why cold start isn't a bug you can simply tune away within collaborative filtering itself — it's a direct, structural consequence of collaborative filtering's core assumption (patterns emerge from existing interactions) applied to a case where, by definition, no interactions yet exist.

*One-liner: collaborative filtering's signal comes entirely from existing interaction patterns, so a brand-new user has an empty row with nothing to compare against other users, and a brand-new item has an empty column with no users connecting it to any other item — in both cases there's simply no data yet for the pattern-matching mechanism to work with, which is a structural limitation of the approach itself, not a tunable bug.*

**Q: What does matrix factorization actually learn, and how does it predict a rating that was never actually observed?**
A: Matrix factorization learns two smaller matrices, `U` (one row per user) and `V` (one row per item), each row being a vector of "latent factors" — a set of numbers that don't individually correspond to any pre-defined, human-labeled feature (not literally "action-ness" or "price," though they can end up loosely correlating with such concepts) but that, when multiplied together appropriately, reconstruct the known, observed ratings as accurately as possible.

The training process works by only looking at the ratings that are actually known (observed) — it adjusts the numbers in `U` and `V` to make the dot product of a specific user's row and a specific item's row match that specific known rating as closely as possible, across every observed rating in the dataset, repeating this adjustment process (via gradient descent) until the reconstruction is as good as it can get. Critically, the *empty* cells (ratings that were never observed) are never directly used to adjust `U` and `V` during training — they're skipped entirely.

But once training is done, `U` and `V` are two complete, fully-populated matrices — every user has a learned row, every item has a learned row, with no gaps. To predict a rating that was *never* actually observed, you simply compute the dot product of that specific user's learned row in `U` and that specific item's learned row in `V` — the exact same operation used during training to reconstruct known ratings, just now applied to a user-item pair that had no actual observed rating to begin with. The prediction works because the latent factors were learned in a way that generalizes — if the training process successfully learned factors that make sense for a user's general taste and an item's general characteristics (based on all their *other* observed ratings), the dot product for a never-seen pair tends to produce a sensible prediction too, even though that specific pair was never directly part of training.

*One-liner: matrix factorization learns abstract latent-factor vectors for every user and every item, adjusted during training to make known ratings' dot products match their actual observed values — predicting a never-observed rating is just computing that same dot product for a new user-item pair, which works because the learned factors generalize from a user/item's other observed ratings to pairs that were never directly seen during training.*

**Q: Why is item-based collaborative filtering generally considered more stable than user-based collaborative filtering?**
A: Item-based filtering relies on item-to-item similarity — "users who liked item A also tended to like item B." A catalog's items (movies, products, songs) are typically far more stable over time than any individual user's evolving preferences are — a movie's genre, style, and the kind of audience it appeals to don't meaningfully change day to day, so the similarity relationship between two specific items tends to stay roughly consistent over long stretches of time, needing relatively infrequent recomputation to stay accurate.

User-based filtering instead relies on user-to-user similarity — "users similar to you." A user's taste genuinely can shift meaningfully over time (new interests, life changes, simply trying something different), and critically, a user's similarity to other users needs to be recomputed relative to the *entire, constantly-growing* population of other users — as new users join the system continuously, the pool of "similar users" to compare against is itself constantly shifting, in a way the comparatively static pool of items isn't. This makes user-based similarity calculations both computationally heavier to keep current (comparing against an ever-growing user base) and more volatile over time (since both the target user's own taste and the comparison population are both moving targets simultaneously), whereas item-based similarity has a comparatively more stable, slower-moving target to compute and maintain.

*One-liner: items (their inherent style, genre, characteristics) change far less over time than individual users' evolving tastes do, and item-to-item similarity only needs to be computed against a relatively stable catalog rather than against a constantly-growing, shifting population of other users — which is why item-based similarity stays more consistent and needs less frequent recomputation than user-based similarity.*

**Q: Why might RMSE on predicted ratings be the wrong metric to optimize for a real-world recommender system?**
A: RMSE measures how numerically close your predicted ratings are to the actual observed ratings, averaged across every single rating in your evaluation set — including ratings for items that are nowhere near the top of what you'd actually show a user. But a real recommender product typically only ever shows a user a short list — the top 5 or top 10 recommended items — meaning what genuinely matters for the actual user experience is whether *those specific top few items* are good, not whether your rating predictions are accurate on average across your entire catalog, most of which the user will never even see displayed to them.

Concretely: a model could have excellent RMSE overall (accurately predicting ratings across the bulk of the catalog) while still doing a mediocre job specifically at correctly identifying which handful of items deserve to be in the user's actual top-5 recommended list — getting the *relative ranking* at the very top wrong, even while being numerically accurate on average across everything else. Conversely, a model could have somewhat higher overall RMSE but nail the ranking of the top few items precisely, which is what a user actually experiences and judges the system by.

This is exactly why ranking-focused metrics (precision@k, recall@k, NDCG — borrowed from the same information-retrieval tradition covered in Retrieval Evaluation) are often more appropriate for evaluating a real recommender — they specifically measure "were the items actually shown to the user (the top of the ranked list) good ones," which is a more direct, honest proxy for the actual user-facing product experience than an average error computed across the entire, mostly-unseen catalog.

*One-liner: RMSE measures average rating-prediction accuracy across the whole catalog, but a real recommender only ever shows a user the top few items — a model can have great overall RMSE while still misranking exactly the handful of items a user actually sees, which is why ranking metrics (precision@k, NDCG) that specifically evaluate top-of-list quality are a more honest measure of real recommender performance than average prediction error.*

**Q: How does a hybrid recommender system actually combine collaborative and content-based signals in practice?**
A: There are a few common patterns, but the underlying principle across all of them is using each signal where it's actually strong and letting the other one cover the gap. One common approach: weighted blending — compute a score from the collaborative-filtering model and a separate score from the content-based model for the same candidate item, then combine them into one final score using a weighted sum, where the weight given to each signal can itself depend on context — for instance, giving content-based scoring a much heavier weight for a brand-new user or brand-new item (where collaborative filtering has essentially no real signal to offer at all), and shifting weight toward collaborative filtering as more interaction history accumulates for that specific user or item over time.

Another common pattern is a fallback/cascading structure rather than a blended weighted score: use collaborative filtering as the primary recommendation source whenever sufficient interaction data exists for a given user/item, but explicitly fall back to content-based recommendations (or simple, generic popularity-based defaults) specifically when collaborative filtering has insufficient data to produce a meaningful recommendation at all — rather than trying to blend a near-meaningless collaborative-filtering signal with a meaningful content-based one, simply switch to relying on content-based filtering alone until enough real behavioral data accumulates to make collaborative filtering genuinely useful.

Either way, the core idea is the same: recognize which signal is actually informative for a specific user/item pair right now (collaborative filtering needs sufficient interaction history to be informative at all; content-based filtering is available immediately, with zero need for behavioral history), and lean on whichever one is actually providing real, meaningful signal for that specific case.

*One-liner: a hybrid system either blends weighted scores from both models (shifting weight toward content-based for new users/items with little interaction history, and toward collaborative filtering as history accumulates) or uses collaborative filtering as the default with an explicit fallback to content-based/popularity defaults when collaborative filtering has insufficient data — either way, the core idea is leaning on whichever signal is actually informative for a specific user/item pair at that moment.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Machine Learning]]
- Related map: [[06 Maps of Content/Machine Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Machine Learning - Lesson 06 Unsupervised Learning]]
</content>
