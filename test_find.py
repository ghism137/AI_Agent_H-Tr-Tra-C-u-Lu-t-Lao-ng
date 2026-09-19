import backend.ingestion.version_builder as vb
import json
with open('data/staging/phase1-candidate/parsed.json', 'r', encoding='utf-8') as f:
    parsed = json.load(f)
chunks = []
with open('data/staging/phase1-candidate/chunks.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunks.append(json.loads(line))
versions = vb.base_versions(parsed, chunks)
source_clause = 'doc:02/2025/NĐ-CP:body/article:1/item:1'
svs = [sv for sv in versions if sv['doc_id'] + ':' + '/'.join(sv['structural_path']) == source_clause]
print('Found:', len(svs))
if svs:
    print(svs[0].keys())

