# Deep Learning - Lesson 06 PyTorch

> Depth goal: understand PyTorch's define-by-run (dynamic graph) philosophy and why that specifically matters versus TensorFlow's more static style, plus the actual `autograd`/`backward()` mechanism underneath a training loop.

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 06 - PyTorch
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_06_PyTorch.pdf]]

---

## 1. Mental Model

**PyTorch is built around "define-by-run" — the computation graph is built dynamically, operation by operation, as your actual Python code executes, rather than being defined upfront as a static, fixed structure before any data flows through it.** This means a PyTorch model's forward pass is written as plain, ordinary Python code (with real `if` statements, real loops, real Python control flow) — the graph *is* whatever sequence of operations that Python code happens to execute on a given call, which can genuinely vary from one call to the next.

> Key intuition: **TensorFlow 1.x (and to a lesser degree, the Functional API style broadly) leans toward "define, then run" — describe the whole computation graph structure first, then feed data through it. PyTorch's native style is "run, and the graph gets defined as a byproduct" — you just write normal imperative code, and gradients can still be computed because every operation is silently tracked as it happens.** This difference is why PyTorch has historically been favored for research and rapid, flexible experimentation — architectures with genuinely dynamic structure (varying per input, like certain recurrent or tree-structured models) are naturally expressible as just normal Python control flow, rather than needing special, static-graph-compatible constructs to represent that same dynamic behavior.

---

## 2. How It Actually Works

### 2.1 Tensors and `requires_grad`
A PyTorch tensor is functionally similar to a TensorFlow tensor (an N-dimensional array), but tensors that need gradients tracked are explicitly marked with `requires_grad=True` (model parameters get this automatically when wrapped in `nn.Module`). Any tensor computed *from* a `requires_grad=True` tensor automatically inherits gradient tracking too — PyTorch's `autograd` engine silently builds a graph of exactly which operations produced which tensors, as those operations actually execute.

