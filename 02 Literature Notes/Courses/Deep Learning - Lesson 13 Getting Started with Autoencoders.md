# Deep Learning - Lesson 13 Getting Started with Autoencoders

> Depth goal: understand precisely why forcing data through a narrow bottleneck forces useful compression (not just "it compresses"), why reconstruction loss is the training signal despite needing no labels, and how anomaly detection via reconstruction error actually works.

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 13 - Getting Started with Autoencoders
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_13_Getting_Started_with_Autoencoders.pdf]]
- Related Notebook:
  - [[07 Resources Library/Deep Learning/Notebooks/13.05_Building_and_Visualizing_an_Autoencoder_with_the_Fashion_MNIST_Dataset.ipynb]]

---

## 1. Mental Model

**An autoencoder is two networks back to back: an encoder that compresses input into a small latent representation, and a decoder that reconstructs the original input from that compressed form — trained purely to make the reconstruction match the original input as closely as possible.** The entire training signal comes from comparing input against reconstructed output — there are no labels at all, which makes autoencoders a genuinely unsupervised technique, closer in spirit to PCA (covered in Unsupervised Learning) than to classification or regression.

> Key intuition: **forcing information through a narrow bottleneck (the latent representation, which is deliberately much smaller than the original input) is what forces the network to learn only the most important, genuinely compressible structure in the data.** If the bottleneck were the same size as the input (or larger), the network could trivially learn to just copy input to output with no real compression or learning happening at all — the bottleneck's narrowness is the entire mechanism that forces genuine, useful learning to occur.

---

## 2. How It Actually Works

### 2.1 Encoder, latent space, decoder
The **encoder** is a stack of layers that progressively reduces the input's dimensionality, step by step, down to a final, small **latent representation** (also called the "bottleneck" or "code") — a vector much smaller than the original input. The **decoder** is a mirror-image stack of layers that progressively *expands* this small latent representation back up to the original input's full dimensionality, attempting to reconstruct the original input as closely as possible. Both encoder and decoder are trained jointly, end-to-end, using a **reconstruction loss** (commonly mean squared error between the original input and the reconstructed output) as the training signal.

### 2.2 Why the bottleneck specifically forces useful compression
If the latent representation were the same size as (or larger than) the original input, the network could, in principle, simply learn an identity function — copy every input value straight through, unchanged, achieving perfect reconstruction with zero actual compression or genuine learning of the data's structure. This would technically minimize the reconstruction loss (perfectly, in fact) while learning nothing useful whatsoever.

The bottleneck's narrowness makes this trivial "just copy everything" strategy mathematically impossible: there simply isn't enough room in a smaller latent vector to preserve every single detail of a larger input exactly. To still minimize reconstruction loss as much as possible *given this hard capacity constraint*, the network is forced to make a choice about what to actually keep — and the only way to reconstruct a close approximation of the input from fewer numbers than the input originally contained is to discard genuinely redundant or less-important information while retaining whatever structure is most essential for approximately reconstructing the input. This is exactly analogous to PCA's variance-maximizing compression (covered in Unsupervised Learning) — both are fundamentally solving "represent this data with fewer numbers while losing as little as possible" — except an autoencoder can learn a non-linear compression (via its non-linear activation functions), potentially capturing more complex structure than PCA's strictly linear projection can.

### 2.3 Why this needs no labels — reconstruction loss as the training signal
The training signal — "how different is the reconstructed output from the original input" — is available directly from the input data itself, with no external label ever required: you already have the original input, and you compute the reconstruction loss by comparing it against the network's own reconstructed output of that exact same input. This is exactly what makes autoencoders unsupervised (or, more precisely, "self-supervised," similar in spirit to BERT's masked-language-modeling setup from Transformer Models for NLP) — the "ground truth" the loss compares against is simply the original input itself, always available, with zero external labeling effort needed, regardless of the dataset's size.

