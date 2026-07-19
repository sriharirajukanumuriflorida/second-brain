# Layout Reading Order Reconstructor

> Domain 10 · Document Ingestion & Parsing (PDF/table/OCR). Sort toy layout boxes into human reading order using row grouping and coordinates.

```python
def reading_order(boxes, y_tol=8):
    rows = []
    for b in sorted(boxes, key=lambda x: (x["y0"], x["x0"])):
        placed = False
        for row in rows:
            if abs(row[0]["y0"] - b["y0"]) <= y_tol:
                row.append(b); placed = True; break
        if not placed:
            rows.append([b])
    ordered = []
    for row in rows:
        ordered.extend(sorted(row, key=lambda x: x["x0"]))
    return ordered

boxes = [
    {"text":"Total", "x0":320, "y0":200}, {"text":"Invoice", "x0":40, "y0":40},
    {"text":"Acme", "x0":40, "y0":120}, {"text":"$42", "x0":410, "y0":200},
]
print(" | ".join(b["text"] for b in reading_order(boxes)))
```


Related: [[04 Code Snippets/LLM/Table Structure to Markdown]]
