# Recurrent Neural Networks Model Sequence Dependencies

## Core Idea
- Recurrent neural networks model ordered data by carrying information forward across sequence steps, which helps them learn temporal dependencies.

## Why It Matters
- They make sequence problems like text, time series, and video modeling tractable.
- They provide the conceptual bridge from feedforward vision models to language and temporal learning systems.

## Explanation
- An RNN processes input one step at a time while maintaining a hidden state that summarizes prior context.
- This lets the model use earlier information when interpreting later tokens or timesteps.
- LSTMs improve on basic RNNs by handling longer-range dependencies more effectively.

## Examples
- Text classification using an RNN or LSTM.
- Modeling sequential sensor data or video frame sequences.

## Links
- Source literature note: [[02 Literature Notes/Courses/Deep Learning - Lesson 11 Recurrent Neural Network]]
- Related notes: [[03 Permanent Notes/Transformers Use Attention for Sequence Modeling]]
- Related project:
