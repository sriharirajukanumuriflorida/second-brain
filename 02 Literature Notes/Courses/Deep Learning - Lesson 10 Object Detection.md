# Deep Learning - Lesson 10 Object Detection

> Depth goal: understand precisely what object detection adds on top of classification (bounding boxes + multiple objects per image), why YOLO's single-pass design is fast, how non-max suppression resolves duplicate detections, and the actual quantization tradeoff behind TensorFlow Lite conversion.

## Source
- Course: Deep Learning
- Lesson / Chapter: Lesson 10 - Object Detection
- Resource: [[07 Resources Library/Deep Learning/Slides/Lesson_10_Object_Detection.pdf]]
- Related Notebooks:
  - [[07 Resources Library/Deep Learning/Notebooks/10.07_Object_Detection_with_YOLO.ipynb]]
  - [[07 Resources Library/Deep Learning/Notebooks/10.10_Converting_TensorFlow_Model_to_TensorFlow_Lite_Model.ipynb]]

---

## 1. Mental Model

**Image classification answers "what is in this image?" (one label for the whole image); object detection answers "what is in this image, and exactly where, for potentially multiple objects at once?" — adding both localization (bounding boxes) and multiplicity (zero, one, or many objects per image) on top of classification's single-label-per-image assumption.**

> Key intuition: **object detection isn't a separate, unrelated task from classification — it's classification with the output shape generalized** from "one label" to "a variable-length list of (label, bounding box, confidence) tuples." Every object-detection architecture is, at its core, solving a harder version of the same underlying recognition problem CNNs already solve, plus the additional problem of figuring out *where* and *how many*.

---

## 2. How It Actually Works

### 2.1 The added complexity versus plain classification
Classification assumes exactly one label per image, with no notion of "where" in the image that label applies. Object detection has to additionally solve: **how many objects are present** (a variable, unknown number per image), **where each one is** (a bounding box — typically center coordinates plus width/height, or corner coordinates), and **what each one is** (a class label, same as classification) — all simultaneously, for every object present, with no prior knowledge of how many objects a given image will contain.

### 2.2 YOLO's single-pass design ("You Only Look Once")
Older object-detection approaches (predating YOLO) often worked by first proposing many candidate regions that *might* contain an object, then separately classifying each candidate region one at a time — this two-stage "propose, then classify each proposal" approach is fundamentally slow, since it requires running classification many times per image (once per candidate region).

YOLO's core innovation is treating detection as a *single* regression problem, solved in one forward pass through the network: the input image is divided into a grid, and for each grid cell, the network directly predicts (in one shot, for the whole image at once) a fixed number of candidate bounding boxes, each with its predicted coordinates, a confidence score (how likely this box actually contains an object), and class probabilities — all computed simultaneously by one single network pass over the whole image, rather than requiring a separate pass per candidate region. This single-pass design is exactly what makes YOLO fast enough for real-time video applications, where the "look once instead of look-and-classify-many-times" design directly translates into dramatically fewer total computations per image.

### 2.3 Non-max suppression — resolving duplicate detections
Because YOLO's grid-based approach predicts multiple candidate boxes, it's common for several overlapping candidate boxes to all detect the *same* real object (slightly different box coordinates, but clearly referring to the same physical object in the image) — without correction, this would report the same object multiple times. **Non-max suppression (NMS)** resolves this: among a group of candidate boxes that overlap significantly with each other (measured via **Intersection over Union**, IoU — the overlap area divided by the combined area of both boxes) and are predicted to be the same class, keep only the single highest-confidence box and discard the rest as redundant duplicates of the same underlying detection.