### 2.4 Applications: dimensionality reduction, denoising, and anomaly detection
**Dimensionality reduction**: the trained encoder, used alone (without the decoder), converts any input into its compact latent representation — useful for visualization, as a preprocessing step before a supervised model, or anywhere a compact, information-preserving representation is more useful than the original high-dimensional input.

**Denoising autoencoders**: trained specifically by feeding in a deliberately *corrupted* (noisy) version of an input, while still using the *original, clean* input as the reconstruction target — this forces the network to learn to recover genuine underlying structure while actively ignoring noise, since noise (by its nature) doesn't follow a consistent, learnable, reconstructible pattern, while genuine signal does.

**Anomaly detection**: an autoencoder trained only on *normal*, typical data learns to compress and reconstruct normal patterns well (since that's literally all it was ever shown during training) — when given an input that's genuinely anomalous (meaningfully different in kind from anything seen during training), the trained encoder/decoder pair, having never learned how to efficiently compress and reconstruct *this* kind of pattern, produces a reconstruction with noticeably higher error than it does for normal inputs. This elevated reconstruction error itself becomes the anomaly signal — no labeled anomaly examples are needed at all; the model just needs to be trained exclusively on normal data, and anomalies reveal themselves through disproportionately poor reconstruction.

---

## 3. Implementation

Assumed stack: `tensorflow`/`keras`.

### A Basic Autoencoder for Dimensionality Reduction
```python
import tensorflow as tf

input_dim, latent_dim = 784, 32   # e.g., 28x28 flattened images -> 32-dim latent code

encoder = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation="relu", input_shape=(input_dim,)),
    tf.keras.layers.Dense(latent_dim, activation="relu"),   # the bottleneck
])
decoder = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation="relu", input_shape=(latent_dim,)),
    tf.keras.layers.Dense(input_dim, activation="sigmoid"),   # reconstruct original shape
])
autoencoder = tf.keras.Sequential([encoder, decoder])
autoencoder.compile(optimizer="adam", loss="mse")
# autoencoder.fit(X_train, X_train, epochs=20)  -- note: input is also the target (reconstruction loss)
autoencoder.summary()
```

### Anomaly Detection via Reconstruction Error
```python
import numpy as np

def reconstruction_error(model, X):
    reconstructed = model.predict(X, verbose=0)
    return np.mean((X - reconstructed) ** 2, axis=1)   # per-example MSE

# Train only on normal data; then score new data for anomalies:
# normal_errors = reconstruction_error(autoencoder, X_normal_test)
# new_errors = reconstruction_error(autoencoder, X_new_data)
# flag as anomaly where new_errors significantly exceeds the normal_errors distribution
threshold_example = """
threshold = normal_errors.mean() + 3 * normal_errors.std()
anomalies = new_errors > threshold
"""
print(threshold_example)
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Latent dimension size** | Smaller forces more aggressive compression (more information loss risk); larger preserves more detail but risks the identity-function trivial-copy failure if too close to input size. |
| **Autoencoder vs PCA** | PCA for fast, linear, interpretable compression; autoencoders when the data's genuine structure is non-linear and PCA's linear projection underfits it. |
| **Denoising variant** | Use when the deployment data is genuinely expected to be noisy, and robustness to that noise specifically matters. |
| **Anomaly threshold** | Set based on the reconstruction-error distribution observed on validation *normal* data, not an arbitrary fixed number. |
| **Architecture symmetry** | Decoder is conventionally a mirror image of the encoder, but doesn't strictly have to be — just needs to expand back to the original input's shape. |

---

## 5. Failure Modes & Gotchas

- Setting the latent dimension too close to (or larger than) the input dimension, letting the network trivially learn to copy input to output with no genuine compression.
- Using an anomaly-detection autoencoder trained on data that secretly contains some anomalies, contaminating what the model learns to consider "normal."
- Expecting an autoencoder trained on one data distribution to reconstruct a genuinely different distribution well — its "normal" is specifically whatever it was trained on.
- Forgetting that autoencoder training needs no labels but does need the input itself as the target — a very different `.fit()` call shape than supervised training.
- Over-interpreting individual latent dimensions as having clean, human-interpretable meaning, the same caution as with PCA's components.

---

## 6. Self-Check

1. Why does the bottleneck specifically force useful compression, rather than the network just learning to copy input to output?
2. Why does an autoencoder need no labels, and what serves as the training signal instead?
3. How does anomaly detection via reconstruction error actually work, mechanically?
4. How does a denoising autoencoder differ in its training setup from a standard autoencoder, and why does that difference teach it to ignore noise?

---

## 7. Interview Q&A

**Q: Why does the bottleneck specifically force useful compression, rather than the network simply learning to copy input to output with no real learning happening?**
A: If the latent representation (the bottleneck) were the same size as, or larger than, the original input, there's a trivial strategy that would achieve perfect reconstruction with literally zero compression or learning of any genuine structure: just copy each input value straight through unchanged, all the way to the output. This would minimize reconstruction loss perfectly (zero error), but it would be a completely useless model — it learned nothing about the data's actual structure; it just became an expensive, complicated identity function.

Making the bottleneck genuinely smaller than the input makes this trivial "just copy everything" strategy mathematically impossible — there simply isn't enough room in a smaller vector to hold every single value of a larger input without some information being lost. Given this hard capacity constraint, the only way for the network to still minimize reconstruction loss as much as it possibly can is to make smart choices about what to preserve: keep whatever information is genuinely necessary to approximately reconstruct the input, and let go of whatever's redundant or, from the perspective of accurate reconstruction, less essential. This forced, constrained optimization — "do your best to reconstruct, but you only have this much room to work with" — is exactly what pushes the network to discover and retain the data's genuinely important underlying structure, rather than ever being allowed the easy, structure-free option of simply copying everything through unchanged.

*One-liner: a bottleneck the same size as or larger than the input allows a trivial "just copy everything through unchanged" strategy that achieves perfect reconstruction with zero actual learning — making the bottleneck genuinely smaller makes this trivial strategy mathematically impossible, forcing the network to make real choices about what information to keep versus discard, which is exactly what pushes it to learn the data's genuinely important underlying structure instead.*

**Q: Why does an autoencoder need no labels at all, and what exactly serves as its training signal instead?**
A: A supervised model's training signal comes from comparing its prediction against a separately-provided, human-assigned ground-truth label — something external to the raw input itself, that someone had to go determine and attach to each example beforehand. An autoencoder's training signal instead comes purely from comparing its own reconstructed output against the *original input itself* — the exact same data point that was fed in as input is also used as the target the reconstruction gets compared against, with nothing external or separately-labeled required at all.

This works because the autoencoder's actual task — "take this input, compress it, then reconstruct it as closely as possible" — has a built-in, automatically-available notion of "correct" that requires no human judgment or external labeling whatsoever: the "correct" reconstruction is, by definition, simply the original input, unchanged. You already have that original input in hand the moment you have any data point at all — there's no additional step of a person looking at the data and deciding "here's the right answer" the way there would be for, say, labeling an image as "cat" or "dog." This is exactly why autoencoder training can scale to however much raw, unlabeled data happens to be available, with zero labeling cost — the training target is always already present, built directly into the data itself.

*One-liner: an autoencoder's training signal is reconstruction loss, comparing its reconstructed output against the original input itself — since the "correct answer" (the original input) is automatically available the moment you have any data point at all, with no external human judgment or labeling step required, autoencoder training needs no labels and can scale to any amount of available raw data for free.*

**Q: How does anomaly detection via reconstruction error actually work, mechanically — walk through why an anomaly specifically produces higher reconstruction error?**
A: Train the autoencoder exclusively on data that represents the "normal" case — whatever typical, expected pattern the data is supposed to follow. Because this is literally all the data the network ever sees during training, and because the bottleneck forces it to learn an efficient compression specifically suited to reconstructing *this* particular kind of pattern well (per the earlier question), the trained encoder/decoder pair becomes genuinely good — low reconstruction error — specifically at compressing and reconstructing data that resembles what it was actually trained on.

Now feed it something genuinely anomalous — a pattern meaningfully different in kind from anything it ever saw during training. The encoder's learned compression strategy was specifically shaped around the structure of normal data; it has no learned mechanism for efficiently representing whatever makes this new, different pattern "anomalous" in the first place, since it was never exposed to anything like it during training. When this unfamiliar input gets pushed through the same encoder/decoder pipeline, the resulting reconstruction tends to be noticeably worse — the network, having no learned "efficient compression path" for this unfamiliar kind of pattern, reconstructs something that looks more like its best approximation using normal-data patterns, which doesn't actually match this genuinely different anomalous input well at all.

This elevated reconstruction error (comparing the anomalous input against its own poor reconstruction) is exactly the anomaly signal: by comparing a new input's reconstruction error against the distribution of reconstruction errors observed on known-normal validation data, you can flag inputs whose reconstruction error is unusually high (well beyond what normal data typically produces) as likely anomalies — all without ever needing a single labeled example of what an anomaly actually looks like during training, since the model only ever needed to learn what "normal" looks like.

*One-liner: training only on normal data makes the autoencoder specifically efficient at compressing and reconstructing normal patterns — when fed a genuinely anomalous input (unlike anything seen in training), it has no learned efficient path for that unfamiliar pattern, producing a noticeably worse reconstruction; this elevated reconstruction error, compared against the error distribution typical of known-normal data, is exactly the anomaly signal, requiring no labeled anomaly examples at all since the model only ever needed to learn what "normal" looks like.*

**Q: How does a denoising autoencoder's training setup differ from a standard autoencoder's, and why does that specific difference teach it to ignore noise?**
A: A standard autoencoder's training pair is (input, same input) — feed in a clean data point, and the reconstruction target is that exact same clean data point. A denoising autoencoder's training pair is different: feed in a deliberately *corrupted* (noisy) version of a data point, but the reconstruction target remains the *original, clean* version of that same data point — not the noisy version that was actually fed in as input.

This single change in what the target is forces a genuinely different thing to be learned. If the target were the same noisy input (as in a standard autoencoder), the network's easiest path to minimizing reconstruction loss would be to simply learn to reproduce whatever noise pattern happened to be present, alongside the genuine signal — since that noisy version is, by definition, exactly what it's being asked to reconstruct. But because the target is specifically the *clean*, uncorrupted version instead, the network is being directly trained, through its loss function, to actively strip away the noise it was given as input and recover only the genuine underlying signal — reconstructing something different from what it was actually shown, specifically the clean version that the noisy input was originally derived from.

Why this specifically teaches it to ignore noise rather than learn to reproduce it: noise, by its nature, doesn't follow a consistent, learnable, genuinely compressible pattern across different training examples — each instance of noise is essentially random and different, so there's no stable, generalizable "noise pattern" for the limited-capacity bottleneck to usefully learn to preserve across many different training examples. Genuine signal, by contrast, *does* have consistent, learnable structure that repeats meaningfully across examples. Given the bottleneck's limited capacity (forcing the network to prioritize what's worth preserving, per the first question), the network ends up prioritizing the consistent, learnable, genuinely useful signal over the inconsistent, non-generalizable noise — precisely because learning to preserve noise doesn't actually help minimize loss consistently across many different, independently-corrupted training examples the way learning to preserve genuine signal does.

*One-liner: a denoising autoencoder is fed a corrupted input but trained against the original clean version as its target (not the noisy input itself) — this directly trains the network to strip away noise and recover genuine signal, and because noise (unlike genuine signal) doesn't follow a consistent, learnable pattern across different examples, the bottleneck's limited capacity naturally gets prioritized toward preserving the consistent, generalizable signal rather than the inconsistent, non-generalizable noise.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 12 Transformer Models for NLP]]
- Related permanent note: [[03 Permanent Notes/Autoencoders Learn Compact Representations]]
</content>
