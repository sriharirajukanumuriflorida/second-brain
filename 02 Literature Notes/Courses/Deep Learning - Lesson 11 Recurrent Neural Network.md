# Deep Learning - Lesson 11 Recurrent Neural Network

> Depth goal: trace an RNN's actual recurrence equation, understand vanishing gradients through time (not just space), and understand LSTM's gating mechanism well enough to explain why each gate specifically exists.

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 11 - Recurrent Neural Network
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_11_Recurrent_Neural_Network.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Deep Learning/Notebooks/11.05_Part_1_Text_Classification_Using_RNN.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/11.07_Part_2_Text_Classification_Using_LSTM.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/11.11_Video_Classification_Using_Hybrid_Model.ipynb]]

---

## 1. Mental Model

**An RNN processes a sequence one element at a time, carrying forward a hidden state that summarizes everything relevant seen so far — letting earlier elements in a sequence influence how later ones are interpreted.** This is the sequential analog of CNN's spatial-locality assumption: just as a CNN assumes nearby *pixels* are related (and builds that assumption into its architecture via convolution), an RNN assumes nearby *positions in a sequence* are related (earlier words/timesteps provide context for later ones), and builds that assumption in by explicitly carrying a hidden state forward, step by step.

> Key intuition: **a plain feedforward network (ANN/DNN/CNN) has no inherent memory of "what came before" — each input is processed independently. An RNN's entire structural addition is this one idea: reuse the *same* set of weights at every timestep, but feed in the previous timestep's hidden state alongside the current input, so information can flow forward through the sequence.**

---

## 2. How It Actually Works

### 2.1 The recurrence equation
At each timestep `t`, an RNN computes a new hidden state `hₜ` from the current input `xₜ` and the *previous* hidden state `hₜ₋₁`:

$$h_t = f(W_{xh}x_t + W_{hh}h_{t-1} + b_h)$$

`W_xh` transforms the current input, `W_hh` transforms the previous hidden state, and these are *summed* before the activation `f` (typically tanh). Critically, the same weight matrices `W_xh` and `W_hh` are reused at *every* timestep — this is parameter sharing across time, directly analogous to CNN's parameter sharing across space: the same "how to combine current input with prior context" logic is assumed to apply regardless of *which* position in the sequence you're currently at, which is both parameter-efficient and lets the network generalize to sequences of varying lengths it's never seen before (since the same recurrence rule just gets applied however many times the sequence happens to be long).

### 2.2 Why RNNs struggle with long-range dependencies
Training an RNN (via **backpropagation through time**, BPTT) requires computing gradients that flow backward not just through layers (as in a standard feedforward network), but backward through *every single timestep* of the sequence — for a long sequence, this is mathematically equivalent to backpropagating through a very deep network, where "depth" here is the sequence length rather than the number of stacked layers. Exactly the same vanishing/exploding gradient problem covered in Deep Neural Network applies here, just along the time dimension instead of the layer dimension: if the recurrent weight matrix `W_hh` tends to shrink signals as they repeatedly pass through it, the gradient (and the actual information) from many timesteps ago gets vanishingly diminished by the time it reaches — or needs to influence — a much later timestep, making it very difficult for a plain RNN to learn dependencies that span a long distance in the sequence (e.g., connecting a pronoun to a noun mentioned 50 words earlier).

### 2.3 LSTM — adding explicit gates to control information flow
**LSTM** (Long Short-Term Memory) addresses this by adding a separate **cell state** (a kind of long-term memory conveyor belt) alongside the regular hidden state, plus three learned **gates** that explicitly control what information flows into, out of, and stays in this cell state:

- **Forget gate**: decides what to discard from the existing cell state — `fₜ = σ(W_f·[hₜ₋₁, xₜ] + b_f)`, a value between 0 (completely forget) and 1 (completely retain) for each piece of stored information.
- **Input gate**: decides what new information from the current input should be added into the cell state — `iₜ = σ(W_i·[hₜ₋₁, xₜ] + b_i)`, paired with a candidate update `C̃ₜ = tanh(W_C·[hₜ₋₁, xₜ] + b_C)`.
- **Output gate**: decides what part of the (now-updated) cell state should actually be exposed as this timestep's hidden state output — `oₜ = σ(W_o·[hₜ₋₁, xₜ] + b_o)`.

