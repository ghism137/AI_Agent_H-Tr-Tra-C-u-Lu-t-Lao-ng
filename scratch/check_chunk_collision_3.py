import json
from pathlib import Path
from backend.ingestion.docx_extractor import extract_docx
from backend.ingestion.parser import parse_legal_document

ROOT = Path('.')
selection = json.loads(Path('data/registry/source_selection.json').read_text(encoding='utf-8')).get('doc:145/2020/NĐ-CP')
sources = json.loads((ROOT / 'data' / 'registry' / 'sources.json').read_text(encoding='utf-8'))
document = next(d for d in json.loads((ROOT / 'data' / 'registry' / 'documents.json').read_text(encoding='utf-8')) if d['doc_id'] == 'doc:145/2020/NĐ-CP')
metadata = {'doc_id': document['doc_id'], 'valid_from': document['valid_from'], 'doc_number': document['doc_number'], 'doc_title': document['title'], 'doc_type': document['doc_type'], 'issued_date': document.get('issued_date'), 'verification_status': 'verified', 'content_kind': 'normative'}

body_source = next(s for s in sources if s['path'] == selection['body'])
body_blocks = extract_docx(ROOT / body_source['path'])
result = parse_legal_document('', metadata, body_blocks)

import uuid
NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, 'urn:luat:vn')

import collections
import hashlib
from backend.ingestion.chunker_v2 import _parts
output = []
chunk_count = collections.defaultdict(int)
for article in result['articles']:
    provision_id = f"doc:145/2020/NĐ-CP:{'/'.join(article['structural_path'])}"
    full_hash = hashlib.sha256(article['content'].encode('utf-8')).hexdigest()
    version_id = f"{provision_id}@{full_hash[:16]}"
    
    for part in _parts(article, 4000):
        digest = hashlib.sha256(part[0].encode('utf-8')).hexdigest()
        index = chunk_count[provision_id]
        chunk_count[provision_id] += 1
        chunk_id = str(uuid.uuid5(NAMESPACE, f"{version_id}:{index}:{digest}"))
        output.append({'chunk_id': chunk_id, 'provision_id': provision_id, 'index': index, 'content': part[0], 'version_id': version_id, 'digest': digest})

counts = collections.Counter(r['chunk_id'] for r in output)
for cid, cnt in counts.items():
    if cnt > 1:
        print(f"Collision! {cid}")
        for r in output:
            if r['chunk_id'] == cid:
                print(f"  prov: {r['provision_id']}, idx: {r['index']}, version: {r['version_id']}, digest: {r['digest']}")
