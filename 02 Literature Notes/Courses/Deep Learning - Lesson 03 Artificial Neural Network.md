# Deep Learning - Lesson 03 Artificial Neural Network

> Depth goal: understand a perceptron's actual computation, derive why non-linear activation functions are mathematically necessary (not just conventional), and know the practical tradeoffs between common activation functions.

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 03 - Artificial Neural Network
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_03_Artificial_Neural_Network.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Deep Learning/Notebooks/3.04_Perceptron_Based_Classification_Model.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/3.06_Configure_Neural_Network_and_Activation_Function.ipynb]]

---

## 1. Mental Model

**A perceptron is the basic computational unit of a neural network: take weighted inputs, sum them, pass the sum through an activation function.** This is literally the entire computation of a single artificial neuron: `output = activation(w₁x₁ + w₂x₂ + ... + wₙxₙ + b)`. A full neural network is just many of these units arranged in layers, each layer's outputs feeding into the next layer's inputs.

> Key intuition: **without a non-linear activation function, stacking any number of layers mathematically collapses into one single linear transformation — depth would buy you nothing.** This is why activation functions aren't a minor implementation detail; they're the single mathematical ingredient that makes "deep" actually mean something more powerful than "one big linear model."

---

## 2. How It Actually Works

### 2.1 The perceptron computation
A perceptron takes a vector of inputs `x = (x₁, ..., xₙ)`, multiplies each by a learned weight, sums them plus a learned bias term `b`, and passes the result through an activation function `f`:

$$\text{output} = f\left(\sum_{i=1}^{n} w_i x_i + b\right)$$

The weights `w` and bias `b` are what training actually learns — adjusting them so the network's final output gets closer to the correct answer across the training data. The original perceptron (historically) used a simple step function as its activation (output 1 if the sum exceeds a threshold, else 0) — this could only learn linearly-separable patterns (famously, it can't learn XOR), which is exactly the historical motivation for moving to richer, differentiable activation functions and multi-layer architectures.

### 2.2 Why activation functions must be non-linear (the actual math)
Suppose every layer in a network used no activation function at all (or, equivalently, a purely linear activation `f(z) = z`). Layer 1's output would be `W₁x + b₁`. Layer 2 would then compute `W₂(W₁x + b₁) + b₂ = (W₂W₁)x + (W₂b₁ + b₂)`. Notice: this is still just `W'x + b'` for some combined weight matrix `W' = W₂W₁` and combined bias `b' = W₂b₁ + b₂` — mathematically, two stacked linear layers collapse into one single equivalent linear layer, no matter how many layers you stack. A network of 100 purely linear layers is, mathematically, exactly equivalent to one single linear layer.

This is precisely why non-linear activation functions are mathematically necessary, not a stylistic convention: inserting a non-linear function between layers breaks this collapse — `f(W₂ f(W₁x + b₁) + b₂)` genuinely cannot be reduced to a single linear transformation when `f` is non-linear, which is exactly what allows depth to add real representational power rather than being a wasted, collapsible redundancy.

