# Optimization Shapes How Neural Networks Learn

## Core Idea
- Optimization algorithms determine how a neural network updates its parameters, which strongly affects training speed, stability, and final model quality.

## Why It Matters
- Good optimization choices can make the difference between a model that trains well and one that stalls or overfits.
- It is a core practical lever in deep learning beyond model architecture alone.

## Explanation
- Basic gradient descent updates weights in the direction that reduces loss.
- Variants like Momentum, AdaGrad, RMSProp, and Adam change how updates are scaled or accumulated over time.
- Regularization methods like dropout complement optimization by improving generalization, not just convergence.

## Examples
- Using Adam to train a deep model faster and more reliably than plain SGD.
- Applying dropout to reduce overfitting in a neural network.

## Links
- Source literature note: [[02 Literature Notes/Courses/Deep Learning - Lesson 07 Model Optimization and Performance Improvement]]
- Related notes: [[03 Permanent Notes/Convolutional Neural Networks Learn Spatial Features]]
- Related project:
