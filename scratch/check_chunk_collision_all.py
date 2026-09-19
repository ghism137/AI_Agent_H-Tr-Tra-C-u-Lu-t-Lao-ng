import json
from pathlib import Path
from backend.ingestion.docx_extractor import extract_docx
from backend.ingestion.parser import parse_legal_document
from backend.ingestion.chunker_v2 import chunk_articles, _parts
import uuid
import hashlib
import collections

ROOT = Path('.')
selection = json.loads(Path('data/registry/source_selection.json').read_text(encoding='utf-8')).get('doc:145/2020/NĐ-CP')
sources = json.loads((ROOT / 'data' / 'registry' / 'sources.json').read_text(encoding='utf-8'))
document = next(d for d in json.loads((ROOT / 'data' / 'registry' / 'documents.json').read_text(encoding='utf-8')) if d['doc_id'] == 'doc:145/2020/NĐ-CP')
metadata = {'doc_id': document['doc_id'], 'valid_from': document['valid_from'], 'doc_number': document['doc_number'], 'doc_title': document['title'], 'doc_type': document['doc_type'], 'issued_date': document.get('issued_date'), 'verification_status': 'verified', 'content_kind': 'normative'}

variants = [s for s in sources if s['source_id'] in document['source_ids'] and s['format'] == 'docx']
supplemental = [item for item in variants if item['path'] != selection['body'] and item['path'].rsplit('/', 1)[-1].lower().startswith(('mau ', 'phu '))]

body_source = next(s for s in sources if s['path'] == selection['body'])
body_blocks = extract_docx(ROOT / body_source['path'])
result = parse_legal_document('', metadata, body_blocks)

output = []
chunk_count = collections.defaultdict(int)

NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, 'urn:luat:vn')

def process_articles(articles):
    for article in articles:
        provision_id = f"doc:145/2020/NĐ-CP:{'/'.join(article['structural_path'])}"
        full_hash = hashlib.sha256(article['content'].encode('utf-8')).hexdigest()
        version_id = f"{provision_id}@{full_hash[:16]}"
        
        for part in _parts(article, 4000):
            digest = hashlib.sha256(part[0].encode('utf-8')).hexdigest()
            index = chunk_count[provision_id]
            chunk_count[provision_id] += 1
            chunk_id = str(uuid.uuid5(NAMESPACE, f"{version_id}:{index}:{digest}"))
            
            output.append({'chunk_id': chunk_id, 'provision_id': provision_id, 'index': index, 'content': part[0]})

process_articles(result['articles'])

for artifact in sorted(supplemental, key=lambda item: item["path"]):
    artifact_kind = "form" if artifact["path"].rsplit("/", 1)[-1].lower().startswith("mau ") else "annex"
    artifact_meta = {**metadata, "content_kind": artifact_kind}
    artifact_parsed = parse_legal_document("", artifact_meta, extract_docx(ROOT / artifact["path"]))
    for part_number, article in enumerate(artifact_parsed["articles"], 1):
        article["structural_path"] = [artifact_kind, artifact["source_id"], f"item:{part_number}"]
    
    # Notice we reset chunk_count for each chunk_articles call in reality! 
    # Because chunk_articles is called independently!
    # WAIT! chunk_articles creates a NEW chunk_count dict each time!
    # So if there are two articles with the same structural_path in different calls?
    # NO! structural_path includes artifact["source_id"] which is unique for each artifact!
    # Let's simulate what chunk_articles does exactly:
    local_chunk_count = collections.defaultdict(int)
    for article in artifact_parsed["articles"]:
        provision_id = f"doc:145/2020/NĐ-CP:{'/'.join(article['structural_path'])}"
        full_hash = hashlib.sha256(article['content'].encode('utf-8')).hexdigest()
        version_id = f"{provision_id}@{full_hash[:16]}"
        
        for part in _parts(article, 4000):
            digest = hashlib.sha256(part[0].encode('utf-8')).hexdigest()
            index = local_chunk_count[provision_id]
            local_chunk_count[provision_id] += 1
            chunk_id = str(uuid.uuid5(NAMESPACE, f"{version_id}:{index}:{digest}"))
            
            output.append({'chunk_id': chunk_id, 'provision_id': provision_id, 'index': index, 'content': part[0]})

cids = collections.defaultdict(list)
for c in output:
    cids[c['chunk_id']].append(c)

for cid, cs in cids.items():
    if len(cs) > 1:
        print(f"Collision! {cid}")
        for c in cs:
            print("  prov:", c['provision_id'], "idx:", c['index'])
            print("  content:", c['content'][:100])
