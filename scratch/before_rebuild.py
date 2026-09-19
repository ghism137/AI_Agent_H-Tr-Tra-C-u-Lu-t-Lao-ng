"""Capture before-rebuild corpus state for Q3 reconciliation."""
import json
from pathlib import Path

STAGE = Path("data/staging/phase1-candidate")

print("=== BEFORE REBUILD ===")
manifest = json.loads((STAGE / "manifest.json").read_text("utf-8"))
print(f"release_id: {manifest['release_id']}")
print(f"documents_parsed: {manifest['documents_parsed']}")
print(f"chunks: {manifest['chunks']}")
print(f"provision_versions: {manifest['provision_versions']}")
print(f"quarantined_documents: {manifest['quarantined_documents']}")
print(f"gate1: {manifest['gate1']}, gate2: {manifest['gate2']}, gate3: {manifest['gate3']}")
print(f"sources_sha256: {manifest['sources_sha256'][:16]}...")
print(f"parser_code_sha256: {manifest['parser_code_sha256'][:16]}...")
print(f"verified_relations_sha256: {manifest['verified_relations_sha256'][:16]}...")
print(f"operations_sha256: {manifest.get('operations_sha256', 'ABSENT')}")

with open(STAGE / "chunks.jsonl", encoding="utf-8") as f:
    chunk_lines = f.readlines()
print(f"chunks.jsonl lines: {len(chunk_lines)}")

with open(STAGE / "provision_versions.jsonl", encoding="utf-8") as f:
    version_lines = f.readlines()
print(f"provision_versions.jsonl lines: {len(version_lines)}")

quarantine = json.loads((STAGE / "quarantine.json").read_text("utf-8"))
print(f"quarantine items: {len(quarantine)}")

# Check if any versions reference operations (materialized from stubs)
versions = [json.loads(l) for l in version_lines if l.strip()]
materialized_from_ops = [v for v in versions if v.get("applied_relation_ids")]
print(f"versions with applied_relation_ids: {len(materialized_from_ops)}")