### 2.4 Deployment: TensorFlow Lite and quantization
Moving a trained model from a development notebook (running on a powerful machine/GPU) to a resource-constrained deployment environment (a mobile phone, an embedded device) requires addressing real constraints: limited memory, limited compute, and often no GPU at all. **TensorFlow Lite** converts a trained TensorFlow model into a more compact, optimized format specifically suited for these constrained environments — frequently applying **quantization** (reducing weight precision, e.g., from 32-bit floating point down to 8-bit integers) as part of this conversion, directly analogous to the quantization concept covered in LLM Efficiency, just applied here to a vision model rather than a language model: fewer bits per weight means a smaller model file and faster inference on hardware without specialized high-precision math units, at the cost of a small amount of potential accuracy loss that needs to be validated, not assumed negligible.

---

## 3. Implementation

Assumed stack: `tensorflow`, a pretrained YOLO-style model (via `ultralytics` or similar).

### Running Inference with a Pretrained YOLO Model
```python
# Illustrative pattern -- exact API varies by YOLO implementation/version.
from ultralytics import YOLO

model = YOLO("yolov8n.pt")   # pretrained, nano-size model
results = model("path/to/image.jpg")

for result in results:
    for box in result.boxes:
        print(f"class={result.names[int(box.cls)]}  confidence={float(box.conf):.2f}  bbox={box.xyxy.tolist()}")
```

### Non-Max Suppression from Scratch
```python
import numpy as np

def iou(box_a, box_b):
    xa, ya = max(box_a[0], box_b[0]), max(box_a[1], box_b[1])
    xb, yb = min(box_a[2], box_b[2]), min(box_a[3], box_b[3])
    inter = max(0, xb - xa) * max(0, yb - ya)
    area_a = (box_a[2]-box_a[0]) * (box_a[3]-box_a[1])
    area_b = (box_b[2]-box_b[0]) * (box_b[3]-box_b[1])
    return inter / (area_a + area_b - inter + 1e-9)

def non_max_suppression(boxes, scores, iou_threshold=0.5):
    order = np.argsort(scores)[::-1]   # highest confidence first
    keep = []
    while len(order) > 0:
        current = order[0]
        keep.append(current)
        remaining = [i for i in order[1:] if iou(boxes[current], boxes[i]) < iou_threshold]
        order = remaining
    return keep

boxes = [[10,10,50,50], [12,12,52,52], [100,100,150,150]]   # first two overlap heavily
scores = [0.9, 0.75, 0.95]
print("kept box indices:", non_max_suppression(boxes, scores))
# Expect the lower-confidence overlapping duplicate (index 1) to be suppressed.
```

