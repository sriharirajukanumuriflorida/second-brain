# Deep Learning - Lesson 02 Introduction to Deep Learning

> Depth goal: understand precisely what makes deep learning different from classical ML (hierarchical, learned representations vs hand-engineered features), and why depth specifically matters, not just "more parameters."

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 02 - Introduction to Deep Learning
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_02_Introduction_to_Deep_Learning.pdf]]

---

## 1. Mental Model

**Deep learning is machine learning where the model learns its own useful features from raw data, layer by layer, instead of a human hand-engineering those features first.** Classical ML (Lessons 02-07 of the Machine Learning course) largely assumes a human has already done feature engineering — turning raw data into meaningful numeric inputs (square footage, word counts, pixel histograms) before any model ever sees it. Deep learning flips this: feed the model something close to raw data (pixel values, raw text), and let a stack of layers learn, on its own, which intermediate representations are actually useful for the task.

> Key intuition: **"deep" refers to the number of layers the data passes through, and each layer builds on the representation the previous layer learned.** An early layer in an image model might learn to detect simple edges; a middle layer combines edges into shapes; a later layer combines shapes into object parts; the final layer combines parts into whole-object recognition. Nobody told the network "look for edges first" — it discovered that this hierarchy of increasingly abstract features was useful for minimizing its training error.

---

## 2. How It Actually Works

### 2.1 Why depth, specifically, matters
A single-layer model (like linear/logistic regression) can only learn relationships that are expressible as a straight line or flat hyperplane in feature space — it's fundamentally limited to linear decision boundaries, no matter how many input features it has. Stacking multiple layers, each with a non-linear activation function in between, lets the network compose simple transformations into far more complex, curved decision boundaries and representations — this compositional structure is specifically what "depth" buys you over "width" (just adding more units to a single layer), since composing many simple non-linear transformations can represent certain complex functions far more efficiently (with far fewer total parameters) than a single very wide layer trying to approximate the same function directly.

### 2.2 Hierarchical representation learning
The signature claim of deep learning is that a network trained end-to-end on raw input and a target output will, as a side effect of minimizing its training loss, discover intermediate representations that are increasingly abstract and useful, layer by layer — without anyone explicitly designing those intermediate representations. This is a genuinely different workflow from classical ML, where a human explicitly decides "extract these specific statistical features from the raw image" before any model training even begins. In deep learning, the "feature engineering" work is pushed into the network's own learned weights.

### 2.3 Why this needed to wait for the 2010s to take off
Deep networks aren't a new idea — but they require large amounts of data (to avoid overfitting a model with many parameters) and large amounts of compute (training many layers, over many iterations, on large datasets) to actually outperform simpler methods. The simultaneous rise of large labeled datasets (ImageNet and similar), GPU-accelerated matrix computation, and better training techniques (covered in Lesson 07's optimization content) is what made deep learning practically dominant starting in the early-to-mid 2010s, rather than any single new theoretical breakthrough alone.

### 2.4 The architecture family tree this course builds toward
Each later lesson in this course introduces an architecture specialized for a different kind of data and structure: **ANN/DNN** (Lessons 03-04) are the general-purpose fully-connected foundation; **CNNs** (Lesson 08) specialize in spatial/image data by exploiting local structure; **RNNs** (Lesson 11) specialize in sequential data by carrying state forward through time; **Transformers** (Lesson 12) specialize in sequences too, but via attention instead of recurrence; **Autoencoders** (Lesson 13) specialize in learning compressed representations without labels at all. Each of these is still, fundamentally, a stack of layers learning hierarchical representations — just with different internal structure suited to different data shapes.

---

## 3. Implementation

Assumed stack: `tensorflow`/`keras`. A minimal illustration of the "stack of layers" idea, deferred fully to Lessons 03-05.

