import json
with open('data/registry/operations.json', encoding='utf-8') as f:
    ops = json.load(f)
for op in ops:
    if op.get('source_clause', '').startswith('doc:02/2025/NĐ-CP') and '146' in op.get('target_locator', ''):
        print(f"{op['operation_id']} -> {op['target_locator']} from {op.get('source_clause')}")
