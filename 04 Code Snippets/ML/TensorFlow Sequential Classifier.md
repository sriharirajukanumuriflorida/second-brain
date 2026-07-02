# TensorFlow Sequential Classifier

## Purpose
- Build and train a simple dense neural network using TensorFlow's Sequential API.

## Language
- Python

## Snippet
```python
import tensorflow as tf
from tensorflow.keras import layers

model = tf.keras.Sequential()
model.add(layers.Flatten(input_shape=(28, 28)))
model.add(layers.Dense(64, activation="relu"))
model.add(layers.Dense(64, activation="relu"))
model.add(layers.Dense(10, activation="softmax"))

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

model.fit(x_train, y_train, epochs=5)
```

## Notes
- `Sequential()` is best when layers flow in a simple stack.
- `Flatten` converts 2D image input into a 1D vector for dense layers.
- `compile(...)` defines optimization, loss, and evaluation metrics before training.

## Links
- Source note: [[02 Literature Notes/Courses/Deep Learning - Lesson 05 TensorFlow]]
- Related project:
