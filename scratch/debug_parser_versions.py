"""Debug parser and chunker behavior for base_provision_versions test."""
from backend.ingestion.parser import parse_legal_document
from backend.ingestion.chunker_v2 import chunk_articles
from backend.ingestion.version_builder import base_versions

parsed = parse_legal_document(
    "Điều 1. Phạm vi\n1. Nội dung thứ nhất.\n2. Nội dung thứ hai.",
    {"doc_id": "doc:example", "doc_number": "example", "doc_title": "Example",
     "doc_type": "luat", "valid_from": "2025-01-01"},
)
print("Articles from parser:")
for a in parsed["articles"]:
    print(f"  path={a['structural_path']}")
    print(f"  content={a['content'][:80]!r}")
    print()

chunks = chunk_articles(parsed, release_id="candidate-test", source_id="src:example",
                        source_url=None, max_chars=55)
print("Chunks:")
for c in chunks:
    print(f"  provision_version_id={c['provision_version_id']}")
    print(f"  content={c['content'][:80]!r}")
    print()

versions = base_versions({"doc:example": parsed}, chunks)
print(f"Versions count: {len(versions)}")
for v in versions:
    print(f"  provision_id={v['provision_id']}")
    print(f"  verification_status={v['verification_status']}")
    print(f"  valid_from={v['valid_from']}")
