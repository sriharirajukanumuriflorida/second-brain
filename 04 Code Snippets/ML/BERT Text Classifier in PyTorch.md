# BERT Text Classifier in PyTorch

## Purpose
- Build a text classifier by reusing a pretrained BERT model and adding a simple classification head.

## Language
- Python

## Snippet
```python
from transformers import BertTokenizer, BertModel
from torch import nn

tokenizer = BertTokenizer.from_pretrained("bert-base-cased")

class BertClassifier(nn.Module):
    def __init__(self, dropout=0.5):
        super().__init__()
        self.bert = BertModel.from_pretrained("bert-base-cased")
        self.dropout = nn.Dropout(dropout)
        self.linear = nn.Linear(768, 5)
        self.relu = nn.ReLU()

    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=False,
        )
        dropout_output = self.dropout(pooled_output)
        linear_output = self.linear(dropout_output)
        final_output = self.relu(linear_output)
        return final_output
```

## Notes
- `BertTokenizer.from_pretrained(...)` prepares text inputs in the format BERT expects.
- `BertModel.from_pretrained(...)` reuses pretrained language representations.
- Replace `nn.Linear(768, 5)` with the output size for your own label set.

## Links
- Source note: [[02 Literature Notes/Courses/Deep Learning - Lesson 12 Transformer Models for NLP]]
- Related project:
