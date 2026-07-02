# Autoencoders Learn Compact Representations

## Core Idea
- Autoencoders learn a compressed latent representation of input data and then reconstruct the original input from that representation.

## Why It Matters
- They provide a practical way to learn structure in data without requiring explicit labels.
- They are useful for dimensionality reduction, representation learning, reconstruction, and anomaly-oriented workflows.

## Explanation
- An autoencoder has an encoder that maps input data into a smaller latent space and a decoder that reconstructs the input from that latent code.
- The model learns by minimizing reconstruction error, which encourages it to keep the most important information.
- This makes autoencoders useful when the goal is understanding or compressing data rather than direct supervised prediction.

## Examples
- Compressing image data into a lower-dimensional latent space.
- Detecting unusual inputs by identifying cases with high reconstruction error.

## Links
- Source literature note: [[02 Literature Notes/Courses/Deep Learning - Lesson 13 Getting Started with Autoencoders]]
- Related notes: [[03 Permanent Notes/Convolutional Neural Networks Learn Spatial Features]]
- Related project:
