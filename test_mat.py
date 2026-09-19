import backend.ingestion.version_builder as vb
import json
with open('data/staging/phase1-candidate/parsed.json', 'r', encoding='utf-8') as f:
    parsed = json.load(f)
chunks = []
with open('data/staging/phase1-candidate/chunks.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        chunks.append(json.loads(line))
with open('data/registry/operations.json', 'r', encoding='utf-8') as f:
    operations = json.load(f)
versions = vb.base_versions(parsed, chunks)
try:
    res = vb.materialize_versions(versions, operations)
    print('Done materialize, len res:', len(res))
except Exception as e:
    import traceback
    traceback.print_exc()

