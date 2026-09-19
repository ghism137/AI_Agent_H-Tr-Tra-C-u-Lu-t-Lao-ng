import json
from pathlib import Path
from backend.ingestion.pdf_text_extractor import extract_pdf_text

ROOT = Path('.')
selection = json.loads(Path('data/registry/source_selection.json').read_text(encoding='utf-8')).get('doc:02/2025/NĐ-CP')
sources = json.loads((ROOT / 'data' / 'registry' / 'sources.json').read_text(encoding='utf-8'))
body_source = next(s for s in sources if s['path'] == selection['body'])

try:
    body_blocks = extract_pdf_text(ROOT / body_source['path'], first_page=1, last_page=9)
    text = '\n'.join(b.get('text', '') for b in body_blocks)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'khoản 5 Điều 14' in line:
            print(f"Found: {lines[i-1:i+3]}")
            print("---")
except Exception as e:
    print(e)
