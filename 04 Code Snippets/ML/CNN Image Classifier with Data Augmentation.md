# CNN Image Classifier with Data Augmentation

## Purpose
- Build a basic image-classification CNN with augmentation, convolution blocks, pooling, and dropout.

## Language
- Python

## Snippet
```python
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal", input_shape=(img_height, img_width, 3)),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])

num_classes = len(class_names)
model = Sequential([
    data_augmentation,
    layers.Rescaling(1.0 / 255),
    layers.Conv2D(16, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),
    layers.Conv2D(32, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, padding="same", activation="relu"),
    layers.MaxPooling2D(),
    layers.Dropout(0.2),
    layers.Flatten(),
    layers.Dropout(0.5),
    layers.Dense(128, activation="relu"),
    layers.Dense(num_classes),
])
```

## Notes
- Augmentation helps improve robustness by exposing the model to varied versions of the same images.
- `Rescaling` normalizes pixel values before they reach the convolution layers.
- Dropout is used here to reduce overfitting before the dense classifier head.

## Links
- Source note: [[02 Literature Notes/Courses/Deep Learning - Lesson 08 Convolutional Neural Networks]]
- Related project:
