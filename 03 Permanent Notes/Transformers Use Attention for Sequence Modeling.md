# Transformers Use Attention for Sequence Modeling

## Core Idea
- Transformers model sequences by using attention to relate tokens directly, instead of relying only on step-by-step recurrence.

## Why It Matters
- They power many of the strongest modern NLP systems.
- They scale well to large pretrained models that can be adapted to many downstream tasks.

## Explanation
- Attention lets the model weigh which parts of an input sequence matter most for each token.
- This makes it easier to capture long-range dependencies than with basic recurrent architectures.
- Pretrained transformer models like BERT can then be fine-tuned for tasks such as classification, search, and question answering.

## Examples
- Using BERT for text classification.
- Adapting a pretrained transformer for summarization or question answering.

## Links
- Source literature note: [[02 Literature Notes/Courses/Deep Learning - Lesson 12 Transformer Models for NLP]]
- Related notes: [[03 Permanent Notes/Transfer Learning Reuses Pretrained Models]]
- Related project:
