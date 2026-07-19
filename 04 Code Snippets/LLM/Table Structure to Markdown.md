# Table Structure to Markdown

> Domain 10 · Document Ingestion & Parsing (PDF/table/OCR). Reconstruct table cells into a grid and serialize for LLM-readable chunks.

```python
def reconstruct_table(cells):
    max_r = max(c["row"] for c in cells); max_c = max(c["col"] for c in cells)
    grid = [["" for _ in range(max_c + 1)] for _ in range(max_r + 1)]
    for c in cells:
        grid[c["row"]][c["col"]] = c["text"].strip()
    return grid

def table_to_markdown(grid):
    header = "| " + " | ".join(grid[0]) + " |"
    sep = "| " + " | ".join(["---"] * len(grid[0])) + " |"
    rows = ["| " + " | ".join(r) + " |" for r in grid[1:]]
    return "\n".join([header, sep] + rows)

cells = [{"row":0,"col":0,"text":"Item"},{"row":0,"col":1,"text":"Price"},
         {"row":1,"col":0,"text":"Widget"},{"row":1,"col":1,"text":"$10"}]
print(table_to_markdown(reconstruct_table(cells)))
```


Related: [[04 Code Snippets/LLM/Layout Reading Order Reconstructor]]
