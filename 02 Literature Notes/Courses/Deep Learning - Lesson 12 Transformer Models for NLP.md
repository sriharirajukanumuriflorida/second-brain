# Deep Learning - Lesson 12 Transformer Models for NLP

> Depth goal: understand why attention beats recurrence for NLP specifically (tying to RNN's vanishing-gradient/sequential-bottleneck limitations), BERT's masked-language-modeling pretraining objective, and how fine-tuning BERT for classification actually works mechanically.
>
> Note: the core attention/transformer architecture math (Q/K/V, multi-head attention, residual stream) is covered in full depth in [[02 Literature Notes/LLM Engineering/Attention Deep-Dive]] and [[02 Literature Notes/LLM Engineering/Transformer Architecture]] — this lesson focuses specifically on the NLP/BERT application layer, not re-deriving the attention mechanism itself.

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 12 - Transformer Models for NLP
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_12_Transformer_Models_for_NLP.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Deep Learning/Notebooks/12.05_Introduction_to_BERT__V3.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/12.06_Text_Classification_Using_BERT.ipynb]]

---

## 1. Mental Model

**Transformers replaced RNNs as the dominant NLP architecture because attention solves both of recurrence's core weaknesses at once: it doesn't suffer from vanishing gradients over long distances (every position can directly attend to every other position, with no multiplicative chain through many timesteps), and it parallelizes across the whole sequence during training (no need to wait for timestep `t-1` to finish before computing timestep `t`).** BERT is a landmark pretrained transformer that demonstrated these architectural advantages translate into dramatically better, more transferable language understanding than RNN-based approaches had achieved.

> Key intuition: **BERT is pretrained once, at great expense, on a generic "understand language" objective (masked language modeling) using a massive amount of unlabeled text — then fine-tuned cheaply, with comparatively little task-specific labeled data, for a specific downstream task (classification, question answering).** This pretrain-then-fine-tune pattern is the direct NLP analog of transfer learning covered in Transfer Learning — the same underlying idea (reuse expensive, generically-useful learned representations; adapt cheaply to a specific task), just applied to language instead of images.

---

## 2. How It Actually Works

### 2.1 Why attention beats recurrence for NLP specifically
Recall from Recurrent Neural Network that an RNN's core limitation is twofold: vanishing gradients over long sequences (information from early timesteps struggles to influence much later ones, due to repeated multiplicative shrinking through many timesteps), and strict sequential computation (timestep `t` can't be computed until timestep `t-1` finishes, since it directly depends on `t-1`'s hidden state) — this sequential dependency prevents parallelizing computation across a sequence during training, making RNN training slow on long sequences.

Attention (covered fully in Attention Deep-Dive) solves both simultaneously: any token can directly attend to any other token in the sequence, regardless of distance — there's no multiplicative chain of many intermediate steps for a gradient to vanish through, since the relationship between any two positions is computed in a single, direct step. And because every token's attention computation can happen simultaneously (no token's attention output depends on another token's output being computed first, within the same layer), attention parallelizes across the whole sequence during training, letting transformers train much faster on modern parallel hardware (GPUs/TPUs) than an inherently sequential RNN can.

