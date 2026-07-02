# Bidirectional LSTM Text Classifier

## Purpose
- Build a text-classification model using tokenization, padded sequences, and a bidirectional LSTM.

## Language
- Python

## Snippet
```python
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(train_articles)

train_sequences = tokenizer.texts_to_sequences(train_articles)
train_padded = pad_sequences(
    train_sequences,
    maxlen=max_length,
    padding=padding_type,
    truncating=trunc_type,
)

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(embedding_dim)),
    tf.keras.layers.Dense(embedding_dim, activation="relu"),
    tf.keras.layers.Dense(num_classes, activation="softmax"),
])
```

## Notes
- `Tokenizer` converts raw text into integer sequences.
- `pad_sequences(...)` makes sequence lengths uniform for batching.
- A bidirectional LSTM uses both forward and backward context, which can improve text classification.

## Links
- Source note: [[02 Literature Notes/Courses/Deep Learning - Lesson 11 Recurrent Neural Network]]
- Related project:
