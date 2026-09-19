import json
from pathlib import Path
from backend.ingestion.docx_extractor import extract_docx
from backend.ingestion.parser import parse_legal_document

ROOT = Path('.')
selection = json.loads(Path('data/registry/source_selection.json').read_text(encoding='utf-8')).get('doc:74/2025/NĐ-CP')
sources = json.loads((ROOT / 'data' / 'registry' / 'sources.json').read_text(encoding='utf-8'))
document = next(d for d in json.loads((ROOT / 'data' / 'registry' / 'documents.json').read_text(encoding='utf-8')) if d['doc_id'] == 'doc:74/2025/NĐ-CP')
metadata = {'doc_id': document['doc_id'], 'valid_from': document['valid_from'], 'doc_number': document['doc_number'], 'doc_title': document['title'], 'doc_type': document['doc_type'], 'issued_date': document.get('issued_date'), 'verification_status': 'verified', 'content_kind': 'normative'}

body_source = next(s for s in sources if s['path'] == selection['body'])
body_blocks = extract_docx(ROOT / body_source['path'])
result = parse_legal_document('', metadata, body_blocks)

for article in result['articles']:
    path = '/'.join(article['structural_path'])
    if 'article:4' in path:
        print(f"{path} -> {article['content'][:100]}")
