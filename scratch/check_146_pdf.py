import json
from pathlib import Path
from backend.ingestion.pdf_text_extractor import extract_pdf_text
from backend.ingestion.parser import parse_legal_document

ROOT = Path('.')
selection = json.loads(Path('data/registry/source_selection.json').read_text(encoding='utf-8')).get('doc:146/2018/NĐ-CP')
sources = json.loads((ROOT / 'data' / 'registry' / 'sources.json').read_text(encoding='utf-8'))
document = next(d for d in json.loads((ROOT / 'data' / 'registry' / 'documents.json').read_text(encoding='utf-8')) if d['doc_id'] == 'doc:146/2018/NĐ-CP')
metadata = {'doc_id': document['doc_id'], 'valid_from': document['valid_from'], 'doc_number': document['doc_number'], 'doc_title': document['title'], 'doc_type': document['doc_type'], 'issued_date': document.get('issued_date'), 'verification_status': 'verified', 'content_kind': 'normative'}

body_source = next(s for s in sources if s['path'] == selection['body'])

page_intervals = {
    "146/2018/NĐ-CP": (1, 57),
}
first_page, last_page = page_intervals[document["doc_number"]]
body_blocks = extract_pdf_text(ROOT / body_source['path'], first_page=first_page, last_page=last_page)
result = parse_legal_document('', metadata, body_blocks)

for article in result['articles']:
    path = '/'.join(article['structural_path'])
    if 'article:14' in path:
        print(f"path: {path}")
