import pytest
from backend.ingestion.parser import normalize_text, parse_legal_document

def test_normalize_text():
    assert normalize_text("  Khoảng   trắng  \n \t thừa  ") == "Khoảng trắng thừa"
    assert normalize_text("") == ""

def test_parse_legal_document():
    md_mock = """Phần I. QUY ĐỊNH CHUNG
Chương I. PHẠM VI ĐIỀU CHỈNH
Điều 1. Phạm vi điều chỉnh
Bộ luật Lao động quy định tiêu chuẩn lao động.
Điều 2. Đối tượng áp dụng
1. Người lao động.
2. Người sử dụng lao động."""
    
    doc_meta = {"doc_number": "45/2019/QH14"}
    result = parse_legal_document(md_mock, doc_meta)
    
    assert "metadata" in result
    assert result["metadata"]["doc_number"] == "45/2019/QH14"
    assert len(result["articles"]) == 2
    
    a1 = result["articles"][0]
    assert a1["article_number"] == "1"
    assert a1["hierarchy_path"] == "Phần I. QUY ĐỊNH CHUNG > Chương I. PHẠM VI ĐIỀU CHỈNH"
    assert "tiêu chuẩn lao động" in a1["content"]
    
    a2 = result["articles"][1]
    assert a2["article_number"] == "2"
    assert "1. Người lao động" in a2["content"]
    assert "2. Người sử dụng lao động" in a2["content"]
