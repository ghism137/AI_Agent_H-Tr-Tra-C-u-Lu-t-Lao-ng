import json
with open('data/registry/operations.json', encoding='utf-8') as f:
    ops = json.load(f)
    for op in ops:
        if '146' in op.get('target_locator', '') and '75' in op.get('source_clause', ''):
            print(f"{op['operation_id']} -> {op['target_locator']} from {op.get('source_clause')}")