### A Minimal Multi-Layer Network (preview)
```python
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation="relu", input_shape=(20,)),   # layer 1: learns some representation
    tf.keras.layers.Dense(32, activation="relu"),                      # layer 2: builds on layer 1's representation
    tf.keras.layers.Dense(1, activation="sigmoid"),                    # output layer: final decision
])
model.summary()
# Each layer transforms the representation handed to it by the previous layer --
# nobody designed what layer 1 or layer 2 "should" learn; training determines it.
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Classical ML vs deep learning** | Classical ML (with hand-engineered features) for small/structured tabular data; deep learning when raw, high-dimensional data (images, text, audio) and enough training data/compute are available. |
| **Depth vs width** | Favor depth for compositional, hierarchical structure in the data; width alone rarely captures the same structure as efficiently. |
| **Data requirements** | Deep learning generally needs substantially more labeled data than classical ML to avoid overfitting its larger parameter count. |
| **When NOT to use deep learning** | Small tabular datasets with clear, already-engineered features often still favor ensemble methods (Lesson 05 of ML course) over deep nets. |

---

## 5. Failure Modes & Gotchas

- Reaching for deep learning on a small, simple tabular dataset where a gradient-boosted tree would perform as well or better with far less data and compute.
- Assuming "deeper is always better" without considering optimization difficulty (vanishing gradients, covered in Lesson 07) that comes with excessive depth.
- Treating hierarchical feature learning as literally interpretable layer-by-layer, when in practice learned representations are often much messier than the clean "edges → shapes → objects" narrative suggests.

---

## 6. Self-Check

1. What's the core difference in workflow between classical ML and deep learning, regarding features?
2. Why does depth specifically (not just more parameters in one layer) matter?
3. Why did deep learning only become practically dominant in the 2010s, despite the core ideas being older?
4. Name the architecture family each later lesson in this course introduces, and what data shape each specializes in.

---

## 7. Interview Q&A

**Q: What's the core workflow difference between classical ML and deep learning, specifically regarding features?**
A: Classical ML workflows typically split into two separate stages done by different parties: first, a human (a data scientist, a domain expert) manually designs and extracts meaningful numeric features from raw data — deciding that "square footage," "number of bathrooms," and "neighborhood crime rate" are the right features to feed a house-price model, for instance. Only after this feature-engineering work is done does the actual model (a regression, a tree, an SVM) get trained on these human-designed features.

Deep learning collapses these two stages into one: instead of a human pre-deciding what features matter, the network is fed something close to raw input (pixel values, raw word sequences) and trained end-to-end — during this single training process, the network's own early layers learn, as a direct consequence of minimizing training loss, to extract whatever intermediate representations turn out to be useful for the task, without any human explicitly specifying what those representations should look like. The "feature engineering" work still happens, but it happens *inside* the model's learned weights during training, rather than as a separate, human-driven step beforehand.

*One-liner: classical ML separates feature engineering (done by a human, beforehand) from model training (done on those human-designed features); deep learning collapses both into one end-to-end training process, where the network's own early layers learn useful intermediate representations as a side effect of minimizing training loss, with no human explicitly designing what those representations should be.*

**Q: Why does depth specifically matter, rather than just adding more units to a single wide layer?**
A: A single layer, no matter how wide (how many units it has), is fundamentally limited by the specific mathematical form of what one layer can compute — generally some linear transformation followed by one non-linear activation applied to the result. You can make this one transformation arbitrarily wide, but it's still structurally just "one non-linear transformation of the input," and some genuinely complex functions require composing many such transformations in sequence to represent efficiently, not just applying one (however wide) transformation once.

Stacking layers lets the network *compose* simple transformations — layer 2 doesn't operate on the raw input directly, it operates on whatever representation layer 1 already produced, meaning layer 2 can build directly on top of patterns layer 1 already extracted, rather than having to rediscover them from scratch. This compositional structure is specifically what allows certain complex, hierarchical functions (image recognition, where low-level edges compose into higher-level shapes which compose into object parts) to be represented with dramatically fewer total parameters when built through several layers of composition, compared to trying to approximate that same complex function with one very wide single layer attempting to capture the whole hierarchy's worth of complexity all at once, without any intermediate composition at all.

*One-liner: a single layer, however wide, is still structurally just one non-linear transformation applied once — depth lets layers compose, with each layer building directly on the representation the previous layer already learned, which can represent certain complex, hierarchical functions far more efficiently (fewer total parameters) than one very wide layer trying to capture that same hierarchy of structure all in a single, uncomposed transformation.*

**Q: Why did deep learning only become practically dominant starting in the 2010s, despite the core mathematical ideas (multi-layer networks, backpropagation) being substantially older?**
A: The core theoretical ideas behind multi-layer neural networks and the backpropagation algorithm for training them predate the 2010s by decades — this wasn't a case of a new mathematical breakthrough suddenly making deep learning possible. What actually changed was the practical, real-world availability of the two other ingredients deep learning genuinely needs to outperform simpler methods: large labeled datasets and large amounts of affordable compute.

Deep networks have many parameters, which means they need large amounts of training data to actually learn generalizable patterns rather than simply overfitting their abundant capacity to a small dataset's noise (the same overfitting principle covered in Introduction to Machine Learning, just at a much larger parameter-count scale). Large, labeled datasets like ImageNet (millions of labeled images) only became widely available and standardized starting around the late 2000s/early 2010s. Separately, training many-layered networks on large datasets requires substantial computation — and GPUs, originally built for graphics rendering, turned out to be extremely well-suited to the parallel matrix multiplications deep learning training requires, becoming widely and affordably available for this repurposed use starting around the same period. Without both of these — enough data to avoid overfitting a large model, and enough affordable compute to actually train it in reasonable time — the older theoretical ideas simply couldn't be practically realized at meaningful scale, which is exactly why the field's rapid practical rise tracked the availability of data and compute, not a sudden theoretical discovery.

*One-liner: the core theory (multi-layer networks, backpropagation) predates the 2010s — what actually changed was the practical availability of the two other necessary ingredients: large labeled datasets (like ImageNet) to avoid overfitting a large model's many parameters, and affordable GPU compute to actually train many-layered networks in reasonable time — without both, the older theory simply couldn't be realized at meaningful scale.*

**Q: This course covers ANN/DNN, CNN, RNN, Transformers, and Autoencoders — what data shape does each architecture specifically specialize in, and why does that specialization exist?**
A: ANN/DNN (the general, fully-connected foundation) makes no particular assumption about the input's structure — every input feature connects to every unit in the next layer, which is flexible but doesn't exploit any special structure the data might have, like spatial or sequential relationships.

CNNs specialize in spatial data (images) by exploiting the fact that nearby pixels are related — instead of fully connecting every pixel to every unit (which would ignore spatial locality and need enormous numbers of parameters), CNNs use small, local filters that slide across the image, learning to detect local patterns (edges, textures) regardless of where in the image they appear, then compose these into higher-level spatial structure.

RNNs specialize in sequential data (time series, text as a sequence) by carrying a hidden state forward from one step to the next, letting earlier context influence how later elements in the sequence are interpreted — exploiting the fact that order and preceding context matter for sequential data, something a plain ANN/DNN has no inherent mechanism to capture at all.

Transformers also specialize in sequential data, but via a fundamentally different mechanism (attention, covered in the LLM Engineering domain) rather than RNN-style recurrence — letting any position in a sequence directly relate to any other position, rather than only propagating information step by step through a hidden state, which both captures long-range dependencies better and parallelizes far better during training.

Autoencoders specialize in learning compressed representations without needing any labels at all — exploiting the idea that forcing data through a narrow bottleneck and then reconstructing it forces the network to learn which information is actually essential to keep, useful for compression, denoising, and anomaly detection.

*One-liner: ANN/DNN makes no structural assumption about the input (flexible but doesn't exploit any special data structure); CNNs exploit spatial locality in images via local filters; RNNs exploit sequential order via a carried-forward hidden state; Transformers also handle sequences but via attention (direct position-to-position relationships) instead of recurrence; Autoencoders exploit a reconstruction bottleneck to learn compressed representations with no labels needed at all — each architecture's specialization directly reflects a specific structural assumption about the kind of data it's built to handle well.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Downstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 03 Artificial Neural Network]]
</content>
