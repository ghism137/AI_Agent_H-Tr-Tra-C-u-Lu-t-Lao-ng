"""write_test_file.py — writes test file with correct Vietnamese text."""
from pathlib import Path

content = (
    "from backend.ingestion.chunker_v2 import chunk_articles\n"
    "from backend.ingestion.parser import parse_legal_document\n"
    "from backend.ingestion.version_builder import base_versions\n"
    "\n"
    "\n"
    "def test_base_version_keeps_full_parent_and_pending_validity():\n"
    '    """Schema v2: each provision (article + items) becomes a separate version.\n'
    "    Input with 2 items produces 3 versions: article:1, item:1, item:2.\n"
    "    All must be pending (no verified evidence yet) and have valid_from=None.\n"
    '    """\n'
    "    parsed = parse_legal_document(\n"
    '        "\\u0110i\\u1ec1u 1. Ph\\u1ea1m vi\\n1. N\\u1ed9i dung th\\u1ee9 nh\\u1ea5t.\\n2. N\\u1ed9i dung th\\u1ee9 hai.",\n'
    '        {"doc_id": "doc:example", "doc_number": "example", "doc_title": "Example",\n'
    '         "doc_type": "luat", "valid_from": "2025-01-01"},\n'
    "    )\n"
    '    chunks = chunk_articles(parsed, release_id="candidate-test", source_id="src:example",\n'
    "                            source_url=None, max_chars=55)\n"
    '    versions = base_versions({"doc:example": parsed}, chunks)\n'
    "\n"
    "    # Schema v2: article:1 + article:1/item:1 + article:1/item:2 = 3 provisions\n"
    "    assert len(versions) == 3\n"
    "\n"
    "    # All chunks must map to one of the versions\n"
    '    version_ids = {v["provision_version_id"] for v in versions}\n'
    '    assert {chunk["provision_version_id"] for chunk in chunks} == version_ids\n'
    "\n"
    "    # All versions must be pending with no verified dates\n"
    "    for v in versions:\n"
    '        assert v["verification_status"] == "pending"\n'
    '        assert v["valid_from"] is None\n'
    '        assert v["source_refs"]\n'
    "\n"
    "    # Provision IDs must cover the expected structural paths\n"
    '    provision_ids = {v["provision_id"] for v in versions}\n'
    '    assert "doc:example:body/article:1" in provision_ids\n'
    '    assert "doc:example:body/article:1/item:1" in provision_ids\n'
    '    assert "doc:example:body/article:1/item:2" in provision_ids\n'
    "\n"
    "\n"
    "def test_materialization_handles_overlapping_validity_and_future_dates():\n"
    "    from backend.ingestion.version_builder import materialize_versions\n"
    "    # Mock base versions - must include doc_id for matching\n"
    '    # No source_hash/target_hash keys = provenance guard not triggered (absent != "unknown")\n'
    "    input_versions = [\n"
    "        {\n"
    '            "doc_id": "doc:1",\n'
    '            "provision_id": "doc:1:body/article:1",\n'
    '            "provision_version_id": "doc:1:body/article:1@abc123",\n'
    '            "structural_path": ["body", "article:1"],\n'
    '            "valid_from": "2015-01-01",\n'
    '            "valid_to": None,\n'
    '            "content": "Original",\n'
    '            "applied_relation_ids": [],\n'
    "        }\n"
    "    ]\n"
    "    # Operations without source_hash field = no provenance guard triggered\n"
    "    operations = [\n"
    "        {\n"
    '            "operation_id": "op-replace-1",\n'
    '            "target_locator": "doc:1:body/article:1",\n'
    '            "verb": "replace",\n'
    '            "effective_from": "2025-01-01",\n'
    '            "review_status": "verified",\n'
    '            "payload": "Amended text",\n'
    "        },\n"
    "        {\n"
    '            "operation_id": "op-repeal-1",\n'
    '            "target_locator": "doc:1:body/article:1",\n'
    '            "verb": "repeal",\n'
    '            "effective_from": "2025-08-15",\n'
    '            "review_status": "verified",\n'
    "        },\n"
    "    ]\n"
    "    materialized = materialize_versions(input_versions, operations)\n"
    "\n"
    "    # Original version must have valid_to set to the replace date\n"
    '    originals = [v for v in materialized if v.get("content") == "Original"]\n'
    "    assert len(originals) >= 1\n"
    '    assert originals[0]["valid_to"] == "2025-01-01"\n'
    "\n"
    "    # Amended version must exist\n"
    '    amended = [v for v in materialized if v.get("content") == "Amended text"]\n'
    "    assert len(amended) >= 1\n"
    "\n"
    "    # Result must have more than just the original (at least original + amended)\n"
    "    assert len(materialized) >= 2\n"
)

out = Path("tests/test_base_provision_versions.py")
out.write_text(content, encoding="utf-8")
print(f"Written {len(content)} chars to {out}")
# Verify it reads back correctly
roundtrip = out.read_text("utf-8")
assert roundtrip == content
print("Roundtrip OK")