### Converting to TensorFlow Lite with Quantization
```python
import tensorflow as tf

converter = tf.lite.TFLiteConverter.from_saved_model("saved_model_path")
converter.optimizations = [tf.lite.Optimize.DEFAULT]   # applies post-training quantization
tflite_model = converter.convert()

with open("model.tflite", "wb") as f:
    f.write(tflite_model)
print(f"TFLite model size: {len(tflite_model) / 1e6:.2f} MB")
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Single-stage (YOLO) vs two-stage detectors** | Single-stage for real-time/speed-critical applications; two-stage approaches can achieve higher accuracy at the cost of speed. |
| **IoU threshold for NMS** | Lower threshold suppresses more aggressively (fewer duplicate risk, more risk of removing genuinely separate nearby objects); tune per use case. |
| **Confidence threshold** | Higher threshold reduces false positives but risks missing genuine low-confidence detections; tune against validation data. |
| **Quantization for deployment** | Apply when deploying to constrained hardware; always validate accuracy on a held-out set post-quantization, don't assume negligible loss. |
| **Model size (nano/small/large variants)** | Match model size to the actual deployment hardware's compute/memory budget and the task's accuracy requirements. |

---

## 5. Failure Modes & Gotchas

- Skipping non-max suppression and reporting the same physical object as multiple separate detections.
- Setting the IoU threshold too aggressively, accidentally suppressing genuinely distinct, nearby objects as if they were duplicates.
- Assuming quantization has negligible accuracy impact without actually validating post-quantization performance.
- Deploying a large, high-accuracy model variant to hardware that can't run it in real time, defeating the purpose of a real-time detection use case.
- Confusing confidence score (how sure the model is a box contains an object) with classification probability (which specific class that object is) — these are related but distinct outputs.

---

## 6. Self-Check

1. What does object detection add on top of plain image classification?
2. Why is YOLO's single-pass design faster than a two-stage "propose then classify" approach?
3. What problem does non-max suppression solve, and how does IoU factor into it?
4. What does TensorFlow Lite's quantization actually trade off, and why does it matter for deployment?

---

## 7. Interview Q&A

**Q: What does object detection add on top of plain image classification — be specific about the output shape, not just "it finds objects."**
A: Plain image classification's output is fixed-shape and simple: one label (or one probability distribution over a fixed set of classes) per image, with no notion of location at all — the model is only ever answering "what's the single most prominent/relevant thing in this whole image."

Object detection's output is fundamentally different in shape: a *variable-length list* of detections, where each individual detection is itself a tuple of (class label, bounding box coordinates, confidence score). The list's length isn't fixed or known in advance — an image might contain zero objects of interest, one, or a dozen, and the model has to determine this count itself as part of its output, rather than it being a fixed, pre-known output dimensionality the way classification's "one label" always is. Each individual detection within that list also carries more information than classification's single label did — not just "what class is this," but also "exactly where in the image is it" (the bounding box) and "how confident is the model that this specific detection is both correctly located and correctly classified."

This is exactly why object detection is structurally harder than classification: it's not just "classify, but also localize" as an independent add-on — it's solving for an unknown, variable number of simultaneous (class, location, confidence) predictions per image, a genuinely more complex output structure than classification's single, fixed-shape label ever has to deal with.

*One-liner: classification outputs one fixed-shape label per image with no location information; object detection outputs a variable-length list of (class, bounding box, confidence) tuples, where even the *number* of detections isn't known in advance and has to be determined by the model itself — a genuinely more complex output structure than classification's single, fixed-shape prediction.*

**Q: Why is YOLO's single-pass design faster than an older two-stage "propose candidate regions, then classify each one" approach?**
A: A two-stage approach's computational cost scales with the *number of candidate regions it proposes* — if it generates, say, 2,000 candidate regions that might contain an object, it then has to run a full classification pass on each of those 2,000 regions individually, one at a time (or in smaller batches) — meaning the total compute cost is roughly 2,000 times the cost of a single classification pass, just to process one image.

YOLO's single-pass design computes predictions for the *entire image, for every grid cell, in one single forward pass through the network* — rather than running the network repeatedly once per candidate region, it runs the network exactly once per image, and that one pass directly outputs all the bounding boxes, confidences, and class predictions across the whole image simultaneously, for every grid cell at once. This is a fundamentally different computational shape: instead of cost scaling with "however many candidate regions got proposed" (which could be in the thousands), cost scales with "one single pass over the image," regardless of how many objects actually turn out to be present in it.

This difference in computational shape is exactly why YOLO achieves dramatically higher speed, suitable for real-time video processing (where you need to process many frames per second) — a two-stage approach's cost, scaling with the number of proposed regions, makes real-time processing far more difficult to achieve, since you're paying for many separate classification passes per single image rather than just one.

*One-liner: a two-stage detector's cost scales with the number of candidate regions it proposes (potentially thousands, each needing its own separate classification pass) — YOLO instead runs one single forward pass over the entire image, directly outputting all predictions for every grid cell at once, meaning its cost scales with "one pass per image" rather than "one pass per candidate region," which is exactly why it achieves the speed needed for real-time video processing.*

**Q: What specific problem does non-max suppression solve, and how does Intersection over Union (IoU) factor into solving it?**
A: Because an object-detection model (like YOLO, predicting boxes across a grid) often produces several candidate bounding boxes that all overlap substantially and refer to the *same single real object* in the image (slightly different coordinates for the same physical thing, since nearby grid cells or overlapping predictions can each independently "notice" the same object), without any correction, the model would report that single real object as multiple separate detections — which is wrong; there's genuinely only one object there, not several.

Non-max suppression resolves this by specifically identifying which candidate boxes are likely duplicates of the same underlying object, versus which ones genuinely represent different, separate objects — and the tool for making this distinction is IoU (Intersection over Union): the area where two boxes overlap, divided by the total combined area the two boxes cover together. A high IoU between two candidate boxes (close to 1) means they overlap almost completely — strong evidence they're both detecting the same single object, just with slightly different predicted coordinates. A low IoU (close to 0) means the boxes barely overlap at all — evidence they're likely detecting two genuinely different, separate objects that just happen to be positioned somewhat near each other in the image.

Non-max suppression's actual algorithm: among a group of candidate boxes (for the same predicted class) whose IoU with each other exceeds some chosen threshold, keep only the single box with the highest confidence score, and discard the rest as redundant duplicates — while boxes with a low IoU relative to each other (genuinely different, separate objects) are each kept independently, since their low overlap is evidence they're not duplicates of each other at all.

*One-liner: non-max suppression solves the problem of a single real object being reported multiple times by several overlapping candidate boxes — IoU (overlap area divided by combined area) is the tool used to tell apart "these boxes are duplicates of the same object" (high IoU) from "these boxes are genuinely different, separate objects" (low IoU), keeping only the highest-confidence box among a high-IoU group and discarding the rest as redundant.*

**Q: What does TensorFlow Lite's quantization actually trade off, and why does that tradeoff matter specifically for deployment to constrained devices?**
A: Quantization, in this context, reduces the numeric precision used to store a model's weights — typically converting from 32-bit floating-point numbers down to 8-bit integers (or similar lower-precision formats). This is a lossy compression: representing a number with fewer bits necessarily discards some precision, which means the model's computations after quantization are no longer mathematically identical to the original, full-precision model's computations — there's some real, if usually small, risk of accuracy degradation as a direct consequence of this lost precision.

In exchange for this precision loss, quantization delivers two very concrete, directly useful benefits for constrained deployment: the model's file size shrinks substantially (fewer bits per weight means a smaller total model file, which matters directly on a mobile device or embedded system with genuinely limited storage), and inference often runs faster, specifically on hardware that either lacks specialized high-precision floating-point math units entirely, or has highly optimized, fast integer-arithmetic hardware paths that 8-bit integer computation can take direct advantage of in a way full 32-bit floating-point math often can't on that same constrained hardware.

Why this tradeoff matters specifically for deployment, rather than for a model running on a powerful development machine or server: a mobile phone or embedded device genuinely has hard, real constraints on storage space, available memory, and compute power that a development GPU workstation simply doesn't have to the same degree — the real-world benefit of a smaller, faster model is often the difference between an application actually being usable on that constrained device at all versus not. But this benefit isn't free or automatic — the accuracy impact genuinely needs to be checked directly (the same evaluation discipline covered throughout the Evaluation domain, just applied here to a vision model) on a held-out validation set after quantization, rather than assumed to be negligible just because quantization is commonly used — the actual impact can vary by model and task, and should be verified, not assumed.

*One-liner: quantization reduces weight precision (typically 32-bit float down to 8-bit integer), trading some real, if usually small, accuracy loss for a substantially smaller model file size and often faster inference on hardware that favors integer arithmetic — this tradeoff matters specifically for constrained deployment devices (mobile, embedded) where storage and compute are hard, real limits, but the accuracy impact needs to be directly validated on held-out data afterward, not assumed negligible just because quantization is commonly used.*

---

## 8. Links
- Related course note: [[02 Literature Notes/Courses/Deep Learning]]
- Related map: [[06 Maps of Content/Deep Learning Concepts]]
- Upstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 09 Transfer Learning]] · Downstream: [[02 Literature Notes/Courses/Deep Learning - Lesson 11 Recurrent Neural Network]]
</content>
