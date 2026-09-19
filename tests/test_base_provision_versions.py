from backend.ingestion.chunker_v2 import chunk_articles
from backend.ingestion.parser import parse_legal_document
from backend.ingestion.version_builder import base_versions


def test_base_version_keeps_full_parent_and_pending_validity():
    """Schema v2: each provision (article + items) becomes a separate version.
    Input with 2 items produces 3 versions: article:1, item:1, item:2.
    All must be pending (no verified evidence yet) and have valid_from=None.
    """
    parsed = parse_legal_document(
        "\u0110i\u1ec1u 1. Ph\u1ea1m vi\n1. N\u1ed9i dung th\u1ee9 nh\u1ea5t.\n2. N\u1ed9i dung th\u1ee9 hai.",
        {"doc_id": "doc:example", "doc_number": "example", "doc_title": "Example",
         "doc_type": "luat", "valid_from": "2025-01-01"},
    )
    chunks = chunk_articles(parsed, release_id="candidate-test", source_id="src:example",
                            source_url=None, max_chars=55)
    versions = base_versions({"doc:example": parsed}, chunks)

    # Schema v2: article:1 + article:1/item:1 + article:1/item:2 = 3 provisions
    assert len(versions) == 3

    # All chunks must map to one of the versions
    version_ids = {v["provision_version_id"] for v in versions}
    assert {chunk["provision_version_id"] for chunk in chunks} == version_ids

    # All versions must be pending with no verified dates
    for v in versions:
        assert v["verification_status"] == "pending"
        assert v["valid_from"] is None
        assert v["source_refs"]

    # Provision IDs must cover the expected structural paths
    provision_ids = {v["provision_id"] for v in versions}
    assert "doc:example:body/article:1" in provision_ids
    assert "doc:example:body/article:1/item:1" in provision_ids
    assert "doc:example:body/article:1/item:2" in provision_ids


def test_materialization_handles_overlapping_validity_and_future_dates():
    from backend.ingestion.version_builder import materialize_versions
    # Mock base versions - must include doc_id for matching
    # No source_hash/target_hash keys = provenance guard not triggered (absent != "unknown")
    input_versions = [
        {
            "doc_id": "doc:1",
            "provision_id": "doc:1:body/article:1",
            "provision_version_id": "doc:1:body/article:1@abc123",
            "structural_path": ["body", "article:1"],
            "valid_from": "2015-01-01",
            "valid_to": None,
            "content": "Original",
            "applied_relation_ids": [],
        }
    ]
    # Operations without source_hash field = no provenance guard triggered
    operations = [
        {
            "operation_id": "op-replace-1",
            "target_locator": "doc:1:body/article:1",
            "verb": "replace",
            "effective_from": "2025-01-01",
            "review_status": "verified",
            "payload": "Amended text",
        },
        {
            "operation_id": "op-repeal-1",
            "target_locator": "doc:1:body/article:1",
            "verb": "repeal",
            "effective_from": "2025-08-15",
            "review_status": "verified",
        },
    ]
    materialized = materialize_versions(input_versions, operations)

    # Original version must have valid_to set to the replace date
    originals = [v for v in materialized if v.get("content") == "Original"]
    assert len(originals) >= 1
    assert originals[0]["valid_to"] == "2025-01-01"

    # Amended version must exist
    amended = [v for v in materialized if v.get("content") == "Amended text"]
    assert len(amended) >= 1

    # Result must have more than just the original (at least original + amended)
    assert len(materialized) >= 2
