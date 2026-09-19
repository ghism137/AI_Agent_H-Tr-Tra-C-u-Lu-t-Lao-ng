import json
from pathlib import Path
from backend.ingestion.html_extractor import extract_government_html

blocks = extract_government_html(Path('data/raw/official/158-2025-ND-CP.html'))
for i, block in enumerate(blocks):
    if 'Điều 21' in block['text']:
        start = max(0, i-1)
        end = min(len(blocks), i+2)
        print('---')
        for j in range(start, end):
            print(f"[{j}] {blocks[j]['text']}")
