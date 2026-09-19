import json
with open('data/registry/relations_verified.json', encoding='utf-8') as f:
    rels = json.load(f)
for r in rels:
    if r.get('review_status') == 'verified' and r.get('operation') != 'none':
        print(f"{r['relation_id']} - {r['operation']}")
