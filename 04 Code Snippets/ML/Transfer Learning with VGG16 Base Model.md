# Transfer Learning with VGG16 Base Model

## Purpose
- Build a transfer learning classifier by reusing VGG16 as the base model and adding a custom dense head.

## Language
- Python

## Snippet
```python
from keras.applications.vgg16 import VGG16
from keras.models import Model
from keras.layers import Dense, Flatten

base_model = VGG16(include_top=False, input_shape=(300, 300, 3))
flat1 = Flatten()(base_model.layers[-1].output)
class1 = Dense(1024, activation="relu")(flat1)
output = Dense(10, activation="softmax")(class1)

model = Model(inputs=base_model.inputs, outputs=output)
```

## Notes
- `include_top=False` removes the original classifier so you can attach a task-specific head.
- This pattern is useful when adapting pretrained image models to a new dataset.
- Freeze or selectively unfreeze base layers depending on whether you want feature extraction or fine-tuning.

## Links
- Source note: [[02 Literature Notes/Courses/Deep Learning - Lesson 09 Transfer Learning]]
- Related project: [[05 Projects/Active/Transfer Learning Image Classifier]]
