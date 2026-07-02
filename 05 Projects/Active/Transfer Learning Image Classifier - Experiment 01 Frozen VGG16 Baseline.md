# Experiment 01 — Frozen VGG16 Baseline

## 🎯 Objective
- Measure baseline image-classification performance using a frozen VGG16 base model with a custom dense head.

## 🧠 Model
- Architecture: VGG16 feature extractor + custom classifier head
- Hyperparameters:
  - Input shape: `(300, 300, 3)`
  - Dense head: `Dense(1024, activation="relu")`
  - Output layer: `Dense(10, activation="softmax")`
  - Base model: frozen

## 📂 Dataset
- Source: `07 Resources Library/Capstone/Datasets/Capstone 2/Part 1/dataset_hist_structures 3/dataset_hist_structures/`
- Preprocessing:
  - Train/validation data from `Stuctures_Dataset/`
  - Held-out test data from `Dataset_test/Dataset_test_original_1478/`
  - Resize images to `(300, 300)`
  - Normalize pixel values
  - Apply light augmentation to training data only

## ⚙️ Training Setup
- Epochs: 3
- Batch size: 16
- Optimizer: Adam
- Learning rate: `1e-4`
- Loss: sparse categorical crossentropy

## 📈 Results
- Metrics:
  - Final training accuracy: `0.9644`
  - Final training loss: `0.2004`
  - Best validation accuracy: `0.9244`
  - Best validation loss: `0.6882`
  - Final validation accuracy: `0.9244`
  - Final validation loss: `0.7609`
  - Test accuracy: blocked
- Observations:
  - Frozen VGG16 produced a strong baseline on the heritage-structure training split.
  - Validation accuracy improved across all 3 epochs.
  - Held-out test evaluation failed because the test set contains at least one corrupt JPEG.
  - Corrupt file identified: `Dataset_test/Dataset_test_original_1478/stained_glass/9d1de848-bfd8-40e1-9686-0f8aba896655.jpg`

## 📝 Notes
- This experiment is the baseline for comparing later fine-tuning runs.
- Do not mix in `dataset_hist_structures 2/` because it appears to duplicate the training archive.
- Test-set evaluation should be rerun after removing or replacing the corrupt JPEG above.

## 🔗 Related Project
- [[05 Projects/Active/Transfer Learning Image Classifier]]

## 🔗 Related Notes
- Permanent Notes:
  - [[03 Permanent Notes/Transfer Learning Reuses Pretrained Models]]
- Literature Notes:
  - [[02 Literature Notes/Courses/Deep Learning - Lesson 09 Transfer Learning]]
- Code Snippets:
  - [[04 Code Snippets/ML/Transfer Learning with VGG16 Base Model]]