The cell state update is `Cₜ = fₜ * Cₜ₋₁ + iₜ * C̃ₜ` — note this is an *additive*, gated update, not a full recomputation from scratch the way the plain RNN's hidden state update is. This additive structure is exactly what fixes the vanishing-gradient problem: information can flow through the cell state across many timesteps largely unchanged (when the forget gate stays close to 1), giving gradients a much more direct, less-attenuated path backward through time, compared to a plain RNN where the hidden state gets fully recomputed (and thus fully subject to repeated shrinking/multiplication) at every single step.

### 2.4 Bidirectional RNNs/LSTMs
A standard RNN/LSTM only ever sees *past* context when processing a given timestep (it processes left-to-right). A **bidirectional** RNN/LSTM runs two separate recurrent passes — one left-to-right (as normal) and one right-to-left (processing the sequence in reverse) — then combines both directions' hidden states at each timestep. This lets each position's representation incorporate context from *both* directions (both what came before and what comes after in the sequence), which is valuable for tasks where the full sequence is available upfront (like classifying a complete sentence) — though not usable for genuinely real-time, left-to-right generation tasks where the "future" of the sequence doesn't exist yet at the time a prediction is needed.

---

## 3. Implementation

Assumed stack: `tensorflow`/`keras`.

### A Plain RNN and an LSTM for Text Classification
```python
import tensorflow as tf

vocab_size, embedding_dim, max_len = 10000, 64, 100

plain_rnn_model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_len),
    tf.keras.layers.SimpleRNN(32),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])

lstm_model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_len),
    tf.keras.layers.LSTM(32),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])

bidirectional_lstm_model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_len),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
    tf.keras.layers.Dense(1, activation="sigmoid"),
])
for name, m in [("Plain RNN", plain_rnn_model), ("LSTM", lstm_model), ("BiLSTM", bidirectional_lstm_model)]:
    print(f"{name}: {m.count_params()} params")
```

