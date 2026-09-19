import json
from pathlib import Path
from backend.ingestion.pdf_text_extractor import extract_pdf_text
from backend.ingestion.parser import parse_legal_document

ROOT = Path('.')
selection = json.loads(Path('data/registry/source_selection.json').read_text(encoding='utf-8')).get('doc:75/2023/NĐ-CP')
sources = json.loads((ROOT / 'data' / 'registry' / 'sources.json').read_text(encoding='utf-8'))
document = next(d for d in json.loads((ROOT / 'data' / 'registry' / 'documents.json').read_text(encoding='utf-8')) if d['doc_id'] == 'doc:75/2023/NĐ-CP')
metadata = {'doc_id': document['doc_id'], 'valid_from': document['valid_from'], 'doc_number': document['doc_number'], 'doc_title': document['title'], 'doc_type': document['doc_type'], 'issued_date': document.get('issued_date'), 'verification_status': 'verified', 'content_kind': 'normative'}

body_source = next(s for s in sources if s['path'] == selection['body'])
body_blocks = extract_pdf_text(ROOT / body_source['path'], first_page=1, last_page=9)
result = parse_legal_document('', metadata, body_blocks)

for article in result['articles']:
    if 'khoản 5 Điều 14' in article['content']:
        path = '/'.join(article['structural_path'])
        print(f"{path} -> {article['content'][:200]}...")