### 2.3 Common activation functions and their tradeoffs
- **Sigmoid**: `σ(z) = 1/(1+e^{-z})`, squashes output to (0, 1). Historically popular, but suffers from **vanishing gradients** — for large positive or negative inputs, the sigmoid curve flattens out almost entirely, making its derivative (needed for backpropagation) nearly zero, which stalls learning in deep networks (covered further in Lesson 07).
- **Tanh**: `tanh(z)`, squashes output to (-1, 1). Similar vanishing-gradient issue to sigmoid, but zero-centered output (which can help optimization slightly compared to sigmoid's always-positive output).
- **ReLU** (Rectified Linear Unit): `f(z) = max(0, z)`. The modern default for hidden layers — computationally cheap, and its gradient is either exactly 0 or exactly 1 (no vanishing-gradient flattening for positive inputs), which dramatically helps training deep networks. The tradeoff: a unit can get stuck permanently outputting 0 ("dying ReLU") if its weights end up in a region where its input is always negative, since the gradient there is exactly 0 with no way to recover.
- **Softmax** (for the output layer in multi-class classification): converts a vector of raw scores into a probability distribution that sums to 1 across all classes — this isn't applied per-neuron independently like the others; it's applied across the whole output layer jointly.

### 2.4 Decision boundaries
A single perceptron with a step or sigmoid activation can only carve out a single straight-line (linear) decision boundary in feature space — this is the direct consequence of its underlying computation being a linear combination of inputs before the activation squashes the result. Stacking multiple perceptrons into hidden layers, with non-linear activations between them, lets the network compose multiple linear boundaries into increasingly complex, curved decision regions — which is exactly the mechanism behind why multi-layer networks can solve problems (like XOR) that a single perceptron fundamentally cannot.

---

## 3. Implementation

Assumed stack: `numpy`, `tensorflow`/`keras`.

### A Single Perceptron from Scratch
```python
import numpy as np

def sigmoid(z): return 1 / (1 + np.exp(-z))

def perceptron(x, w, b):
    return sigmoid(np.dot(w, x) + b)

x = np.array([0.5, -0.2, 0.9])
w = np.array([0.4, 0.1, -0.3])
b = 0.1
print("perceptron output:", perceptron(x, w, b))
```

### Why Linear Layers Collapse Without Activation (demonstration)
```python
import numpy as np

rng = np.random.RandomState(0)
x = rng.randn(5)
W1, b1 = rng.randn(4, 5), rng.randn(4)
W2, b2 = rng.randn(3, 4), rng.randn(3)

# Two "linear-only" layers stacked
stacked_output = W2 @ (W1 @ x + b1) + b2

# Equivalent single combined linear layer
W_combined = W2 @ W1
b_combined = W2 @ b1 + b2
single_layer_output = W_combined @ x + b_combined

print("stacked output:     ", np.round(stacked_output, 6))
print("single-layer output:", np.round(single_layer_output, 6))
print("identical:", np.allclose(stacked_output, single_layer_output))
```

### Comparing Activation Functions
```python
import tensorflow as tf
import numpy as np

z = tf.constant(np.linspace(-5, 5, 5), dtype=tf.float32)
print("sigmoid:", tf.nn.sigmoid(z).numpy().round(3))
print("tanh   :", tf.nn.tanh(z).numpy().round(3))
print("relu   :", tf.nn.relu(z).numpy().round(3))
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Hidden layer activation** | ReLU as the default; consider variants (Leaky ReLU, GELU) if dying-ReLU is observed. |
| **Output layer activation** | Sigmoid for binary classification; softmax for multi-class; none (linear) for regression. |
| **Sigmoid/tanh usage today** | Mostly reserved for specific gate mechanisms (e.g., LSTM gates) rather than general hidden layers, due to vanishing gradients. |
| **Number of hidden units** | Start modest; increase only if validation performance shows under-capacity (underfitting). |

---

## 5. Failure Modes & Gotchas

- Using sigmoid/tanh throughout a deep network and encountering vanishing gradients that stall training.
- Forgetting an activation function entirely between layers, silently collapsing a deep network into an equivalent linear model.
- Dying ReLU units that get stuck outputting zero permanently, with gradient-based learning unable to recover them.
- Applying softmax to a binary classification problem (where sigmoid, not softmax, is the conventional and simpler choice).
- Assuming a single perceptron can solve any classification problem — it fundamentally cannot solve non-linearly-separable problems like XOR.

---

## 6. Self-Check

1. Write the perceptron equation and identify what training actually adjusts.
2. Prove, mathematically, why two linear layers stacked are equivalent to one linear layer.
3. Why does ReLU help with vanishing gradients compared to sigmoid/tanh?
4. What is "dying ReLU," and why does it happen?
5. Why can't a single perceptron solve XOR, and what does a multi-layer network add that fixes this?

---

## 7. Interview Q&A

**Q: Prove, with the actual math, why stacking two layers with no non-linear activation between them is mathematically equivalent to just one single layer.**
A: Write out what each layer actually computes. Layer 1, given input `x`, computes `h = W₁x + b₁` — a weight matrix multiplication plus a bias vector. Layer 2 takes that output `h` as its own input and computes `y = W₂h + b₂`. Substituting the first expression into the second: `y = W₂(W₁x + b₁) + b₂`.

Now just distribute the multiplication: `y = W₂W₁x + W₂b₁ + b₂`. Look closely at this final expression — `W₂W₁` is just some other matrix (the product of two matrices is itself a matrix), call it `W'`. And `W₂b₁ + b₂` is just some other vector (the sum of a matrix-vector product and another vector is itself a vector), call it `b'`. So the whole expression reduces to `y = W'x + b'` — which is exactly the same *form* as a single linear layer's output, just with a different (but perfectly computable in advance) weight matrix and bias vector.

This means that no matter how many purely linear layers you stack — two, ten, a hundred — the entire stack can always be collapsed down into one single equivalent linear layer, since each additional layer's weight matrix just multiplies into the running combined product, and each bias just adds into the running combined sum. Depth, in the absence of any non-linearity, buys you absolutely nothing beyond what one single layer could already represent — which is exactly the mathematical reason non-linear activation functions are a genuine necessity, not a stylistic choice.

*One-liner: layer 2's output, `W₂(W₁x + b₁) + b₂`, algebraically distributes to `(W₂W₁)x + (W₂b₁ + b₂)` — which is exactly the form of a single linear layer, with a combined weight matrix and combined bias — proving that any stack of purely linear layers collapses into one equivalent linear layer, which is precisely why non-linear activation functions are mathematically required for depth to add any real representational power at all.*

**Q: Why does ReLU help avoid vanishing gradients compared to sigmoid or tanh?**
A: Backpropagation (covered more fully in Deep Neural Network and Model Optimization) relies on the *derivative* (gradient) of each activation function to figure out how to adjust weights during training — this gradient has to actually flow backward through every layer, and if any layer's gradient is very close to zero, that near-zero value multiplies into the chain of gradients flowing backward through all the earlier layers too, shrinking the overall gradient signal that reaches those earlier layers.

Sigmoid and tanh both saturate (flatten out) for inputs that are sufficiently large in magnitude, in either the positive or negative direction — once the input is far enough from zero, the curve is nearly flat, meaning its derivative at that point is very close to zero. In a deep network, it's quite likely that at least some units, at some layers, will end up with inputs far enough into this flat region that their local gradient is tiny — and since gradients multiply together as they propagate backward through many layers, having even a handful of near-zero gradients along that backward path can shrink the overall gradient reaching early layers down to something vanishingly small, meaning those early layers' weights barely get updated at all during training — they stop learning effectively, even though they're just as important to the network's overall computation as any other layer.

ReLU's derivative is much simpler: exactly 1 for any positive input, and exactly 0 for any negative input — there's no gradual "squashing" or flattening region in between for positive inputs the way sigmoid/tanh have. For any unit whose input happens to be positive, its local gradient is a clean, full-strength 1, with no shrinkage at all — which means gradients flowing backward through ReLU units (for inputs on the positive side) don't get progressively diminished the way they do flowing through sigmoid/tanh's saturating curve. This is exactly why ReLU dramatically helps gradients propagate effectively through many layers in a deep network, compared to sigmoid/tanh.

*One-liner: sigmoid/tanh flatten out (saturate) for large-magnitude inputs, making their derivative nearly zero there, and since gradients multiply together across many layers during backpropagation, even a few near-zero local gradients can shrink the overall backward-flowing gradient to nearly nothing — ReLU's derivative is a clean, full-strength 1 for any positive input with no flattening region, which is why gradients propagate through ReLU units without the same progressive shrinkage.*

**Q: What is "dying ReLU," and why does it happen?**
A: ReLU's derivative is exactly 0 for any negative input — this is actually the useful, gradient-preserving property described above *for positive inputs*, but it has a specific downside on the negative side. If a particular unit's weights end up adjusted (through training) such that its input ends up negative for essentially every training example it ever sees, that unit's output is always 0 (since ReLU of any negative number is 0), and critically, its gradient is also always exactly 0 in that region.

Here's why this becomes permanent, rather than just a temporary phase: gradient-based learning updates a weight in proportion to its gradient — if the gradient is exactly 0, the weight update is also exactly 0, meaning that unit's weights never change again, no matter how much more training happens. The unit is permanently stuck outputting 0 for every input, contributing nothing useful to the network's computation ever again, with no mechanism within standard gradient descent to ever pull it back out of this state, since escaping would require the weights to change, but the weights only change in response to a nonzero gradient, which this unit will never produce again once stuck.

This typically happens from a combination of unlucky weight initialization, too large a learning rate causing a big, destabilizing weight update that pushes the unit into this always-negative-input regime, or simply an accumulation of training dynamics that happens to push a specific unit's weights into this dead zone. Mitigations include using a smaller, more careful learning rate, using a variant like Leaky ReLU (which allows a small, nonzero gradient even for negative inputs, specifically to avoid this permanent-zero trap), or using better weight initialization schemes designed to reduce the chance of units starting in or quickly falling into this regime.

*One-liner: dying ReLU happens when a unit's weights end up such that its input is negative for essentially every training example, making its output and gradient both permanently zero — since gradient descent can only change weights in response to a nonzero gradient, the unit gets permanently stuck contributing nothing, with no way to recover; mitigated by smaller learning rates, better initialization, or variants like Leaky ReLU that keep a small nonzero gradient on the negative side specifically to avoid this trap.*

**Q: Why can't a single perceptron solve the XOR problem, and what does a multi-layer network specifically add that fixes this?**
A: XOR (exclusive or) outputs true when exactly one of its two binary inputs is true, and false otherwise — plotted as points, the "true" outputs (at inputs (0,1) and (1,0)) and the "false" outputs (at inputs (0,0) and (1,1)) are arranged such that no single straight line can separate the true points from the false points — any line you draw will have at least one true point and one false point on the same side as each other, no matter how you position or angle it.

A single perceptron's decision boundary is, by its underlying math (a linear combination of inputs passed through an activation), always a single straight line (in 2D) or flat hyperplane (in higher dimensions) — it is structurally incapable of representing any decision boundary that isn't expressible this way. Since XOR's true/false regions require a boundary that isn't a single straight line (you'd need at least two lines, or a genuinely curved boundary, to correctly separate them), a single perceptron is mathematically incapable of ever learning XOR correctly, no matter how its weights are trained.

A multi-layer network fixes this precisely because of the composition mechanism covered earlier: with a hidden layer of multiple perceptron-like units, each with a non-linear activation, the network can learn several different linear boundaries in the hidden layer (each hidden unit learns its own line), and then the output layer combines these multiple linear boundaries together — effectively building a more complex, piecewise/curved decision region out of several individually-simple linear pieces. This composed, multi-piece boundary is exactly what's needed to correctly separate XOR's true and false regions, which is why adding even just one hidden layer with a couple of units is sufficient to solve XOR, where a single perceptron fundamentally cannot.

*One-liner: XOR's true/false regions can't be separated by any single straight line, but a single perceptron's decision boundary is always exactly that (a single line/hyperplane) — a multi-layer network fixes this by having a hidden layer learn several individual linear boundaries, which the output layer then composes together into a more complex, piecewise boundary capable of correctly separating XOR, which is structurally impossible for a single perceptron to represent no matter how it's trained.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 02 Introduction to Deep Learning]] · Downstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 04 Deep Neural Network]]
</content>