### A Plain RNN Recurrence Step from Scratch
```python
import numpy as np

def rnn_step(x_t, h_prev, W_xh, W_hh, b_h):
    return np.tanh(W_xh @ x_t + W_hh @ h_prev + b_h)

rng = np.random.RandomState(0)
input_dim, hidden_dim, seq_len = 4, 3, 5
W_xh, W_hh, b_h = rng.randn(hidden_dim, input_dim)*0.1, rng.randn(hidden_dim, hidden_dim)*0.1, np.zeros(hidden_dim)

h = np.zeros(hidden_dim)   # initial hidden state
for t in range(seq_len):
    x_t = rng.randn(input_dim)
    h = rnn_step(x_t, h, W_xh, W_hh, b_h)
    print(f"timestep {t}  hidden state: {np.round(h, 3)}")
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Plain RNN vs LSTM/GRU** | Use LSTM/GRU by default for anything beyond very short sequences — plain RNNs rarely outperform them in practice due to vanishing gradients. |
| **Unidirectional vs bidirectional** | Bidirectional when the full sequence is available upfront (classification); unidirectional for real-time/streaming/generation tasks. |
| **LSTM vs GRU** | GRU is a simpler, faster variant with fewer gates; often comparable performance to LSTM with less computation — try both. |
| **RNN/LSTM vs Transformer** | For long sequences or when parallelizable training matters, modern practice increasingly favors Transformers/attention (covered in LLM Engineering) over RNN-style recurrence. |

---

## 5. Failure Modes & Gotchas

- Using a plain RNN on long sequences and finding it can't learn long-range dependencies (vanishing gradients through time).
- Applying bidirectional processing to a real-time/streaming task where future context genuinely isn't available yet.
- Forgetting that RNN/LSTM training is inherently sequential (can't fully parallelize across timesteps the way a Transformer can), making it slower to train on long sequences.
- Not padding/masking variable-length sequences correctly, letting padding tokens incorrectly influence the hidden state.

---

## 6. Self-Check

1. Write the plain RNN recurrence equation and identify what's being shared across timesteps.
2. Why do plain RNNs struggle with long-range dependencies — tie this to vanishing gradients specifically through time.
3. What does each of LSTM's three gates specifically control, and why does the cell state's additive update fix the vanishing-gradient problem?
4. When would a bidirectional RNN/LSTM not be usable, and why?

---

## 7. Interview Q&A

**Q: Write the plain RNN recurrence equation, and identify exactly what gets shared across timesteps (and why that sharing matters).**
A: `hₜ = f(W_xh·xₜ + W_hh·hₜ₋₁ + b_h)` — the new hidden state at time `t` is computed from the current input `xₜ` and the previous hidden state `hₜ₋₁`, combined via two separate weight matrices and passed through an activation function (typically tanh).

What's shared across every single timestep: the weight matrices `W_xh` and `W_hh`, and the bias `b_h` — these are the exact same learned parameters reused at timestep 1, timestep 2, timestep 50, and every other timestep in the sequence, no matter how long the sequence is. This is directly analogous to CNN's parameter sharing across spatial position (the same filter reused everywhere in an image) — here, the same "combine current input with prior hidden state" logic is reused everywhere in time.

Why this sharing matters: it means the network only ever needs to learn *one* rule for "how to update my understanding given a new input and what I already knew" — and because that one rule is reused regardless of position in the sequence, the network can generalize to sequences of lengths it's never actually seen during training (a sequence of length 200, even if training only ever showed sequences up to length 50) — since applying the same learned recurrence rule one more time is all that's needed to handle one more timestep, rather than needing entirely separate, position-specific logic for every possible sequence length.

*One-liner: `hₜ = f(W_xh·xₜ + W_hh·hₜ₋₁ + b_h)` shares the exact same weight matrices and bias across every single timestep, regardless of sequence length — this sharing means the network learns just one recurrence rule, which generalizes to sequences of any length (even ones longer than anything seen in training) simply by applying that same rule one more time per additional timestep.*

**Q: Why do plain RNNs specifically struggle with long-range dependencies — tie this precisely to vanishing gradients through time, not just space.**
A: Training an RNN requires computing gradients backward through every timestep the sequence contains — this process, backpropagation through time, is mathematically the same chain-rule mechanism covered in Deep Neural Network's backpropagation section, just with "timesteps" playing the role that "layers" play in a standard feedforward network. For a sequence of length `T`, the gradient reaching timestep 1 (the very first element of the sequence) has to pass backward through roughly `T` multiplicative steps, each one involving the recurrent weight matrix `W_hh` (and the activation function's local derivative at that step).

If `W_hh`'s effect tends to shrink signals somewhat at each step (which is common, especially combined with tanh's saturating behavior for larger-magnitude inputs, similar to the sigmoid saturation issue covered in Artificial Neural Network), then multiplying this shrinking effect together across many timesteps compounds exponentially smaller — exactly the same vanishing-gradient math covered in Deep Neural Network, just now with sequence length playing the role of network depth. For a long sequence (say, 100 timesteps), this means the gradient signal connecting a very early timestep to the final loss can shrink to something vanishingly close to zero, meaning the network effectively can't learn to adjust its behavior based on information from that early timestep at all — it's functionally "forgotten" by the time training signal tries to reach back that far, even though that early information might genuinely matter for correctly interpreting a much later part of the sequence (like resolving what a pronoun 50 words later refers back to).

*One-liner: backpropagation through time requires the gradient to pass backward through roughly as many multiplicative steps as there are timesteps in the sequence, each involving the recurrent weight matrix — if that matrix's effect tends to shrink signals even slightly at each step, this compounds exponentially smaller across a long sequence (the same vanishing-gradient math as deep layers, just with sequence length playing the role of depth), meaning gradient signal from early timesteps becomes vanishingly small by the time it would need to influence much later ones, making long-range dependencies very hard for a plain RNN to learn.*

**Q: What does each of LSTM's three gates specifically control, and why does the cell state's additive update structure fix the vanishing-gradient problem that plagues plain RNNs?**
A: The **forget gate** controls what existing information in the cell state should be discarded — it outputs a value between 0 and 1 for each piece of stored information, where 0 means "completely erase this" and 1 means "keep this completely unchanged." The **input gate** (paired with a candidate update) controls what new information from the current input and previous hidden state should actually be written into the cell state — deciding how much of this timestep's new information is actually worth remembering going forward. The **output gate** controls what part of the (now-updated) cell state should actually be exposed as this timestep's externally-visible hidden state output — the cell state can hold onto information "in reserve" without necessarily exposing all of it as output at every single timestep.

The cell state update itself, `Cₜ = fₜ * Cₜ₋₁ + iₜ * C̃ₜ`, is the key structural fix: notice this is an *addition* — the new cell state is the old cell state (scaled by the forget gate) *plus* new information (scaled by the input gate), rather than the old cell state being fully discarded and recomputed from scratch at every step, the way a plain RNN's hidden state is. When the forget gate is close to 1 (deciding to retain this information), the gradient flowing backward through this additive update has a much more direct path: the derivative of an addition with respect to one of its terms is just 1 (or close to it, scaled by the forget gate), rather than being subject to repeated multiplication through a weight matrix and a saturating activation function at every single step, the way a plain RNN's fully-recomputed hidden state update is. This additive "highway" is directly analogous to the residual-connection mechanism covered in Transformer Architecture — both solve vanishing gradients by providing a path where information (and gradient) can flow through largely unchanged unless something explicitly decides to modify it, rather than being forced through a full, repeated recomputation at every single step.

*One-liner: the forget gate decides what to erase from the cell state, the input gate decides what new information to write in, and the output gate decides what to expose as this timestep's hidden state — the cell state's update is additive (old state scaled by the forget gate, plus new information scaled by the input gate) rather than a full recomputation, which gives gradients a much more direct backward path (similar to a residual connection) when the forget gate stays close to 1, fixing the vanishing-gradient problem that plagues a plain RNN's fully-recomputed hidden state.*

**Q: When would a bidirectional RNN/LSTM not actually be usable, and why specifically?**
A: A bidirectional architecture works by running two separate recurrent passes over the *entire* sequence — one left-to-right, one right-to-left — and this fundamentally requires having the *complete* sequence available, in full, before processing can even begin, since the right-to-left pass needs to start from the very end of the sequence and work backward, which is only possible if that end already exists and is known.

This makes bidirectional processing structurally unusable for any genuinely real-time, streaming, or generative task where the "future" part of the sequence doesn't exist yet at the moment a prediction is actually needed — generating text one word at a time (where the next word hasn't been produced yet, so there's no "right-to-left" context from the future to process at all), processing a live audio stream in real time (where future audio simply hasn't happened yet), or any online prediction task where you need an answer *now*, based only on what's been observed *so far*, with no ability to wait for information that hasn't arrived yet.

Bidirectional processing is specifically appropriate for tasks where the full input is already available upfront before any prediction is needed — classifying a complete, already-written sentence (sentiment analysis on a finished review), tagging parts of speech across an entire already-transcribed sentence, or any task operating on a fixed, complete, already-fully-available piece of sequential data rather than one being generated or observed incrementally in real time.

*One-liner: bidirectional processing requires the complete sequence to already exist before processing begins, since its right-to-left pass needs to start from the sequence's actual end — this makes it structurally unusable for any real-time, streaming, or generative task where the "future" part of the sequence doesn't exist yet at prediction time, and appropriate only for tasks where the full input is already fully available upfront, like classifying an already-complete piece of text.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 10 Object Detection]] · Downstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 12 Transformer Models for NLP]]
- Related permanent note: [[03 Permanent Notes/Recurrent Neural Networks Model Sequence Dependencies]]
- Related code snippet: [[04 Code Snippets/ML/Bidirectional LSTM Text Classifier]]
</content>
