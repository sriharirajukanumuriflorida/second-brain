# Chat Template and Assistant Loss Mask

> Domain 7 · Supervised Fine-Tuning & Instruction Tuning. Serialize role messages and mark only assistant tokens as supervised targets.

```python
def render_chat(messages):
    tokens, mask = [], []
    for m in messages:
        text = f"<{m['role']}> " + m['content'].strip() + " <eos>"
        toks = text.split()
        tokens.extend(toks)
        mask.extend([m['role'] == 'assistant'] * len(toks))
    return tokens, mask

msgs = [{'role':'user','content':'Define SFT'}, {'role':'assistant','content':'SFT imitates demonstrations.'}]
print(list(zip(*render_chat(msgs))))
```


Related: [[04 Code Snippets/LLM/Assistant Only Cross Entropy]]
