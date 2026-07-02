# Transfer Learning Reuses Pretrained Models

## Core Idea
- Transfer learning reuses knowledge from a model trained on a large source task to solve a related target task with less data and less training effort.

## Why It Matters
- It reduces the cost of building strong models from scratch.
- It is one of the most practical ways to apply deep learning to real projects with limited labeled data.

## Explanation
- A pretrained model already contains useful feature representations learned from a broad dataset.
- In a new task, you can either use that model as a fixed feature extractor or fine-tune some or all of its layers.
- This works especially well in computer vision and NLP, where pretrained models capture reusable patterns.

## Examples
- Using a pretrained CNN for image classification on a smaller custom dataset.
- Fine-tuning a pretrained transformer model for a downstream text classification task.

## Links
- Source literature note: [[02 Literature Notes/Courses/Deep Learning - Lesson 09 Transfer Learning]]
- Related notes: [[02 Literature Notes/Courses/Deep Learning - Lesson 08 Convolutional Neural Networks]]
- Related project: [[05 Projects/Active/Transfer Learning Image Classifier]]
