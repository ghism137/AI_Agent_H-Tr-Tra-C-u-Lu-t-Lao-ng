from backend.ingestion.version_builder import materialize_versions
import json

with open('data/registry/operations.json', 'r', encoding='utf-8') as f:
    ops = [o for o in json.load(f) if '146' in o.get('target_locator', '')]

base_versions = [
    {
        'doc_id': 'doc:146/2018/NĐ-CP',
        'structural_path': ['body', 'article:14', 'item:5', 'point:a'],
        'valid_from': '2018-12-01',
        'valid_to': None,
        'content': 'old content',
        'provision_id': 'doc:146/2018/NĐ-CP:body/article:14/item:5/point:a'
    }
]

try:
    versions = materialize_versions(base_versions, ops)
    for v in versions:
        print(f"{v['structural_path']} from {v['valid_from']} to {v['valid_to']}")
except Exception as e:
    print(f"Error: {e}")
