import codecs
import re
import os

filepath = 'scripts/build_phase1_stage.py'
with codecs.open(filepath, 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('from backend.ingestion.version_builder import base_versions',
                          'from backend.ingestion.version_builder import base_versions, materialize_versions')

content = re.sub(r'def apply_temporal_relations.*?return versions\n\n\n', '', content, flags=re.DOTALL)
content = re.sub(r'def apply_temporal_relations.*?return versions\n', '', content, flags=re.DOTALL)

new_logic = '''
    operations_path = REGISTRY / "operations.json"
    operations = []
    gate3 = "PASS"
    if operations_path.exists():
        operations = json.loads(operations_path.read_text(encoding="utf-8"))
        for op in operations:
            if op.get("review_status") != "verified":
                gate3 = "FAIL"
                break
                
    try:
        versions = materialize_versions(versions, operations)
    except Exception as e:
        print(f"Materialization failed: {e}")
        gate3 = "FAIL"
        raise
    
    missing = [item["doc_number"] for item in coverage if f"doc:{item['doc_number']}" not in parsed]
    gate1 = "PASS" if len(quarantine) == 0 and len(missing) == 0 else "FAIL"
    gate2 = "FAIL"
    legal_verification_path = REGISTRY / "legal_verification.json"
    if legal_verification_path.exists():
        try:
            legal_data = json.loads(legal_verification_path.read_text(encoding="utf-8"))
            if legal_data.get("status") == "PASS":
                gate2 = "PASS"
        except Exception:
            pass
'''

content = re.sub(r'versions = apply_temporal_relations\(versions, REGISTRY / "relations_verified\.json"\)\n.*?gate3 = "PASS" # simplified temporal gate for now', new_logic, content, flags=re.DOTALL)

with codecs.open(filepath, 'w', 'utf-8') as f:
    f.write(content)
print('Updated build_phase1_stage.py')
