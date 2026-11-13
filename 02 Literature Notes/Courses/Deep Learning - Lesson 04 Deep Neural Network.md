# Deep Learning - Lesson 04 Deep Neural Network

> Depth goal: trace forward propagation precisely layer by layer (shapes, matrix math), and understand backpropagation's chain-rule mechanism well enough to explain why depth makes training harder, not just more powerful.

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 04 - Deep Neural Network
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_04_Deep_Neural_Network.pdf]]
- Related Notebook:
  - [[07 Resources Library/Deep Learning/Notebooks/4.04_Example__Working_on_Forward_Propagation.ipynb]]

---

## 1. Mental Model

**A deep neural network is a sequence of perceptron-style layers, each consuming the previous layer's output and producing a new representation; forward propagation is the mechanical process of computing a prediction by pushing an input through this entire sequence, layer by layer.** This lesson is about making that mechanism completely explicit — the actual shapes, the actual matrix multiplications — since Lesson 03 introduced one perceptron's math, and here it's a full multi-layer stack.

> Key intuition: **forward propagation computes a prediction; backpropagation (covered more fully in Model Optimization) computes how to improve the weights that produced that prediction, by running the same chain of computations in reverse.** Understanding forward propagation precisely is the prerequisite for understanding why backpropagation works the way it does — you can't meaningfully reverse a computation you haven't traced forward step by step first.

---

## 2. How It Actually Works

### 2.1 Forward propagation, layer by layer
For a network with `L` layers, forward propagation computes, for each layer `l` from 1 to `L`:

$$z^{[l]} = W^{[l]} a^{[l-1]} + b^{[l]} \qquad a^{[l]} = f^{[l]}(z^{[l]})$$

where `a^[0]` is just the raw input `x`, `W^[l]` and `b^[l]` are layer `l`'s learned weight matrix and bias vector, `z^[l]` is layer `l`'s pre-activation (the linear combination before the activation function is applied), `f^[l]` is layer `l`'s activation function, and `a^[l]` is layer `l`'s final output — which becomes the input to layer `l+1`. The final layer's output `a^[L]` is the network's prediction. This is exactly the same single-perceptron computation from Lesson 03, just applied repeatedly, with each layer's output becoming the next layer's input.

### 2.2 Shapes matter — a common source of real bugs
If layer `l` has `n_l` units, `W^[l]` has shape `(n_l, n_{l-1})` — one row per output unit, one column per input from the previous layer. `b^[l]` has shape `(n_l,)`. Getting these shapes wrong (a transposed weight matrix, a mismatched dimension between consecutive layers) is one of the most common practical bugs when implementing a network from scratch — the matrix multiplication will either fail outright (shape mismatch error) or, worse, silently succeed with broadcasting in a way that produces a technically-runnable but mathematically wrong computation.

### 2.3 Backpropagation, at a conceptual level
Training needs to answer: "for each weight in the network, if I nudge it slightly, how much does the final loss change?" This is the **gradient** of the loss with respect to each weight, and computing it requires the **chain rule** from calculus, applied repeatedly backward through the network — hence "back"-propagation. Conceptually: compute the gradient of the loss with respect to the final layer's output first (easy, since that's directly compared to the true label), then use the chain rule to work out the gradient with respect to the final layer's weights, then propagate the gradient signal backward one more layer, repeating all the way back to the first layer.

The key insight that makes this computationally tractable rather than hopelessly expensive: each layer's local gradient calculation only needs the gradient signal arriving from the layer *after* it, plus that layer's own local computation — you never need to recompute everything from scratch for each layer; you reuse the backward-flowing gradient signal, layer by layer, which is exactly why backpropagation is efficient enough to actually train deep networks in practice.

### 2.4 Why depth increases training difficulty
Because backpropagation's gradient signal has to flow all the way backward through every single layer, multiplying by each layer's own local gradient along the way, any systematic tendency for these per-layer gradients to be small (as with saturating activations like sigmoid/tanh, covered in Lesson 03) compounds multiplicatively across many layers — this is the **vanishing gradient problem**, where gradients reaching early layers in a very deep network become vanishingly small, stalling their learning. The opposite failure, **exploding gradients**, happens when per-layer gradients are systematically large, compounding into enormous updates that destabilize training. Both are direct consequences of how many multiplicative steps the gradient has to pass through — a problem that simply doesn't exist (or exists far less severely) for shallow, single-layer models, which is exactly why "just add more layers" isn't free additional power — it comes with a genuine optimization cost that needs to be actively managed (covered fully in Model Optimization and Performance Improvement).

---

## 3. Implementation

Assumed stack: `numpy` (to make the shapes and computation fully explicit).