### 2.2 `autograd` and `.backward()`
When you call `.backward()` on a scalar tensor (typically the loss), PyTorch walks the dynamically-built graph of recorded operations *backward*, applying the chain rule at each recorded step (exactly the same conceptual mechanism as TensorFlow's `GradientTape`, just with a different API surface and a different default execution philosophy) — computing the gradient of the loss with respect to every tensor that had `requires_grad=True` and was involved in producing that loss, storing each gradient in that tensor's `.grad` attribute.

### 2.3 Defining a model with `nn.Module`
PyTorch models are typically defined as Python classes subclassing `nn.Module`, with layers defined in `__init__` and the actual forward computation written explicitly in a `forward()` method — this `forward()` method is literally just Python code, which is exactly what makes dynamic, input-dependent behavior (a loop that runs a different number of times depending on input length, a conditional branch) naturally expressible, since it's just ordinary Python `if`/`for` logic, executed fresh every single call, rather than a fixed structure defined once upfront.

### 2.4 The manual training loop (PyTorch's default style)
Unlike TensorFlow/Keras's `.fit()`, PyTorch's conventional style is writing the training loop explicitly yourself — forward pass, compute loss, zero out old gradients (`optimizer.zero_grad()`), call `.backward()`, call `optimizer.step()`. This is more verbose than `.fit()`, but it makes every single step of the training process fully explicit and directly modifiable — a deliberate design tradeoff favoring transparency and flexibility over the convenience of a single, pre-built training-loop abstraction.

### 2.5 Why "zero the gradients" is a required, explicit step
PyTorch *accumulates* gradients into `.grad` by default, rather than replacing them fresh on every `.backward()` call — this is a deliberate design choice (useful for certain advanced techniques like gradient accumulation across several mini-batches before an update). But it means that if you forget to explicitly zero out gradients before each new `.backward()` call, gradients from the *previous* batch will still be sitting in `.grad` and get added to the new batch's gradients, silently corrupting your training with incorrect, accumulated gradient values — this is one of the most common practical PyTorch bugs for newcomers.

---

## 3. Implementation

Assumed stack: `torch`.

### Defining a Model and Writing the Explicit Training Loop
```python
import torch
import torch.nn as nn

class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(10, 16)
        self.layer2 = nn.Linear(16, 1)

    def forward(self, x):
        x = torch.relu(self.layer1(x))
        return torch.sigmoid(self.layer2(x))

model = SimpleNet()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.BCELoss()

X = torch.rand(32, 10)
y = torch.randint(0, 2, (32, 1)).float()

for epoch in range(5):
    optimizer.zero_grad()                 # clear old gradients -- required
    predictions = model(X)                # forward pass
    loss = loss_fn(predictions, y)         # compute loss
    loss.backward()                        # backward pass (autograd)
    optimizer.step()                       # update weights
    print(f"epoch {epoch}  loss={loss.item():.4f}")
```

### Demonstrating Gradient Accumulation If You Forget zero_grad()
```python
import torch
w = torch.tensor([2.0], requires_grad=True)

for step in range(3):
    loss = (w ** 2).sum()
    loss.backward()               # NOTE: no zero_grad() called here
    print(f"step {step}  w.grad={w.grad.item()}")
# Notice the gradient keeps growing across steps -- it's accumulating, not resetting.
```

### Dynamic Control Flow in a Forward Pass (something Sequential-style APIs can't easily express)
```python
import torch
import torch.nn as nn

class DynamicDepthNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer = nn.Linear(8, 8)

    def forward(self, x, extra_passes: int):
        # The number of times this layer is applied depends on a runtime value --
        # genuinely dynamic per-call structure, expressed as plain Python control flow.
        for _ in range(extra_passes):
            x = torch.relu(self.layer(x))
        return x

model = DynamicDepthNet()
x = torch.rand(4, 8)
print(model(x, extra_passes=2).shape)
print(model(x, extra_passes=5).shape)   # same model, genuinely different computation graph each call
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **PyTorch vs TensorFlow** | Framework choice matters far less than understanding the underlying concepts (tensors, layers, gradients, optimizers), which transfer directly between them. |
| **Explicit training loop vs high-level trainer** | Write explicit loops when you need fine control or non-standard training procedures; use a higher-level wrapper (e.g., PyTorch Lightning) for standard training to reduce boilerplate. |
| **Dynamic vs static graphs** | Favor PyTorch's dynamic style for architectures with genuinely input-dependent structure; either framework is fine for standard, fixed architectures. |
| **Gradient accumulation** | Use PyTorch's default gradient-accumulation behavior deliberately (across several small batches) if memory-constrained; always `zero_grad()` otherwise. |

---

## 5. Failure Modes & Gotchas

- Forgetting `optimizer.zero_grad()`, silently accumulating gradients across batches and corrupting training.
- Forgetting `model.eval()` / `model.train()` mode switches, which affects layers like Dropout and BatchNorm that behave differently during training vs inference.
- Calling `.backward()` on a non-scalar tensor without specifying a gradient argument, causing a confusing error.
- Mixing tensors that do and don't have `requires_grad=True` and being surprised when gradients are `None` for some tensors.
- Assuming framework choice itself determines model quality — the underlying architecture and training procedure matter far more than PyTorch vs TensorFlow.

---

## 6. Self-Check

1. What does "define-by-run" mean, and how does it differ from a static-graph approach?
2. Why does forgetting `optimizer.zero_grad()` corrupt training, mechanically?
3. What kind of architecture is PyTorch's dynamic-graph style specifically well-suited for, that a purely static graph struggles with?
4. What's the actual difference in developer experience between `.fit()` and PyTorch's explicit training loop?

---

## 7. Interview Q&A

**Q: What does "define-by-run" actually mean, and how is it structurally different from a static-graph approach?**
A: In a static-graph approach, you first describe the entire computation graph's structure — every layer, every connection, the whole architecture — as a fixed specification, before any actual data is run through it. Once defined, this graph structure is fixed; the same exact sequence of operations happens on every single call, since the graph was built once, upfront, independent of any specific input.

"Define-by-run" flips this: there's no separate "define the graph first" step at all — you just write ordinary code (in PyTorch's case, a `forward()` method that's literally plain Python), and the actual sequence of operations that counts as "the graph" is simply whatever that code actually executed, for this specific call, with this specific input. If that code contains a conditional (`if some_condition: do_this else: do_that`) or a loop whose iteration count depends on the input, the graph genuinely *is different* from one call to the next, since it's just a record of whatever operations actually ran this time — there's no separate, pre-fixed structure sitting behind the scenes dictating what must happen; the code's own actual execution, this time, defines the graph.

*One-liner: a static graph is a fixed structure defined once, upfront, before any data runs through it, with the same operations happening every single call — define-by-run has no separate upfront definition step at all; the graph is simply whatever sequence of operations the actual code executed this specific time, which can genuinely differ call to call if the code contains input-dependent control flow.*

**Q: Why does forgetting `optimizer.zero_grad()` corrupt training, mechanically — what's actually happening to the numbers?**
A: PyTorch's design choice is that calling `.backward()` *adds* newly-computed gradients into whatever is already sitting in each tensor's `.grad` attribute, rather than replacing that value outright — `.grad` accumulates across calls by default, unless you explicitly clear it first.

So here's what happens if you skip `zero_grad()`: on the first batch, `.backward()` computes gradients correctly and stores them in `.grad`. You then call `optimizer.step()`, which uses those gradients to update the weights — correct so far. But then, on the *second* batch, if you forgot to clear `.grad` first, calling `.backward()` again computes this new batch's gradients and *adds* them on top of whatever gradient values were still sitting there from the first batch (which haven't been cleared) — so the gradient your optimizer actually uses for this second update is the sum of batch 1's gradient and batch 2's gradient combined, not just batch 2's gradient alone, which is what you actually wanted for a correct, independent update on this new batch.

This compounds further with every subsequent batch you forget to clear — the accumulated gradient keeps growing, increasingly dominated by stale gradients from many previous batches rather than reflecting the current batch's actual gradient signal, which produces increasingly incorrect, oversized weight updates that destabilize or corrupt training, often in a way that's subtly wrong rather than obviously crashing — making it a particularly easy bug to miss until training visibly misbehaves.

*One-liner: PyTorch's `.grad` accumulates (adds) new gradients onto whatever's already there, rather than replacing it, by design — skipping `zero_grad()` means each new batch's gradient gets added on top of stale gradients from previous batches that were never cleared, producing increasingly incorrect, oversized combined gradients that corrupt the weight updates, often subtly rather than with an obvious crash.*

**Q: What specific kind of model architecture is PyTorch's dynamic-graph style well-suited for, that a purely static-graph approach genuinely struggles to express?**
A: Any architecture where the actual sequence or number of computational steps genuinely depends on the specific input, at runtime, rather than being fixed in advance for every input. A concrete example: a recurrent network processing variable-length sequences, where a genuinely different number of recurrent steps are needed depending on how long this specific input sequence happens to be — sentence A might be 5 words long, sentence B might be 20 words long, and the actual computation (how many times the recurrent step repeats) genuinely differs between them. Another example: a tree-structured network, where the computation follows the specific branching structure of a parse tree, and different input trees have genuinely different shapes and depths.

In a purely static-graph approach, since the whole graph has to be defined once, upfront, independent of any specific future input, handling this kind of input-dependent structure requires workarounds — often padding all sequences to one fixed maximum length (wasting computation on padding) and using special control-flow constructs built specifically to be representable within a static graph (which are less natural and more awkward to write than plain language control flow).

With PyTorch's define-by-run style, this is just... ordinary code — a `for` loop that runs exactly as many times as this specific input's sequence length, a conditional that follows this specific input's actual tree structure. Since the graph is simply "whatever the code did this time," expressing genuinely input-dependent computation needs no special workaround at all — it's just normal, natural Python, which is exactly why this style has historically been favored for architectures (and especially for research, where trying out such flexible, non-standard structures quickly is a real, frequent need) with this kind of genuinely dynamic computational shape.

*One-liner: architectures where the actual computation genuinely varies per input at runtime (variable-length recurrent processing, tree-structured networks following each input's own specific branching shape) are naturally expressible in PyTorch's define-by-run style as plain, ordinary Python control flow — a purely static graph, defined once upfront independent of any specific future input, needs awkward workarounds (padding, special static-graph-compatible control constructs) to handle this same genuinely input-dependent computation.*

**Q: What's the actual difference in developer experience between calling `.fit()` and writing PyTorch's explicit training loop — beyond just "more lines of code"?**
A: `.fit()` hides the entire training loop's internals behind one method call — forward pass, loss computation, backward pass, optimizer step all happen inside that call, with you only specifying high-level configuration (which loss function, which optimizer, how many epochs) rather than writing out each of those steps yourself. This is genuinely convenient for standard training procedures, since you don't have to re-write the same boilerplate four-step loop every single time — but it also means if you need to do something non-standard partway through — apply a different loss weighting to different examples in a batch based on some runtime condition, interleave two different optimization objectives, inspect or modify gradients before they're applied — you either need to find and use whatever specific hooks/callbacks the high-level API happens to expose for that particular customization, or work around the abstraction entirely.

PyTorch's conventional explicit training loop writes out every one of those same four steps directly in your own code — meaning every single step is immediately visible and directly modifiable, with no hidden internal method to work around. If you need to do something non-standard (custom gradient manipulation, a non-standard loss combination, conditional logic based on intermediate values), you just... write that directly into the loop, in plain Python, exactly where it needs to go, rather than needing the high-level framework to have specifically anticipated and exposed a hook for that particular use case.

The genuine tradeoff: `.fit()`'s convenience is real and saves real repetitive boilerplate for standard cases, but it trades away some direct visibility and easy customizability — PyTorch's explicit loop is more verbose for the standard case, but that verbosity is exactly what buys you full, unobstructed visibility and control over every single step, with nothing hidden that you might need to customize later.

*One-liner: `.fit()` hides the four training steps (forward, loss, backward, optimizer step) behind one call, saving boilerplate for standard training but requiring you to find or work around specific hooks for any non-standard customization — PyTorch's explicit loop writes out all four steps directly in your own code, trading verbosity for full, unobstructed visibility and the ability to directly insert any custom logic exactly where it's needed, with nothing hidden behind an abstraction you'd need to work around.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 05 TensorFlow]] · Downstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 07 Model Optimization and Performance Improvement]]
</content>
