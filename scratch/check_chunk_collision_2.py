import json
from pathlib import Path
from backend.ingestion.docx_extractor import extract_docx
from backend.ingestion.parser import parse_legal_document
from backend.ingestion.chunker_v2 import chunk_articles

ROOT = Path('.')
selection = json.loads(Path('data/registry/source_selection.json').read_text(encoding='utf-8')).get('doc:145/2020/NĐ-CP')
sources = json.loads((ROOT / 'data' / 'registry' / 'sources.json').read_text(encoding='utf-8'))
document = next(d for d in json.loads((ROOT / 'data' / 'registry' / 'documents.json').read_text(encoding='utf-8')) if d['doc_id'] == 'doc:145/2020/NĐ-CP')
metadata = {'doc_id': document['doc_id'], 'valid_from': document['valid_from'], 'doc_number': document['doc_number'], 'doc_title': document['title'], 'doc_type': document['doc_type'], 'issued_date': document.get('issued_date'), 'verification_status': 'verified', 'content_kind': 'normative'}

body_source = next(s for s in sources if s['path'] == selection['body'])
body_blocks = extract_docx(ROOT / body_source['path'])
result = parse_legal_document('', metadata, body_blocks)

import collections
import hashlib
from backend.ingestion.chunker_v2 import _parts
output = []
chunk_count = collections.defaultdict(int)
for article in result['articles']:
    provision_id = f"doc:145/2020/NĐ-CP:{'/'.join(article['structural_path'])}"
    if provision_id == 'doc:145/2020/NĐ-CP:annex/item:3/item:1':
        print(f"FOUND ARTICLE! length {len(article['content'])}")
        for part in _parts(article, max_chars=4000):
            print(f"  part length: {len(part[0])}")
            index = chunk_count[provision_id]
            chunk_count[provision_id] += 1
            print(f"  assigned index: {index}")
            output.append({'index': index, 'content': part[0][:20]})
            
print('Output for this provision_id:', output)
