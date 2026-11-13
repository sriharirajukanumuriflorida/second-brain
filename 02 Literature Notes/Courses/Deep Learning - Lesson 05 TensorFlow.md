# Deep Learning - Lesson 05 TensorFlow

> Depth goal: understand what a tensor actually is as a data structure, why TensorFlow has both a Sequential and a Functional API (and when each is structurally necessary, not just stylistic preference), and the actual training-loop mechanics underneath `model.fit()`.

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 05 - TensorFlow
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_05_TensorFlow.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Deep Learning/Notebooks/5.02_Introduction_to_Tensors.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/5.03_Hands_on_with_TensorFlow__Part_A.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/5.04_Training_DNN_Using_TensorFlow.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/5.09_Sequential_APIs_in_TensorFlow.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/5.10_Functional_APIs_in_TensorFlow.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/5.11_Hands_on_with_TensorFlow__Part_B.ipynb]]

---

## 1. Mental Model

**TensorFlow is a framework for defining neural network computations as a graph of tensor operations, then efficiently executing that graph (including computing gradients automatically) on CPU/GPU hardware.** A **tensor** is just an N-dimensional array — a scalar is a 0-D tensor, a vector is 1-D, a matrix is 2-D, a batch of color images is a 4-D tensor (batch, height, width, color channels). Every single computation in a neural network, from input data to final predictions, is tensors flowing through operations.

> Key intuition: **the framework's actual job is handling automatic differentiation (computing gradients for backpropagation without you writing the chain-rule math by hand) and efficient hardware execution — you describe the architecture, the framework handles turning that description into a trainable, hardware-accelerated computation.**

---

## 2. How It Actually Works

### 2.1 Tensors
A tensor has a **shape** (its dimensions, e.g., `(32, 28, 28, 3)` for a batch of 32 RGB images, 28x28 pixels) and a **dtype** (float32, int32, etc.). Tensors are immutable in TensorFlow's core API (operations produce new tensors rather than modifying in place) — this immutability is what makes it tractable for the framework to automatically track how each value was computed (needed for automatic differentiation).

### 2.2 The Sequential API
The **Sequential API** builds a model as a simple linear stack of layers, each feeding directly into the next, with exactly one input and one output:

```python
model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(32, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])
```

This covers the vast majority of simple architectures, and its simplicity is genuinely valuable — but it is structurally limited to a single, linear chain: it cannot express a model with multiple inputs, multiple outputs, or any branching/merging of layers (e.g., two separate input branches that get combined partway through the network), because "sequential" by definition means "one layer after another in a straight line," with no mechanism to express anything that isn't a straight line.

### 2.3 The Functional API
The **Functional API** instead treats each layer as a callable function, and you explicitly wire together which layer's output feeds into which other layer's input — this lets you build models with multiple inputs, multiple outputs, shared layers (the same layer applied to two different inputs), and arbitrary branching/merging:

```python
input_a = tf.keras.Input(shape=(10,))
input_b = tf.keras.Input(shape=(5,))
branch_a = tf.keras.layers.Dense(16, activation="relu")(input_a)
branch_b = tf.keras.layers.Dense(16, activation="relu")(input_b)
merged = tf.keras.layers.concatenate([branch_a, branch_b])
output = tf.keras.layers.Dense(1, activation="sigmoid")(merged)
model = tf.keras.Model(inputs=[input_a, input_b], outputs=output)
```

This is why the Functional API exists at all — it's not a stylistic alternative to Sequential, it's structurally necessary for any architecture that isn't a single linear chain (multiple inputs, multiple outputs, residual/skip connections, shared sub-networks).

### 2.4 What `model.fit()` actually does
Calling `.fit()` hides a training loop that, for each batch of data, repeats: run a **forward pass** (compute predictions using the current weights), compute the **loss** (how wrong those predictions were, via the specified loss function), run a **backward pass** (compute gradients of the loss with respect to every weight, using TensorFlow's automatic differentiation engine, `GradientTape`), and apply an **optimizer step** (adjust every weight slightly in the direction that reduces loss, using the chosen optimizer — SGD, Adam, etc., covered in Model Optimization). `.fit()` repeats this across every batch, for the specified number of epochs.

### 2.5 `GradientTape` — what's actually happening underneath
TensorFlow's automatic differentiation records every tensor operation performed while inside a `tf.GradientTape()` context, building up a computation graph on the fly. When you call `tape.gradient(loss, weights)`, it walks this recorded graph backward (applying the chain rule automatically, step by step, exactly as covered conceptually in Deep Neural Network's backpropagation section) to compute the gradient of the loss with respect to every weight you ask about — this is the actual mechanism `.fit()` relies on internally; you rarely write `GradientTape` directly unless you need a custom training loop.

