# Experiment 02 — Fine Tuned Upper Layers

## 🎯 Objective
- Compare selective fine-tuning of upper VGG16 layers against the frozen-VGG16 baseline.

## 🧠 Model
- Architecture: VGG16 feature extractor + custom classifier head
- Hyperparameters:
  - Input shape: `(300, 300, 3)`
  - Dense head: `Dense(1024, activation="relu")`
  - Output layer: `Dense(10, activation="softmax")`
  - Warmup learning rate: `1e-4`
  - Fine-tune learning rate: `1e-5`
  - Upper trainable layers: last 4 layers of VGG16

## 📂 Dataset
- Source: `07 Resources Library/Capstone/Datasets/Capstone 2/Part 1/dataset_hist_structures 3/dataset_hist_structures/`
- Preprocessing:
  - Train/validation data from `Stuctures_Dataset/`
  - Intended held-out test data from `Dataset_test/Dataset_test_original_1478/`
  - Corrupt test files filtered during experiment setup

## ⚙️ Training Setup
- Warmup epochs: 2
- Fine-tune epochs planned: 1
- Batch size: 16
- Optimizer: Adam
- Loss: sparse categorical crossentropy

## 📈 Results
- Metrics:
  - Warmup epoch 1 validation accuracy: `0.9257`
  - Warmup epoch 1 validation loss: `0.8814`
  - Warmup epoch 2 validation accuracy: `0.9186`
  - Warmup epoch 2 validation loss: `0.7577`
  - Fine-tune epoch: not completed
  - Test accuracy: not reached
- Observations:
  - Warmup performance was competitive with the frozen baseline.
  - The final fine-tune epoch stalled before completion, so this run is inconclusive.

## 📝 Notes
- This run used a filtered test-file list to avoid the corrupt JPEG seen in Experiment 01.
- The fine-tune phase should be rerun in a standalone script or notebook with checkpointing.

## 🔗 Related Project
- [[05 Projects/Active/Transfer Learning Image Classifier]]

## 🔗 Related Notes
- Permanent Notes:
  - [[03 Permanent Notes/Transfer Learning Reuses Pretrained Models]]
- Literature Notes:
  - [[02 Literature Notes/Courses/Deep Learning - Lesson 09 Transfer Learning]]
- Code Snippets:
  - [[04 Code Snippets/ML/Transfer Learning with VGG16 Base Model]]
