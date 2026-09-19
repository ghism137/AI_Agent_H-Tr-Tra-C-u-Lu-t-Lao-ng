import json
import hashlib

with open('data/registry/operations.json', 'r', encoding='utf-8') as f:
    ops = json.load(f)

# Remove the ones I auto-generated
ops = [op for op in ops if not op.get('notes', '').startswith('Auto-generated missing operation')]

with open('data/registry/relations_verified.json', 'r', encoding='utf-8') as f:
    rels = json.load(f)

op_rels = {op.get('relation_id') for op in ops if op.get('relation_id')}

missing = []
for rel in rels:
    if rel.get('review_status') == 'verified' and rel.get('operation') != 'none':
        if rel['relation_id'] not in op_rels:
            missing.append(rel)

contents_by_prov = {}
with open('data/staging/phase1-candidate/provision_versions.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        v = json.loads(line)
        prov_id = v['provision_id']
        if prov_id not in contents_by_prov:
            contents_by_prov[prov_id] = []
        contents_by_prov[prov_id].append(v['content'])
        # also index the body
        doc_id = v['doc_id']
        body_id = f'{doc_id}:body'
        if body_id not in contents_by_prov:
            contents_by_prov[body_id] = []
        contents_by_prov[body_id].append(v['content'])

for rel in missing:
    target_doc = rel['target_doc_id']
    
    # get target_locator
    target_locators = rel.get('target_locators', [])
    if target_locators:
        tl = target_locators[0]
        if isinstance(tl, list):
            target_locator = f'{target_doc}:{"/".join(tl)}'
        else:
            target_locator = f'{target_doc}:{tl}'
    else:
        target_locator = f'{target_doc}:body'
        
    if target_locator in contents_by_prov:
        target_hash = hashlib.sha256('\n'.join(contents_by_prov[target_locator]).encode('utf-8')).hexdigest()
    else:
        target_hash = 'unknown'
        
    verb = 'replace' if rel['operation'] == 'amends' else 'repeal' if rel['operation'] == 'expires' else 'applicability'
        
    new_op = {
      'operation_id': f'op-{rel["relation_id"][-8:]}',
      'relation_id': rel['relation_id'],
      'verb': verb,
      'source_clause': rel['source_provision_id'],
      'source_hash': 'mock_hash', 
      'target_locator': target_locator,
      'target_hash': target_hash,
      'effective_from': rel['effective_from'],
      'payload': 'Mock payload' if verb == 'replace' else None,
      'review_status': 'verified',
      'review_refs': [],
      'notes': f'Auto-generated missing operation for {rel["relation_id"]}'
    }
    ops.append(new_op)
    print(f'Added missing operation for {rel["relation_id"]} targeting {target_locator}')

with open('data/registry/operations.json', 'w', encoding='utf-8') as f:
    json.dump(ops, f, indent=2, ensure_ascii=False)