---

## 3. Implementation

Assumed stack: `tensorflow>=2.x`.

### Tensors — Shape and Basic Operations
```python
import tensorflow as tf

t = tf.constant([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
print("shape:", t.shape, "dtype:", t.dtype)
print("reshaped:", tf.reshape(t, (3, 2)).numpy())
print("matmul with its transpose:\n", tf.matmul(t, tf.transpose(t)).numpy())
```

### A Custom Training Loop with GradientTape (what .fit() does internally)
```python
import tensorflow as tf
import numpy as np

model = tf.keras.Sequential([tf.keras.layers.Dense(4, activation="relu"), tf.keras.layers.Dense(1)])
optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
loss_fn = tf.keras.losses.MeanSquaredError()

X = tf.constant(np.random.RandomState(0).rand(16, 3).astype("float32"))
y = tf.constant(np.random.RandomState(0).rand(16, 1).astype("float32"))

for epoch in range(5):
    with tf.GradientTape() as tape:
        predictions = model(X, training=True)        # forward pass
        loss = loss_fn(y, predictions)                # compute loss
    gradients = tape.gradient(loss, model.trainable_variables)   # backward pass
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))  # optimizer step
    print(f"epoch {epoch}  loss={loss.numpy():.4f}")
```

### Sequential vs Functional for a Branching Architecture
```python
import tensorflow as tf

# This CANNOT be expressed with Sequential (two separate inputs merging) --
# it requires the Functional API.
numeric_input = tf.keras.Input(shape=(5,), name="numeric")
text_input = tf.keras.Input(shape=(20,), name="text_embedding")
x1 = tf.keras.layers.Dense(8, activation="relu")(numeric_input)
x2 = tf.keras.layers.Dense(8, activation="relu")(text_input)
combined = tf.keras.layers.concatenate([x1, x2])
output = tf.keras.layers.Dense(1, activation="sigmoid")(combined)
model = tf.keras.Model(inputs=[numeric_input, text_input], outputs=output)
model.summary()
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Sequential vs Functional** | Sequential for simple, single-chain architectures; Functional whenever you need multiple inputs/outputs, branching, or shared layers. |
| **`.fit()` vs custom training loop** | `.fit()` for standard training; custom `GradientTape` loops for non-standard training procedures (e.g., GANs, custom loss weighting per batch). |
| **Eager vs graph execution** | TensorFlow 2.x defaults to eager execution (immediate, debuggable); wrap performance-critical functions in `@tf.function` to compile to a graph for speed. |
| **Batch size** | Larger batches give smoother gradient estimates but use more memory and fewer updates per epoch; tune based on available memory and convergence behavior. |

---

## 5. Failure Modes & Gotchas

- Trying to force a multi-input or branching architecture into the Sequential API — it structurally cannot express this.
- Forgetting `training=True`/`training=False` on layers (like Dropout/BatchNorm) that behave differently during training vs inference.
- Computing gradients outside a `GradientTape` context and getting `None` back silently.
- Shape mismatches between `Input` layers and actual data causing cryptic errors at `.fit()` time rather than at model definition time.
- Not resetting/recreating optimizers correctly when reusing model-building code across experiments, leading to stale optimizer state.

---

## 6. Self-Check

1. What is a tensor, and what two properties define it?
2. Why can't the Sequential API express a multi-input model?
3. Walk through what `.fit()` actually does internally, step by step.
4. What does `GradientTape` actually record, and why is that recording necessary?

---

## 7. Interview Q&A

**Q: Why can't the Sequential API express a model with two separate inputs that get merged partway through the network?**
A: The Sequential API's entire design is built around one specific assumption: a model is a linear chain of layers, where layer `n`'s output is always exactly layer `n+1`'s only input — there's no way, within this structure, to represent "take two separate outputs from two different places and combine them," because that would require a layer to have *two* inputs coming from two different earlier points, which breaks the strict one-in-one-out, single-chain assumption the entire API is built around.

A model with two separate inputs (say, numeric features and a text embedding) that get processed somewhat independently and then merged partway through genuinely isn't a single linear chain at all — it's a branching, then merging, structure: two separate paths that join together. Representing this requires being able to say "this merge layer takes input from *this* branch and *that* branch" — an inherently graph-like, non-linear specification that the Sequential API's "just list the layers in order" interface has no syntax to express at all.

The Functional API fixes this by treating layers as callable functions you explicitly wire together — you can call a layer on any specific previous output, including merging two separate outputs together via a concatenation layer, giving you the full flexibility to describe any directed graph of layer connections, not just a strict single chain.

*One-liner: Sequential assumes a strict single chain where each layer has exactly one input (the previous layer's output) — a model with two separate inputs merging partway through needs a layer to take two distinct inputs from two different branches, which breaks that single-chain assumption entirely and requires the Functional API's explicit, graph-like layer-wiring instead.*

**Q: Walk through exactly what `model.fit()` does internally, for one single batch of data.**
A: First, a **forward pass**: the current batch of input data is pushed through the network's layers, in order, using the model's current weights, producing a prediction for each example in the batch — exactly the forward propagation mechanism covered in Deep Neural Network, just executed by the framework rather than by hand.

Second, the **loss** is computed: the predictions are compared against the true labels for this batch, using whatever loss function was specified (mean squared error for regression, cross-entropy for classification), producing a single number representing how wrong the predictions were, on average, across this batch.

Third, a **backward pass**: the framework's automatic differentiation engine (TensorFlow's `GradientTape` mechanism, running under the hood even though `.fit()` doesn't show it to you directly) computes the gradient of this loss with respect to every single trainable weight in the network — using the chain rule, propagated backward through every layer, exactly as covered conceptually in Deep Neural Network's backpropagation section.

Fourth, an **optimizer step**: using these computed gradients, the chosen optimizer (SGD, Adam, or whatever was specified when compiling the model) adjusts every weight slightly, in the direction that would reduce the loss, by an amount determined by the learning rate and the optimizer's own specific update rule (covered more fully in Model Optimization and Performance Improvement).

`.fit()` repeats this entire four-step cycle for every batch in the training data, and repeats the whole pass over all batches for however many epochs you specified — all of this machinery is what's actually happening underneath that one single method call.

*One-liner: for each batch, `.fit()` runs a forward pass (compute predictions with current weights), computes the loss (how wrong those predictions were), runs a backward pass (automatic differentiation computes the gradient of loss with respect to every weight via the chain rule), and takes an optimizer step (adjusts every weight based on its gradient) — repeating this four-step cycle across every batch, for every epoch.*

**Q: What does `GradientTape` actually record, and why is that recording necessary for computing gradients?**
A: `GradientTape` records every tensor operation that happens while code is executing inside its context block — every addition, multiplication, matrix product, activation function application — building up, as the forward pass actually executes, a record of exactly which operations were performed, on which tensors, in what order, to produce the final result (the loss, typically).

This recording is necessary because computing a gradient via the chain rule (as covered in Deep Neural Network) requires knowing the *exact sequence of operations* that connects an early input (a specific weight) to the final output (the loss) — you need to walk backward through that exact chain, applying each operation's own local derivative rule in reverse order, to correctly compute the overall gradient. Without recording what operations actually happened during the forward pass, there would be no way to know what sequence to walk backward through at all — the framework genuinely needs this record to know "this value came from multiplying these two other values, which came from this layer's weights, which came from..." all the way back to the actual trainable weights, in order to correctly apply the chain rule in reverse.

Once you call `tape.gradient(loss, weights)`, the tape uses this recorded operation history to automatically walk backward through the exact computation that was actually performed, applying the appropriate local derivative at each recorded step — which is precisely what "automatic differentiation" means: the framework derives the gradient computation automatically from the recorded forward computation, rather than you having to manually write out the chain-rule math for your specific architecture by hand.

*One-liner: GradientTape records every tensor operation performed during the forward pass, building up the exact sequence of computations that connects the weights to the final loss — this recording is necessary because computing a gradient via the chain rule requires knowing that exact sequence to walk backward through, which is exactly what lets the framework automatically derive the gradient computation rather than requiring you to hand-write the chain-rule math for your specific architecture.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 04 Deep Neural Network]] · Downstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 06 PyTorch]]
- Related code snippet: [[04 Code Snippets/ML/TensorFlow Sequential Classifier]]
</content>
