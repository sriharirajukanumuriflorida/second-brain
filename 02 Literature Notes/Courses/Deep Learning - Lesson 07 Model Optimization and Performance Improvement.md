# Deep Learning - Lesson 07 Model Optimization and Performance Improvement

> Depth goal: trace the actual update rule for SGD, Momentum, AdaGrad, RMSProp, and Adam (not just their names), understand what problem each one specifically fixes over its predecessor, and understand Dropout's actual mechanism for reducing overfitting.

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 07 - Model Optimization and Performance Improvement
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_07_Model_Optimization_and_Performance_Improvement.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Deep Learning/Notebooks/7.03_Implementation_of_SGD.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/7.05_Implementation_of_Momentum.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/7.07_Implementation_of_AdaGrad.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/7.09_Implementation_of_RMSProp.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/7.11_Implementation_of_Adadelta.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/7.13_Implementation_of_Adam.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/7.18_Implementation_of_Dropout.ipynb]]

---

## 1. Mental Model

**Having a correct gradient (from backpropagation) only tells you the direction that reduces loss — the optimizer decides exactly how to use that gradient to actually update the weights, and this choice dramatically affects whether training converges quickly, slowly, or not at all.** Every optimizer in this lesson is a variation on the same basic idea (move weights in the direction that reduces loss), each one addressing a specific, identifiable weakness of the version before it — this isn't an arbitrary list of options; it's a genuine evolutionary sequence, each step fixing a concrete problem.

> Key intuition: **plain gradient descent treats every weight and every point in training identically; every improvement on top of it is some form of "remember something about the past, and use that memory to take a smarter step now" — whether that memory is about direction (Momentum) or about how much each specific weight has already moved (AdaGrad/RMSProp/Adam).**

---

## 2. How It Actually Works

### 2.1 Stochastic Gradient Descent (SGD) — the baseline
Plain gradient descent updates every weight by: `w = w - η · ∇L(w)`, where `η` (eta) is the **learning rate** (how big a step to take) and `∇L(w)` is the loss gradient with respect to `w`. "Stochastic" specifically refers to computing this gradient on a small random **mini-batch** of data rather than the entire dataset at once — this makes each individual step noisier (an approximation of the true gradient over all data) but allows far more frequent updates, which in practice usually trains faster overall and can even help escape shallow local minima due to that very noise.

The core weakness: a single, fixed learning rate applied identically to every weight, at every step, regardless of the loss surface's actual local shape — it can be too large (overshooting, oscillating) in steep regions and too small (painfully slow) in flat regions, with no mechanism to adapt.

### 2.2 Momentum — remembering direction
Momentum adds a "velocity" term that accumulates an exponentially-weighted moving average of past gradients, then uses that accumulated velocity (not just the current single gradient) to update weights:

$$v = \beta v + (1-\beta)\nabla L(w) \qquad w = w - \eta v$$

The intuition: imagine a ball rolling downhill — it doesn't instantly change direction every time the local slope changes slightly; it builds up momentum in a consistent direction. This specifically helps in narrow, curving "ravine" loss surfaces, where plain SGD tends to oscillate back and forth across the ravine's narrow walls rather than making steady progress along its length — momentum dampens that oscillation (since the oscillating components partially cancel out in the accumulated average) while reinforcing steady, consistent movement in the genuinely productive direction.

### 2.3 AdaGrad — adapting the learning rate per-weight
AdaGrad's insight: different weights may need genuinely different learning rates — a weight that's been receiving large gradients repeatedly (already moving a lot) probably needs a smaller step size going forward, while a weight receiving small, infrequent gradients might benefit from a relatively larger step. AdaGrad tracks a running *sum of squared past gradients* for each weight individually, and divides that weight's learning rate by (roughly) the square root of this accumulated sum — weights with large historical gradients get their effective learning rate shrunk, weights with small historical gradients keep a relatively larger effective rate.

The weakness: because it accumulates the sum of squared gradients *forever*, without ever forgetting old gradients, this denominator only ever grows — eventually, for any weight that's received substantial gradient activity, the effective learning rate shrinks toward zero and training effectively stalls, regardless of whether further learning would still be useful.

### 2.4 RMSProp — fixing AdaGrad's shrinking problem
RMSProp directly addresses AdaGrad's "learning rate shrinks forever" problem by using an *exponentially-weighted moving average* of squared gradients instead of an ever-growing cumulative sum — recent gradients matter more than very old ones, which naturally "forgets" stale gradient history rather than letting it accumulate without bound. This keeps the adaptive learning-rate mechanism's benefit (per-weight adaptation) while removing the specific flaw that caused training to stall prematurely.