### Forward Propagation Through a 3-Layer Network
```python
import numpy as np

def relu(z): return np.maximum(0, z)
def sigmoid(z): return 1 / (1 + np.exp(-z))

def forward_propagation(x, params):
    a = x
    for l in range(1, len(params) + 1):
        W, b, activation = params[l]
        z = W @ a + b
        a = activation(z)
        print(f"layer {l}: z shape={z.shape}  a shape={a.shape}")
    return a

rng = np.random.RandomState(0)
x = rng.randn(10)             # 10 input features

params = {
    1: (rng.randn(8, 10) * 0.1, rng.randn(8) * 0.1, relu),    # layer 1: 10 -> 8
    2: (rng.randn(4, 8) * 0.1, rng.randn(4) * 0.1, relu),     # layer 2: 8 -> 4
    3: (rng.randn(1, 4) * 0.1, rng.randn(1) * 0.1, sigmoid),  # output layer: 4 -> 1
}

prediction = forward_propagation(x, params)
print("final prediction:", prediction)
```

### Demonstrating Vanishing Gradients Numerically
```python
import numpy as np

def sigmoid_grad(z):
    s = 1 / (1 + np.exp(-z))
    return s * (1 - s)

# Simulate the compounding effect of multiplying several small sigmoid-region gradients
z_values = [3.0, -2.5, 4.0, -3.5, 3.0]   # values deep in sigmoid's saturating region
gradients = [sigmoid_grad(z) for z in z_values]
compounded = np.prod(gradients)
print("individual layer gradients:", [round(g, 4) for g in gradients])
print("compounded gradient through all layers:", compounded)
# Notice how quickly the compounded gradient shrinks toward zero.
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Network depth** | Add depth only if validation performance justifies the added optimization difficulty; deeper isn't automatically better. |
| **Weight initialization** | Use variance-aware schemes (He for ReLU, Xavier/Glorot for sigmoid/tanh) to reduce vanishing/exploding gradient risk from the start. |
| **Shape verification** | Always print/assert layer shapes during development — shape bugs are a leading source of silent errors. |
| **Activation choice per layer** | ReLU (or variants) for hidden layers to mitigate vanishing gradients; task-appropriate activation (sigmoid/softmax/linear) only at the output layer. |

---

## 5. Failure Modes & Gotchas

- Mismatched weight matrix shapes between consecutive layers causing silent broadcasting errors rather than a clear crash.
- Assuming forward propagation alone trains the network — forward propagation only computes a prediction; backpropagation is what actually updates weights.
- Ignoring vanishing/exploding gradients when naively adding many layers with saturating activations.
- Forgetting to apply the correct activation function at the output layer for the task (e.g., using ReLU instead of sigmoid for binary classification output).

---

## 6. Self-Check

1. Write the forward propagation equations for one layer, and explain what each symbol represents.
2. Why does backpropagation need the chain rule specifically?
3. Why does increasing depth increase the risk of vanishing or exploding gradients?
4. What's the practical consequence of a weight-matrix shape mismatch between two layers?

---

## 7. Interview Q&A

**Q: Write out forward propagation for a single layer and explain exactly what each symbol represents.**
A: `z^[l] = W^[l] a^[l-1] + b^[l]`, followed by `a^[l] = f^[l](z^[l])`. Breaking this down: `a^[l-1]` is the output of the *previous* layer — the representation being handed into this layer (for the very first layer, this is just the raw input `x`). `W^[l]` is this layer's learned weight matrix, which linearly combines the incoming values from the previous layer — its shape is specifically `(number of units in this layer, number of units in the previous layer)`, since it needs to map every incoming value to every unit in this layer. `b^[l]` is this layer's learned bias vector, one value per unit in this layer, added after the weighted combination.

`z^[l]` is the result of this linear step — often called the "pre-activation," since it's the raw linear combination *before* any non-linearity is applied. Finally, `f^[l]` is this layer's activation function (ReLU, sigmoid, or whatever was chosen for this specific layer), and applying it to `z^[l]` produces `a^[l]` — this layer's actual output, which then becomes `a^[l-1]` from the perspective of the *next* layer in the sequence. This exact pattern — linear combination, then non-linear activation — repeats at every single layer, all the way to the final output layer.

*One-liner: `z^[l] = W^[l]a^[l-1] + b^[l]` is the linear combination step (weights times the previous layer's output, plus bias), and `a^[l] = f^[l](z^[l])` applies this layer's activation function to produce the actual output handed to the next layer — repeating this same two-step pattern at every layer is literally what forward propagation is.*

**Q: Why does backpropagation specifically need the chain rule from calculus — what would go wrong without it?**
A: Training needs to know, for every single weight in the entire network, how much the final loss would change if that specific weight were nudged slightly — this is the weight's gradient, and gradient descent uses it to decide which direction and how much to adjust that weight to reduce the loss.

Here's the problem a weight deep inside the network (say, in layer 2 of a 5-layer network) faces: that weight doesn't directly touch the final loss at all — its effect on the loss is *indirect*, flowing through every layer that comes after it (layer 2's output affects layer 3's computation, which affects layer 4's, which affects layer 5's, which finally produces the loss). You can't directly compute "how does this one weight affect the final loss" in one single step, because the relationship is mediated through several intermediate computations in between.

The chain rule is precisely the calculus tool for exactly this situation: it tells you that the gradient of a final result with respect to some early input, when that input only affects the result through a chain of intermediate functions, can be computed by multiplying together the local gradients of each step in that chain. So you can compute how the loss changes with respect to layer 5's output, then how layer 5's output changes with respect to layer 4's output, then layer 4's with respect to layer 3's, and so on — multiplying these local, step-by-step gradients together gives you the true, overall effect of an early weight on the final loss, without ever needing to compute some impossibly complex, all-at-once derivative directly. Without the chain rule, there would be no systematic, efficient way to connect an early layer's weights to the final loss through all of the intervening layers' computations at all.

*One-liner: a deep layer's weight only affects the final loss indirectly, through every layer that comes after it — the chain rule lets you compute this indirect effect by multiplying together each step's local gradient (loss-vs-layer-5-output, times layer-5-vs-layer-4, and so on back to the weight in question), which is exactly what makes it possible to efficiently compute how an early weight affects a loss that's many layers removed from it.*

**Q: Why does increasing network depth specifically increase the risk of vanishing or exploding gradients?**
A: Because of the chain rule's multiplicative structure covered above — the gradient reaching an early layer is the *product* of every individual layer's local gradient, from the output all the way back to that early layer. If a network has `L` layers, the gradient reaching layer 1 involves multiplying together roughly `L` individual local gradients in sequence.

Here's why this is dangerous specifically as `L` grows large: if each individual layer's local gradient tends to be somewhat less than 1 (which happens readily with saturating activations like sigmoid/tanh, as covered in Lesson 03), multiplying many such values together compounds *exponentially* smaller with each additional layer — the product of many numbers each less than 1 shrinks toward zero far faster than you might intuitively expect, purely because of how multiplicative compounding works (the same mathematical pattern as compound interest, just shrinking instead of growing). This is the vanishing gradient problem, and it gets systematically worse the deeper the network is, simply because there are more multiplicative steps in the chain for the shrinkage to compound across.

The mirror-image problem, exploding gradients, happens if individual layer gradients tend to be somewhat greater than 1 — multiplying many such values together compounds exponentially *larger*, producing enormous gradient values that cause unstable, destabilizing weight updates. Both problems are a direct, structural consequence of how many multiplicative steps the gradient has to pass through — which is exactly why they're specifically a "deep" network problem: a shallow, single or few-layer network simply doesn't have enough multiplicative steps in its gradient chain for this compounding effect to become severe.

*One-liner: the gradient reaching an early layer is the product of every individual layer's local gradient in the chain between it and the output — if those local gradients tend to be systematically less than 1 (vanishing) or greater than 1 (exploding), multiplying many of them together compounds exponentially in that direction, and this compounding gets worse specifically as depth increases, since there are more multiplicative steps for the effect to build up across.*

**Q: You implement forward propagation and it runs without crashing, but the output is nonsensical. You check and find `W²` was defined with shape `(8, 8)` when it should have been `(4, 8)` (layer 2 should map 8 inputs down to 4 units). Why did this not just crash with a clear shape error?**
A: NumPy (and most array libraries) use **broadcasting** — a set of rules that let arrays of certain mismatched shapes still be combined via arithmetic, by implicitly stretching one of them to match the other, rather than always strictly requiring exactly matching shapes before any operation is allowed to proceed. If the actual shapes involved happen to satisfy broadcasting's specific compatibility rules (even though they don't represent the mathematically intended layer dimensions at all), the matrix multiplication or addition can complete successfully and produce *some* output — it's just not the output you actually intended, since the computation didn't represent the layer transformation you meant to define.

This is exactly the danger: a hard crash (a clear "shapes do not match" error) is actually the easier case to debug, because it's immediately obvious something is wrong, and the error message typically tells you exactly which operation and which shapes were involved. A silent broadcasting "success" that produces a wrong-but-plausible-looking numeric result is much harder to catch — the code runs, produces numbers, and nothing visibly signals that those numbers don't actually mean what you think they mean, until you specifically go looking for the discrepancy (by checking intermediate shapes explicitly, as the implementation snippet does by printing them) or notice the final predictions are inexplicably bad.

*One-liner: broadcasting lets arrays of certain mismatched (but still broadcasting-compatible) shapes combine via arithmetic without raising an error, so a wrong shape can silently produce a plausible-but-mathematically-meaningless result instead of a clear crash — which is exactly why explicitly checking/printing intermediate layer shapes during development matters, since a silent wrong-shape bug is much harder to catch than an outright error.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 03 Artificial Neural Network]] · Downstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 05 TensorFlow]]
</content>
