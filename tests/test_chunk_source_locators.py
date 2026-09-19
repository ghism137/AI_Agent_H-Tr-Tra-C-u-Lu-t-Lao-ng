from backend.ingestion.chunker_v2 import chunk_articles
from backend.ingestion.parser import parse_legal_document


def test_split_chunk_refs_only_its_source_lines():
    blocks = [
        {"kind": "paragraph", "text": "Điều 1. Phạm vi", "locator": "p:1"},
        {"kind": "paragraph", "text": "1. Nội dung khoản một đủ dài để tách chunk.", "locator": "p:2"},
        {"kind": "paragraph", "text": "2. Nội dung khoản hai đủ dài để tách chunk.", "locator": "p:3"},
    ]
    parsed = parse_legal_document("", {
        "doc_id": "doc:test", "doc_number": "1/2025/QH15", "doc_title": "Test",
        "doc_type": "luat", "issued_date": None, "valid_from": None,
    }, blocks)
    chunks = chunk_articles(parsed, release_id="test", source_id="src:test",
                            source_url=None, max_chars=65)
    assert len(chunks) == 3
    assert [ref["locator"] for ref in chunks[0]["source_refs"]] == ["p:1"]
    assert [ref["locator"] for ref in chunks[1]["source_refs"]] == ["p:2"]
    assert [ref["locator"] for ref in chunks[2]["source_refs"]] == ["p:3"]