### 2.5 Adam — combining Momentum and RMSProp
**Adam** (Adaptive Moment Estimation) combines both ideas: it tracks an exponentially-weighted moving average of past gradients (like Momentum, giving a sense of consistent direction) *and* an exponentially-weighted moving average of squared past gradients (like RMSProp, giving per-weight adaptive scaling), using both together to compute each update. This combination — direction-aware *and* adaptively-scaled per weight — is why Adam has become the practical default optimizer for most deep learning tasks: it's generally robust, converges quickly, and needs comparatively little learning-rate tuning compared to plain SGD.

### 2.6 Dropout — fighting overfitting, not optimization speed
Dropout is a regularization technique, not an optimizer — it addresses a different problem (overfitting/generalization) rather than training speed/stability. During training, Dropout randomly "turns off" (zeroes out) a fraction of neurons in a layer, for each training batch, forcing the network to not rely too heavily on any single specific neuron or narrow co-adapted group of neurons, since that neuron might be randomly absent on the next batch. This forces the network to learn more redundant, distributed representations — at test time, all neurons are active (dropout is turned off), typically with outputs scaled to account for the fact that more neurons are now contributing than during training.

---

## 3. Implementation

Assumed stack: `numpy` (to make each optimizer's update rule fully explicit), `tensorflow`/`keras`.

### SGD, Momentum, and Adam Update Rules Side by Side
```python
import numpy as np

def sgd_step(w, grad, lr=0.1):
    return w - lr * grad

def momentum_step(w, grad, v, lr=0.1, beta=0.9):
    v = beta * v + (1 - beta) * grad
    return w - lr * v, v

def adam_step(w, grad, m, v, t, lr=0.001, b1=0.9, b2=0.999, eps=1e-8):
    m = b1 * m + (1 - b1) * grad
    v = b2 * v + (1 - b2) * grad**2
    m_hat = m / (1 - b1**t)   # bias correction for early steps
    v_hat = v / (1 - b2**t)
    w = w - lr * m_hat / (np.sqrt(v_hat) + eps)
    return w, m, v

w, v_mom, m_adam, v_adam = 5.0, 0.0, 0.0, 0.0
for t in range(1, 6):
    grad = 2 * w   # toy loss: w^2, gradient = 2w
    w_sgd = sgd_step(w, grad)
    w_mom, v_mom = momentum_step(w, grad, v_mom)
    w_adam, m_adam, v_adam = adam_step(w, grad, m_adam, v_adam, t)
    print(f"step {t}  SGD={w_sgd:.4f}  Momentum={w_mom:.4f}  Adam={w_adam:.4f}")
```

### Dropout in Keras
```python
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dropout(0.3),    # randomly zero 30% of activations during training
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])
# model(x, training=True)  -> dropout active
# model(x, training=False) -> dropout inactive, all neurons used
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Default optimizer choice** | Adam as a robust first default; plain SGD (with momentum) sometimes generalizes slightly better with careful tuning, at the cost of more tuning effort. |
| **Learning rate** | Too high causes divergence/oscillation; too low causes painfully slow convergence — use learning rate schedules or adaptive optimizers to reduce manual tuning burden. |
| **Dropout rate** | 0.2-0.5 typical for hidden layers; too high degrades learning capacity, too low provides little regularization benefit. |
| **When to skip dropout** | Very small networks or already well-regularized setups (e.g., strong data augmentation) may not need it. |
| **Batch size** | Larger batches give more stable gradient estimates per step, but fewer total updates per epoch — tune jointly with learning rate. |

---

## 5. Failure Modes & Gotchas

- Using plain SGD with too large a learning rate, causing loss to oscillate or diverge entirely.
- Using AdaGrad on a long training run and watching the effective learning rate shrink to near-zero prematurely.
- Applying dropout at test/inference time, degrading predictions unnecessarily (dropout should only be active during training).
- Treating Adam's default hyperparameters as universally optimal without any validation-based tuning.
- Forgetting that dropout is a *regularization* technique, not an optimization-speed technique — it won't make training converge faster, and can slightly slow initial convergence in exchange for better generalization.

---

## 6. Self-Check

1. Write SGD's update rule and explain what specifically it fails to adapt to.
2. What problem does Momentum specifically fix, and how does its update rule fix it?
3. Why does AdaGrad's learning rate shrink toward zero over a long training run, and how does RMSProp fix this?
4. What does Adam combine from Momentum and RMSProp, and why does that combination matter?
5. How does Dropout actually reduce overfitting, mechanically?

---

## 7. Interview Q&A

**Q: Write SGD's update rule, and explain specifically what it fails to adapt to that later optimizers fix.**
A: `w = w - η∇L(w)` — the new weight is the old weight minus the learning rate times the gradient. This treats every single weight, at every single step of training, completely identically: the same learning rate `η` is applied uniformly, regardless of which specific weight is being updated, and regardless of what that weight's own gradient history has looked like so far.

This is exactly what later optimizers specifically improve on, in two different directions. First, SGD has no "memory" of its own recent direction — each step is based purely on the current gradient alone, with no consideration of which direction previous steps have been consistently moving in, which causes oscillation in narrow, curving loss-surface "ravines" (Momentum fixes this). Second, SGD applies the exact same learning rate to every weight, regardless of how much that specific weight has already been updated historically — a weight that's received many large gradients and one that's received few small gradients get treated identically, even though they may genuinely need different step sizes (AdaGrad, RMSProp, and Adam all fix this, in different ways, by adapting the effective learning rate per weight).

*One-liner: SGD applies the exact same learning rate to every weight at every step, using only the current gradient with no memory of past direction or past gradient magnitude per weight — Momentum fixes the lack of directional memory, while AdaGrad/RMSProp/Adam fix the lack of per-weight adaptive scaling, each addressing a different specific limitation of this one uniform, memoryless update rule.*

**Q: What specific problem does Momentum fix, and how does its update rule actually fix it?**
A: Picture a loss surface shaped like a narrow ravine — steep walls on either side, but only gently sloping along the ravine's actual length toward the minimum. Plain SGD, following the current gradient at each step, tends to zigzag back and forth across the ravine's steep walls (since the gradient there is large and keeps pointing it toward the opposite wall each time it overshoots), making comparatively little actual progress along the ravine's gently-sloping length, where the real progress toward the minimum needs to happen.

Momentum's fix: instead of using only the current gradient, it maintains a running, exponentially-weighted average of recent gradients (the "velocity" `v`), and updates weights using this averaged velocity rather than the raw current gradient alone: `v = βv + (1-β)∇L(w)`, then `w = w - ηv`. Here's why this specifically dampens the ravine-wall oscillation: the gradient components pointing back and forth across the ravine's walls tend to flip sign from one step to the next (pointing one way, then the opposite way, as SGD overshoots back and forth) — when averaged together over several recent steps, these oscillating, sign-flipping components partially *cancel out* in the running average. Meanwhile, the gradient component pointing steadily along the ravine's actual gently-sloping direction (toward the true minimum) doesn't flip sign between steps — it reinforces itself consistently in the running average, building up momentum in that one genuinely useful direction. The net effect: oscillation gets dampened while steady, productive progress gets amplified.

*One-liner: Momentum fixes oscillation in narrow, curving loss-surface "ravines" by averaging recent gradients instead of using only the current one — the oscillating, sign-flipping components (bouncing between the ravine's walls) cancel out in this running average, while the consistent component (steady progress along the ravine's actual direction toward the minimum) reinforces itself, dampening the oscillation while amplifying genuine progress.*

**Q: Why does AdaGrad's effective learning rate shrink toward zero over a long training run, and how does RMSProp specifically fix this?**
A: AdaGrad divides each weight's learning rate by (roughly) the square root of the *total sum of all that weight's squared gradients, accumulated since the very start of training* — every single past gradient, going all the way back to step 1, contributes to this ever-growing sum, and it never decreases, since squared values are always non-negative and get added, never subtracted.

Because this sum only ever grows larger (it's a running total that accumulates forever, with nothing ever removed from it), the denominator in AdaGrad's learning-rate adjustment keeps growing larger and larger as training proceeds — which means the effective learning rate for that weight keeps shrinking smaller and smaller, approaching zero as training goes on long enough, regardless of whether the weight's *recent* gradients still suggest useful, ongoing learning should be happening. Even if a weight's gradients in the last few steps are substantial and genuinely informative, the accumulated weight of all its *historical* gradients (going back potentially thousands of steps) can dominate the denominator, effectively freezing that weight's learning rate near zero long before training has actually converged.

RMSProp's fix: instead of an ever-growing *cumulative sum* of all past squared gradients, it uses an *exponentially-weighted moving average* of squared gradients — `v = βv + (1-β)∇L(w)²`. This moving average naturally gives more weight to recent gradients and progressively "forgets" the contribution of very old ones (since each old term gets multiplied by `β` again every subsequent step, shrinking its influence exponentially over time), which means the denominator used for scaling the learning rate reflects *recent* gradient activity for that weight, rather than an ever-accumulating, never-forgetting historical total — preventing the permanent, premature shrinkage-to-zero that plagues AdaGrad over long training runs.

*One-liner: AdaGrad's denominator is an ever-growing cumulative sum of every past squared gradient since training began, which only ever increases, eventually shrinking the effective learning rate toward zero regardless of whether recent gradients still suggest useful learning should continue — RMSProp fixes this by using an exponentially-weighted moving average instead, which naturally forgets old gradients and reflects recent activity, preventing the permanent premature shrinkage AdaGrad suffers from over long training runs.*

**Q: What does Adam combine from Momentum and RMSProp specifically, and why does that particular combination matter?**
A: Adam tracks two separate running statistics simultaneously for every weight: a moving average of the gradients themselves (exactly Momentum's mechanism — capturing a sense of consistent recent direction), and a moving average of the *squared* gradients (exactly RMSProp's mechanism — capturing how large recent gradients for this specific weight have tended to be, used to adaptively scale that weight's effective learning rate). Both of these running averages get updated every single step, and both are used together when computing the actual weight update.

Here's why combining both matters, rather than using just one: Momentum alone gives you directional consistency (dampening oscillation, building up steady progress) but still applies a globally shared learning rate to every weight, with no per-weight adaptation to how large or small that specific weight's gradients have tended to be. RMSProp alone gives you per-weight adaptive scaling but has no memory of consistent recent direction, so it doesn't get Momentum's specific oscillation-dampening benefit in ravine-shaped loss surfaces. Adam gets both benefits simultaneously: each weight's update direction benefits from Momentum's smoothing (reducing oscillation, building consistent progress), *and* each weight's effective step size is independently, adaptively scaled based on that specific weight's own recent gradient magnitude history (RMSProp's benefit). This combination of "smooth, consistent direction" plus "per-weight adaptive scaling" is exactly why Adam tends to converge quickly and robustly across a very wide range of problems with comparatively little manual tuning — it's getting the best of both of its predecessors' individual fixes at once, rather than needing to choose only one.

*One-liner: Adam tracks both a moving average of gradients (Momentum's directional-consistency mechanism) and a moving average of squared gradients (RMSProp's per-weight adaptive-scaling mechanism) simultaneously, using both together in every update — combining smooth, oscillation-dampened direction with per-weight adaptive step sizing is exactly why Adam converges robustly across a wide range of problems with comparatively little manual tuning, getting both predecessors' benefits at once rather than only one.*

**Q: How does Dropout actually reduce overfitting, mechanically — what's happening to the network during training that wouldn't happen otherwise?**
A: Without dropout, during training, neurons can develop a kind of unhealthy, over-specific "teamwork" — a specific neuron might learn to only be useful in tight combination with a few other very specific neurons, each compensating for the others' particular quirks, effectively **co-adapting** into a narrow, interdependent clique rather than each neuron learning something independently useful and robust on its own. This kind of narrow co-adaptation is exactly the sort of over-specific, fragile pattern that fits training data very well but doesn't generalize — these specific neuron cliques formed in response to this exact training set's particular quirks, and may not hold up on new, different data.

Dropout directly disrupts this: during each training batch, it randomly zeroes out a fraction of neurons in a layer — meaning any given neuron can't reliably count on any specific other neuron being present on the next batch to "cover for it" or to co-adapt with, since that neuron might simply be randomly absent next time. This forces every neuron to learn to be independently useful on its own, contributing meaningfully to the network's overall output regardless of which specific other neurons happen to be active alongside it on any given batch — rather than developing a narrow, fragile dependency on one specific set of co-adapted partners.

The practical effect, conceptually, is similar to training many different "thinned" sub-networks (each batch effectively trains a different random subset of the full network) and then, at test time (with dropout turned off and all neurons active), getting something like an implicit average over all those different thinned sub-networks' behavior — a form of built-in ensembling that tends to generalize better than any single, fully-connected network trained without this randomized interruption ever would.

*One-liner: without dropout, neurons can develop narrow, over-specific co-adaptations with a few specific other neurons, fitting training data's particular quirks in a fragile, non-generalizing way — dropout randomly zeroes out neurons each batch, preventing any neuron from reliably depending on specific co-adapted partners being present, forcing each one to be independently useful, which (conceptually) acts like training and implicitly averaging many different thinned sub-networks, producing better generalization than one fully-connected network trained without this disruption.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 06 PyTorch]] · Downstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 08 Convolutional Neural Networks]]
- Related permanent note: [[03 Permanent Notes/Optimization Shapes How Neural Networks Learn]]
</content>
