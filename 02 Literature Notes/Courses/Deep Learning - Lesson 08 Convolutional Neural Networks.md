# Deep Learning - Lesson 08 Convolutional Neural Networks

> Depth goal: understand why convolution (not a fully-connected layer) is the right operation for images, trace the actual filter/stride/padding math, and understand pooling's specific role in building spatial invariance.

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 08 - Convolutional Neural Networks
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_08_Convolutional_Neural_Networks.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Deep Learning/Notebooks/8.03_Working_with_Image_Data.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/8.08_Image_Classification_Using_CNN.ipynb]]

---

## 1. Mental Model

**CNNs learn spatial features in image data by sliding small filters across the image to detect local patterns, then stacking and pooling these detections to build up from simple local features (edges) to complex global ones (objects).** The core design insight: a plain fully-connected layer treats every pixel as an independent input with no awareness that nearby pixels are spatially related — this both throws away genuinely useful structure (nearby pixels usually belong to the same object/edge/texture) and requires an enormous number of parameters (one weight per pixel per output unit, for a high-resolution image).

> Key intuition: **a convolution filter learns one local pattern (an edge at a specific angle, a color blob) and then applies that *same* learned filter everywhere across the image** — this is a deliberate design choice (parameter sharing) based on the assumption that a useful local pattern (like a vertical edge) is worth detecting no matter *where* in the image it appears. This single assumption is what makes CNNs dramatically more parameter-efficient and more effective on images than a fully-connected network treating every pixel as an unrelated, independent input.

---

## 2. How It Actually Works

### 2.1 The convolution operation
A convolution filter (also called a kernel) is a small matrix of learned weights (commonly 3x3 or 5x5) that slides across the input image, computing, at each position, the weighted sum of the filter's values with whatever pixels it's currently positioned over (an element-wise multiply-then-sum). This produces a **feature map** — a new, smaller 2D grid where each value represents "how strongly did this filter's specific pattern match at this location in the original image."

Critically, the *same* filter (the same learned weights) slides across the *entire* image — this is **parameter sharing**, and it's the key efficiency and generalization mechanism: instead of learning a separate set of weights for detecting a vertical edge at every single possible pixel location (which a fully-connected layer would effectively have to do), the network learns just one small filter that detects vertical edges, and reuses it everywhere the image might contain one.

### 2.2 Filter size, stride, and padding
- **Filter size** (e.g., 3x3) determines the local neighborhood each filter examines at once — smaller filters capture finer, more local patterns; stacking several small-filter layers can still build up a large effective receptive field while using fewer parameters than one large filter directly.
- **Stride** is how many pixels the filter moves between each application — stride 1 slides one pixel at a time (dense, overlapping coverage); stride 2 skips every other position (faster, coarser, produces a smaller output feature map).
- **Padding** adds extra border pixels (usually zeros) around the input before convolving, specifically to control the output feature map's size — without padding, each convolution shrinks the spatial dimensions slightly (since the filter can't center itself fully at the very edge), and "same" padding is used specifically to keep output dimensions matching input dimensions when that's desired.

The output feature map's size follows directly from these: `output_size = (input_size - filter_size + 2·padding) / stride + 1`.

### 2.3 Multiple filters and multiple channels
A convolutional layer doesn't learn just one filter — it learns many (e.g., 32, 64, 128), each specializing in detecting a different local pattern (one filter for vertical edges, another for a particular color blob, another for a diagonal texture). The output is a stack of feature maps, one per filter — this stack becomes the input to the next layer, which can then learn filters that combine and build on these already-detected lower-level patterns into more complex, higher-level ones.

### 2.4 Pooling — building spatial invariance
**Pooling** (most commonly **max pooling**) reduces a feature map's spatial size by taking, within each small local region (e.g., 2x2), just the single maximum value and discarding the rest. This serves two purposes: it reduces computation and memory for subsequent layers, and — more importantly conceptually — it builds in a degree of **translation invariance**: if the specific feature a filter detects (say, an eye-like pattern) shifts by a pixel or two within the image, max pooling's local "take the strongest signal in this neighborhood" behavior means the *presence* of that feature still gets detected and passed forward, even though its *exact* pixel position shifted slightly — the network becomes somewhat robust to small positional shifts, which matters because the exact pixel position of a feature is usually far less important than whether that feature is present at all.