### 2.2 BERT and masked language modeling
BERT (Bidirectional Encoder Representations from Transformers) is pretrained using a **masked language modeling** objective: take a large amount of ordinary, unlabeled text, randomly hide (mask) some percentage of the tokens (commonly 15%), and train the model to predict what the hidden tokens actually were, using the *surrounding* context on both sides. Because BERT can see both the tokens before *and* after a masked position (bidirectional, using the encoder-style attention without causal masking, as covered in Attention Deep-Dive's encoder-vs-decoder discussion), it learns genuinely rich, context-aware representations of each token — representations that incorporate the full surrounding context in both directions, not just what came before.

This objective is deliberately self-supervised — it needs no human labeling at all, since the "correct answer" (what the masked token actually was) is already known directly from the original, unmasked text. This is exactly what allows BERT to be pretrained on enormous quantities of generic, readily-available text (Wikipedia, book corpora), learning broadly useful language representations before ever seeing a single example of any specific downstream task.

### 2.3 Fine-tuning BERT for classification
Once pretrained, BERT is adapted to a specific downstream task (like text classification) by attaching a small, task-specific output layer on top of BERT's pretrained representations (typically using the representation of a special `[CLS]` token, specifically designed during pretraining to aggregate whole-sequence information) and then continuing training — but now on the specific, labeled task data, typically for a comparatively short additional training period and at a comparatively small learning rate, exactly analogous to the fine-tuning pattern covered in Transfer Learning.

This fine-tuning works for the exact same underlying reason transfer learning works for CNNs: BERT's pretrained representations already encode rich, generically useful information about how language works (grammar, semantic relationships, contextual meaning) — the classification task doesn't need to relearn any of this from scratch; it only needs to learn how to *use* this already-rich representation to make the specific classification decision at hand, which needs comparatively much less labeled data and much less training than learning both "how language works" and "how to classify this specific task" simultaneously from scratch would require.

### 2.4 Tokenization considerations specific to BERT
BERT uses **WordPiece** tokenization (a subword tokenization scheme, conceptually similar to the BPE tokenization covered in Tokenization) — splitting words into common subword pieces, which handles rare or unseen words by breaking them into familiar sub-components rather than treating them as a single unknown token. This is the same underlying motivation covered in Tokenization: a fixed, modest vocabulary that still covers essentially any input text, by falling back to smaller, known pieces when a whole word isn't itself a known vocabulary token.

---

## 3. Implementation

Assumed stack: `transformers` (Hugging Face), `tensorflow`/`torch`.

### Fine-Tuning BERT for Text Classification
```python
from transformers import BertTokenizer, TFBertForSequenceClassification
import tensorflow as tf

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = TFBertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

texts = ["This movie was fantastic!", "Terrible waste of time."]
labels = [1, 0]

encodings = tokenizer(texts, truncation=True, padding=True, return_tensors="tf")
dataset = tf.data.Dataset.from_tensor_slices((dict(encodings), labels)).batch(2)

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=2e-5),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=["accuracy"])
# model.fit(dataset, epochs=3)  -- fine-tuning: small LR, few epochs, on top of pretrained weights
print("model ready for fine-tuning; trainable params:", model.num_parameters())
```

### Inspecting the [CLS] Token's Role
```python
from transformers import BertTokenizer, TFBertModel
import tensorflow as tf

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = TFBertModel.from_pretrained("bert-base-uncased")

inputs = tokenizer("A great example sentence.", return_tensors="tf")
outputs = model(inputs)
cls_representation = outputs.last_hidden_state[:, 0, :]   # position 0 is always [CLS]
print("CLS token representation shape:", cls_representation.shape)
# This single vector is what gets fed into the classification head during fine-tuning.
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **BERT vs RNN/LSTM for NLP tasks** | BERT (or transformers generally) for most modern NLP tasks — better long-range context, faster training via parallelization. |
| **Fine-tuning learning rate** | Small (e.g., 2e-5), exactly as with CNN transfer learning fine-tuning — protect the pretrained representation's value. |
| **Model size (base vs large)** | Larger BERT variants capture more nuance but cost more compute/memory; match to task complexity and available resources. |
| **Fine-tune vs feature extraction** | Fine-tuning (updating BERT's weights) typically outperforms pure feature extraction (freezing BERT, only training a classifier head) for most NLP tasks, given adequate task data. |

---

## 5. Failure Modes & Gotchas

- Using too large a learning rate during BERT fine-tuning, destructively overwriting the pretrained representation (same risk as CNN fine-tuning).
- Forgetting that BERT's bidirectional attention makes it unsuitable for autoregressive text generation (it's an encoder, not a decoder) — covered in Attention Deep-Dive's encoder-vs-decoder distinction.
- Truncating input text without considering BERT's maximum sequence length, silently losing content beyond that limit.
- Treating the `[CLS]` token's representation as meaningful before any task-specific fine-tuning has actually been done on it.
- Ignoring WordPiece tokenization quirks (rare words splitting into multiple subword tokens) when reasoning about input length/cost.

---

## 6. Self-Check

1. Why does attention solve both of RNN's core weaknesses (vanishing gradients and sequential bottleneck) at once?
2. What is BERT's masked language modeling pretraining objective, and why is it self-supervised?
3. Why does BERT fine-tuning need comparatively little task-specific data, mechanically?
4. Why is BERT (an encoder) unsuitable for text generation, tying to the encoder/decoder distinction?

---

## 7. Interview Q&A

**Q: Why does attention solve both of RNN's core weaknesses — vanishing gradients and the sequential training bottleneck — at the same time, rather than needing two separate fixes?**
A: Both of RNN's weaknesses actually stem from the same root cause: information has to pass *through* many intermediate timesteps, one at a time, to get from an early position to a late one. Vanishing gradients happen because that multi-step path involves repeated multiplication, which can shrink signals exponentially over many steps. The sequential training bottleneck happens because that same multi-step path means timestep `t` genuinely can't be computed until timestep `t-1` is finished, since it directly depends on it.

Attention removes this multi-step path entirely: any token can directly attend to any other token in a single step, regardless of how far apart they are in the sequence — there's no chain of intermediate timesteps a gradient (or a piece of information) has to pass through to connect position 1 to position 100; it's a single, direct relationship, computed once. Since there's no multi-step chain at all, there's nothing for a gradient to vanish across (fixing the first problem) — and since computing the relationship between any pair of positions doesn't require first computing some other position's output (there's no "wait for `t-1` to finish" dependency the way recurrence has), every position's attention computation can happen in parallel, simultaneously (fixing the second problem). Both fixes come from the exact same underlying architectural change — removing the step-by-step, sequentially-dependent path between distant positions — which is why they arrive together, as a package, rather than needing two separate, unrelated solutions.

*One-liner: both of RNN's weaknesses stem from the same root cause — information passing through many sequential intermediate steps — and attention removes that multi-step path entirely by letting any token directly attend to any other token in one step, which simultaneously eliminates the vanishing-gradient risk (no multiplicative chain to shrink across) and the sequential bottleneck (no "wait for the previous step" dependency, enabling full parallelization), since both problems came from the same underlying cause being fixed by the same underlying architectural change.*

**Q: What is BERT's masked language modeling objective, and why specifically is it described as "self-supervised" rather than needing human labels?**
A: Masked language modeling works by taking ordinary, naturally-occurring text, randomly hiding (masking) a percentage of its tokens, and training the model to predict exactly what each hidden token actually was — using the surrounding, unmasked context (on both sides, since BERT is bidirectional) to make that prediction. For example, given "The [MASK] sat on the mat," the model needs to predict that the masked token was most likely "cat" (or some similarly plausible word), based on everything else in the sentence.

The reason this is self-supervised rather than needing human-provided labels: the "correct answer" for every single masked token is already directly known, for free, from the original, unmasked text itself — you don't need a human to look at the sentence and manually label what the missing word should be, since you already know exactly what it was before you masked it out. This means you can generate essentially unlimited training examples from any large body of ordinary text you already have access to (Wikipedia articles, books, web text) — you just pick different random tokens to mask each time, and you already know the ground-truth answer for each one without any additional human labeling effort at all. This is exactly what makes it feasible to pretrain BERT on truly enormous quantities of text — the training signal is free, derived directly from the structure of ordinary, already-existing text, rather than requiring expensive, slow, human-driven labeling for every single training example.

*One-liner: masked language modeling hides random tokens in ordinary text and trains the model to predict them using surrounding bidirectional context — it's self-supervised because the correct answer for every masked token is already known for free from the original unmasked text (no human needs to label anything), which is exactly what makes it feasible to pretrain on enormous quantities of ordinary text with zero additional labeling cost.*

**Q: Why does fine-tuning BERT for a new classification task need comparatively little task-specific labeled data, mechanically — what exactly is being leveraged?**
A: Training a model entirely from scratch for a classification task requires it to simultaneously learn two genuinely different things from the same limited task-specific data: first, how language itself works in general (grammar, word meaning, how context changes interpretation, long-range relationships between words) — a huge, generic challenge — and second, how to use that general language understanding to make this one specific classification decision. If you only have a modest amount of labeled data for the specific task, it's simply not enough to teach a model both of these things well at once from a cold start — there isn't enough signal in a small, task-specific dataset to teach genuinely general language understanding from scratch.

Fine-tuning sidesteps this by starting from BERT's *already pretrained* weights — the "how does language work in general" piece has already been learned, at great expense, from an enormous amount of generic, unlabeled text during the masked-language-modeling pretraining phase, entirely separate from and before ever seeing this specific classification task's data at all. This means the comparatively small amount of task-specific labeled data available for fine-tuning only needs to teach the model the *second* thing — how to use its already-rich, already-learned language understanding to make this one specific decision — which is a much narrower, much more learnable problem than learning both pieces simultaneously from nothing, and is exactly why a comparatively small amount of task-specific data can still produce strong fine-tuned performance.

*One-liner: training from scratch would need a model to learn both general language understanding and task-specific decision-making from the same limited task data at once — fine-tuning starts from BERT's already-pretrained weights, which already encode general language understanding learned separately from a huge amount of unlabeled text, so the comparatively small task-specific dataset only needs to teach the much narrower, more learnable second piece (how to use that existing understanding for this specific decision), which is exactly why comparatively little task-specific data is needed.*

**Q: Why is BERT, specifically because it's an encoder, unsuitable for autoregressive text generation — tie this to the encoder/decoder distinction?**
A: Recall from Attention Deep-Dive's encoder-vs-decoder discussion: the difference between an encoder (BERT-style) and a decoder (GPT-style) is entirely about whether a causal mask is applied before attention's softmax step. BERT, as an encoder, uses no causal mask at all — every token can freely attend to every other token in the sequence, both before and after it, which is exactly what gives BERT its rich, bidirectional understanding of each token's context (useful for understanding/classification tasks) — but this also means BERT was specifically trained *assuming* the entire sequence (including tokens that come "after" any given position) is already fully available and visible during its own processing.

Text generation, by contrast, is fundamentally autoregressive: you generate one token at a time, where each new token can only be based on what's been generated *so far* — the "future" tokens of the sequence genuinely don't exist yet at the moment you need to generate the next one, so a model doing generation must only ever condition on past context, never future context, since there simply isn't any future context yet to condition on. This is exactly what the causal mask in a decoder enforces, and exactly what BERT's lack of a causal mask makes it structurally unsuited for — BERT was trained in a setting where it always had access to both-directional context, and using it for left-to-right generation would require it to operate in a setting (no future context available) that fundamentally contradicts what it was actually trained to expect and rely on.

*One-liner: BERT's lack of a causal mask (its defining encoder property) gives it rich, bidirectional context — useful for understanding tasks — but this means it was trained assuming full-sequence, both-directional context is always available, which directly contradicts autoregressive generation's requirement that only past context exists at any given generation step, since the "future" tokens genuinely don't exist yet; this mismatch between what BERT was trained to expect and what generation actually provides is exactly why BERT (an encoder) is unsuitable for text generation, which requires a decoder's causal masking instead.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 11 Recurrent Neural Network]] · Downstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 13 Getting Started with Autoencoders]]
- Deep dive on attention mechanism: [[02 Literature Notes/LLM Engineering/Attention Deep-Dive]] · [[02 Literature Notes/LLM Engineering/Transformer Architecture]]
- Related permanent note: [[03 Permanent Notes/Transformers Use Attention for Sequence Modeling]]
- Related code snippet: [[04 Code Snippets/ML/BERT Text Classifier in PyTorch]]
</content>
