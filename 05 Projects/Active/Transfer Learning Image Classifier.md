# Transfer Learning Image Classifier — ML Project

## 🎯 Goal
- Build an image classifier by reusing a pretrained VGG16 base model and adapting it to a new dataset.

## 📂 Dataset
- Source: `07 Resources Library/Capstone/Datasets/Capstone 2/Part 1/dataset_hist_structures 3/dataset_hist_structures/`
- Preprocessing notes:
  - Use `Stuctures_Dataset/` as the primary training corpus
  - Use `Dataset_test/Dataset_test_original_1478/` as the held-out test set
  - Ignore `dataset_hist_structures 2/` to avoid duplicate-data leakage

## 🗂️ Dataset Plan
- Candidate dataset type: labeled image classification dataset
- Preferred format: one folder per class
- Train/validation/test split:
  - Train: 85% of `Stuctures_Dataset/`
  - Validation: 15% of `Stuctures_Dataset/`
  - Test: use `Dataset_test_original_1478/`
- Image preparation:
  - Resize to `(300, 300)`
  - Normalize pixel values
  - Apply light augmentation for training only
- Quality checks:
  - Verify class balance
  - Remove corrupt or duplicate images
  - Confirm label names match output classes
- Class labels:
  - `altar`
  - `apse`
  - `bell_tower`
  - `column`
  - `dome(inner)`
  - `dome(outer)`
  - `flying_buttress`
  - `gargoyle`
  - `stained_glass`
  - `vault`

## 🧠 Model
- Architecture: VGG16 base model with a custom dense classification head
- Hyperparameters:
  - Input shape: `(300, 300, 3)`
  - Hidden layer: `Dense(1024, activation="relu")`
  - Output layer: `Dense(10, activation="softmax")`
  - Number of classes: `10`

## 🏋️ Training Plan
- Phase 1: Freeze the VGG16 base and train only the custom classifier head
- Phase 2: Unfreeze selected top layers for fine-tuning
- Optimizer candidate: Adam
- Loss candidate: categorical crossentropy or sparse categorical crossentropy
- Initial metrics:
  - Training accuracy
  - Validation accuracy
  - Validation loss
- Early stopping target:
  - Stop if validation loss no longer improves
- Comparison target:
  - Compare frozen-base results vs fine-tuned results

## 🧪 Experiments
- Experiment log:
  - **Experiment 1 — Frozen VGG16 baseline**
    - Status: completed for train/validation, blocked on test-set cleanup
    - Data: `Stuctures_Dataset/` train/validation split
    - Goal: measure baseline classification quality with feature extraction only
    - Note: [[05 Projects/Active/Transfer Learning Image Classifier - Experiment 01 Frozen VGG16 Baseline]]
  - **Experiment 2 — Fine-tuned upper layers**
    - Status: partial run completed, final fine-tune epoch stalled
    - Data: same train/validation split, then evaluate on `Dataset_test_original_1478/`
    - Goal: compare upper-layer fine-tuning against the frozen baseline
    - Note: [[05 Projects/Active/Transfer Learning Image Classifier - Experiment 02 Fine Tuned Upper Layers]]

## ✅ Experiment Checklist
- [x] Choose the target image dataset
- [x] Define class labels and output size
- [x] Prepare image resizing and normalization pipeline
- [x] Run baseline feature extraction with frozen VGG16
- [x] Record baseline metrics
- [x] Fine-tune selected upper layers
- [x] Compare fine-tuned results against baseline
- [ ] Save best model settings and observations

## 📈 Results
- Baseline metrics:
  - Final training accuracy: `0.9644`
  - Best validation accuracy: `0.9244`
  - Best validation loss: `0.6882`
- Fine-tuned metrics:
  - Warmup epoch 1 validation accuracy: `0.9257`
  - Warmup epoch 2 validation accuracy: `0.9186`
  - Warmup epoch 2 validation loss: `0.7577`
  - Final fine-tune epoch: stalled before completion
- Test-set metrics: baseline blocked by corrupt JPEG in `stained_glass/9d1de848-bfd8-40e1-9686-0f8aba896655.jpg`; fine-tune filtered test evaluation not reached before stall
- Observations:
  - Use this section to compare frozen-base vs fine-tuned behavior.
  - Watch for class imbalance effects across heritage-structure categories.
  - The frozen VGG16 baseline already performs strongly on the training/validation split.
  - Fine-tuning did not clearly outperform the frozen baseline before the run stalled.

## 📝 Notes
- Use this project as the practical workspace for applying transfer learning concepts from the Deep Learning course.
- The dataset contains two very similar archive copies (`dataset_hist_structures 2` and `dataset_hist_structures 3`); use one training source only to avoid leakage.

## 🔗 Related Literature Notes
- [[02 Literature Notes/Courses/Deep Learning - Lesson 09 Transfer Learning]]

## 🔗 Related Permanent Notes
- [[03 Permanent Notes/Transfer Learning Reuses Pretrained Models]]

## 🔗 Related Code Snippets
- [[04 Code Snippets/ML/Transfer Learning with VGG16 Base Model]]