### 2.5 From local features to global understanding — the layer-by-layer hierarchy
Early convolutional layers, operating directly on raw pixels, tend to learn simple, low-level patterns (edges, color gradients, basic textures) — this is genuinely forced by the math, not just a story: with a small filter and no prior layers to build on, the only patterns directly expressible from raw pixel neighborhoods *are* these simple, local ones. Later layers, operating on the *feature maps* produced by earlier layers (not raw pixels anymore), can combine these already-detected simple patterns into increasingly complex, higher-level ones (edges combining into shapes, shapes combining into object parts, object parts combining into whole-object recognition) — this is the direct mechanism behind the "hierarchical representation learning" claim from Introduction to Deep Learning, made concrete and specific for the image domain.

---

## 3. Implementation

Assumed stack: `tensorflow`/`keras`.

### A Basic CNN for Image Classification
```python
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(28, 28, 1)),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
    tf.keras.layers.MaxPooling2D((2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(10, activation="softmax"),
])
model.summary()
# Notice how spatial dimensions shrink and channel depth grows with each Conv2D/Pooling pair.
```

### Convolution from Scratch (to see the actual sliding-window math)
```python
import numpy as np

def conv2d(image, kernel, stride=1):
    h, w = image.shape
    kh, kw = kernel.shape
    out_h = (h - kh) // stride + 1
    out_w = (w - kw) // stride + 1
    output = np.zeros((out_h, out_w))
    for i in range(0, out_h):
        for j in range(0, out_w):
            region = image[i*stride:i*stride+kh, j*stride:j*stride+kw]
            output[i, j] = np.sum(region * kernel)
    return output

image = np.array([[1,2,3,0],[4,5,6,0],[7,8,9,0],[0,0,0,0]], dtype=float)
vertical_edge_filter = np.array([[1,0,-1],[1,0,-1],[1,0,-1]], dtype=float)
print(conv2d(image, vertical_edge_filter))
# High positive values where a strong left-to-right brightness drop exists -- a detected vertical edge.
```

