import json

with open('data/registry/operations.json', 'r', encoding='utf-8') as f:
    ops = json.load(f)

with open('data/registry/relations_verified.json', 'r', encoding='utf-8') as f:
    rels = json.load(f)

rel_map = {r['relation_id']: r for r in rels}

for op in ops:
    rel_id = op.get('relation_id')
    loc = op.get('target_locator', '')
    if loc == 'body' or (not loc.startswith('doc:') and loc != ''):
        if rel_id and rel_id in rel_map:
            target_doc = rel_map[rel_id]['target_doc_id']
            op['target_locator'] = f"{target_doc}:{loc}" if loc else target_doc

with open('data/registry/operations.json', 'w', encoding='utf-8') as f:
    json.dump(ops, f, ensure_ascii=False, indent=2)

print('Fixed target_locators in operations.json')