### Max Pooling from Scratch
```python
import numpy as np

def max_pool(feature_map, size=2, stride=2):
    h, w = feature_map.shape
    out_h, out_w = (h - size)//stride + 1, (w - size)//stride + 1
    pooled = np.zeros((out_h, out_w))
    for i in range(out_h):
        for j in range(out_w):
            region = feature_map[i*stride:i*stride+size, j*stride:j*stride+size]
            pooled[i, j] = region.max()
    return pooled

fm = np.array([[1,3,2,0],[4,2,1,1],[0,1,5,2],[2,3,1,0]], dtype=float)
print("pooled:\n", max_pool(fm))
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Filter size** | Prefer stacking several small filters (3x3) over one large filter — more non-linearity, fewer parameters, same effective receptive field. |
| **Stride vs pooling for downsampling** | Both reduce spatial size; strided convolutions are increasingly used instead of separate pooling layers in modern architectures. |
| **Number of filters per layer** | Typically increases with depth (e.g., 32 -> 64 -> 128) as the network trades spatial resolution for representational richness. |
| **Padding** | "Same" padding when output size should match input; "valid" (no padding) when controlled shrinkage is acceptable/desired. |
| **When NOT to use a CNN** | Non-spatial tabular data gains nothing from convolution's local-pattern assumption — use a plain dense network or classical ML instead. |

---

## 5. Failure Modes & Gotchas

- Using a fully-connected layer directly on raw image pixels, ignoring spatial structure and requiring an enormous number of parameters.
- Forgetting to flatten (or use global pooling) before the final dense classification layers, causing a shape mismatch.
- Over-pooling, destroying so much spatial resolution that fine-grained details needed for the task are lost.
- Assuming a CNN trained on one image size/domain transfers perfectly to very different image characteristics without adaptation (see Transfer Learning).
- Not normalizing pixel values (e.g., scaling to [0,1]) before training, slowing convergence.

---

## 6. Self-Check

1. Why does a convolution filter use the *same* weights at every spatial position, and why does that matter for parameter efficiency?
2. Write the formula for output feature map size given input size, filter size, stride, and padding.
3. How does max pooling build in translation invariance, mechanically?
4. Why do early CNN layers tend to learn simple features (edges) while later layers learn complex ones (object parts)?

---

## 7. Interview Q&A

**Q: Why does a convolution filter use the exact same weights at every spatial position across the image, and why does this specifically matter for parameter efficiency?**
A: The design assumption behind this is: a useful local pattern — say, a vertical edge — is worth detecting no matter *where* in the image it happens to appear. A vertical edge near the top-left of an image is fundamentally the same kind of visual feature as a vertical edge near the bottom-right — there's no inherent reason the network should need to learn a completely separate, independent detector for "vertical edge, but specifically at this one location" versus "vertical edge, but specifically at that other location." Using the same filter weights everywhere directly encodes this assumption: once the network learns one good vertical-edge-detecting filter, that same filter gets reused, as-is, applied at every single position across the entire image.

Compare this to a fully-connected layer, which would need a completely separate, independent weight for every single pixel-to-output-unit connection — if you wanted a fully-connected layer to detect "a vertical edge, wherever it occurs in the image," it would effectively have to learn a *separate copy* of edge-detection logic at every possible spatial location independently, since none of its weights are shared or reused across positions at all. For anything beyond a tiny image, this requires an astronomically larger number of parameters than a small, shared convolution filter reused everywhere — and beyond just the parameter count, it would also need to see training examples with that specific pattern at *every* specific location it needs to learn to detect it at, since nothing learned about detecting the pattern at one location transfers to a different location at all.

*One-liner: a useful local pattern (like a vertical edge) is assumed to be worth detecting regardless of where it appears in the image, so reusing the same filter weights everywhere directly encodes that assumption and only requires learning the pattern once — a fully-connected layer with no weight sharing would need a separate, independent set of weights for every single location, requiring vastly more parameters and needing to separately learn the same pattern at every possible position rather than generalizing it across the whole image.*

**Q: Write the formula for a convolution's output feature map size, and use it: a 32x32 input, 5x5 filter, stride 1, no padding — what's the output size?**
A: The formula: `output_size = (input_size - filter_size + 2·padding) / stride + 1`. Plugging in the given values: input_size=32, filter_size=5, padding=0 (no padding), stride=1.

`output_size = (32 - 5 + 2·0) / 1 + 1 = 27/1 + 1 = 27 + 1 = 28`.

So the output feature map is 28x28. The intuition behind why it shrinks at all (even with stride 1): the filter can't be centered at positions too close to the image's edge, since part of the filter would extend past the image boundary — with a 5x5 filter, the filter's top-left corner can only validly start at positions `0` through `32-5=27` (28 total valid starting positions along each dimension), which is exactly why the output ends up 28x28 rather than the full 32x32 — the filter "loses" a border region around the edge where it can't be fully applied without padding to compensate for this boundary effect.

*One-liner: `output_size = (input_size - filter_size + 2·padding) / stride + 1` — for a 32x32 input, 5x5 filter, stride 1, no padding: `(32-5+0)/1+1 = 28`, giving a 28x28 output, since without padding the filter can't be validly centered in the border region near the image's edges, shrinking the output slightly relative to the input.*

**Q: How does max pooling build in translation invariance, mechanically — walk through why a slightly shifted feature still gets detected?**
A: Max pooling looks at a small local region of a feature map (say, a 2x2 block) and keeps only the single highest value within that region, discarding the rest. Think about what a "high value" in a feature map actually represents: it's the strength of a match between the filter's learned pattern and whatever was at that specific location in the previous layer's output — a high value means "this specific pattern was strongly detected right here."

Now imagine the exact pattern a filter is looking for (say, part of an eye shape) appears in the image, but shifted by just one pixel compared to where it appeared in some other, slightly different version of a similar image. Without pooling, the feature map's single highest-activation pixel for this pattern would be at a slightly different exact position between these two cases — a layer further downstream that's sensitive to the *exact* pixel position of that activation would see a difference between these two cases, even though the underlying pattern (the eye shape being present) is genuinely the same in both.

Max pooling specifically smooths over this: if the high-activation pixel falls anywhere *within* the same local pooling region (say, the same 2x2 block) in both the shifted and unshifted cases, max pooling picks up that same maximum value either way, regardless of its *exact* position within that small region — the pooled output doesn't distinguish between "the strong activation was at the top-left corner of this 2x2 block" versus "it was at the bottom-right corner of this same block"; it just reports "there was a strong activation somewhere in this region." This is exactly what builds in a degree of tolerance to small positional shifts: as long as a detected feature's shift is small enough to still fall within the same local pooling window, the pooled output remains the same, even though the feature's *exact* pixel position genuinely moved.

*One-liner: max pooling keeps only the strongest activation within each small local region, discarding exactly *where* within that region the strongest value came from — so if a detected feature shifts by a small amount but still falls within the same pooling window, the pooled output is identical either way, which is exactly the mechanism that builds in tolerance to small positional shifts (translation invariance) rather than the network being sensitive to a feature's exact pixel position.*

**Q: Why do early CNN layers tend to learn simple features like edges, while later layers learn increasingly complex features like object parts — is this a deliberate design choice, or does it follow necessarily from the architecture?**
A: This isn't something explicitly designed or hard-coded anywhere — nobody tells the first layer "you must learn edges" — it follows necessarily from what each layer actually has available to compute with, given the math of convolution and what's been handed to it as input.

The very first convolutional layer operates directly on raw pixel values — a small filter (say, 3x3 or 5x5) can only examine a small local neighborhood of raw pixels at once, with no prior processing to build on at all. Given just a small raw-pixel neighborhood and nothing else, the only patterns that are directly, mathematically expressible as "weighted combinations of nearby raw pixel values" *are* fairly simple ones — brightness changes in a particular direction (edges), local color blobs, simple textures. There's no way for a single small filter, looking only at a handful of raw pixel values with no other context, to directly represent something as complex as "this is an eye" or "this is a car wheel" — that level of complexity simply isn't expressible from a small raw-pixel neighborhood alone, regardless of how the filter's weights are trained.

The second convolutional layer, however, doesn't operate on raw pixels at all — it operates on the *feature maps* the first layer already produced (which already encode "where are the edges, where are the color blobs"). A filter in this second layer can combine *these already-detected simple patterns* together — and combining several detected edges in a particular spatial arrangement can represent something more complex, like a corner or a simple shape, that wasn't directly expressible from raw pixels alone. This same logic compounds with each subsequent layer: each layer builds on the already-more-abstract representations the previous layer produced, which is exactly why complexity necessarily increases with depth — it's a direct, forced consequence of what each layer has available to compute from, not an explicit design instruction given to any specific layer.

*One-liner: this isn't explicitly designed anywhere — it follows necessarily from what each layer has available to compute with: the first layer only has small neighborhoods of raw pixels to work with, from which only simple patterns (edges, blobs) are mathematically expressible at all; each subsequent layer operates on the already-more-abstract feature maps the previous layer produced, letting it combine already-detected simple patterns into something more complex — a direct, forced consequence of the architecture, not an instruction given to any specific layer.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 07 Model Optimization and Performance Improvement]] · Downstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 09 Transfer Learning]]
- Related permanent note: [[03 Permanent Notes/Convolutional Neural Networks Learn Spatial Features]]
- Related code snippet: [[04 Code Snippets/ML/CNN Image Classifier with Data Augmentation]]
</content>
