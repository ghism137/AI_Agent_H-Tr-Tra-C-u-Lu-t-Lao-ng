import pytest
from backend.ingestion.chunker import split_article_by_clauses, extract_cross_references, chunk_document

def test_extract_cross_references():
    text = "Theo quy định tại Điều 34 và khoản 1 Điều 47 của luật này."
    refs = extract_cross_references(text)
    assert "Điều 34" in refs
    assert "Điều 47" in refs

def test_split_article_by_clauses():
    # Giả lập nội dung rất dài để trigger split (> 1000 chars per sub chunk inside the function)
    long_text = "A" * 1001
    article_text = f"Điều 46. Trợ cấp thôi việc\n1. Khoản 1\n{long_text}\n2. Khoản 2\n{long_text}"
    
    chunks = split_article_by_clauses(article_text)
    
    # Sẽ có 2 chunks vì mỗi khoản > 1000 chars
    assert len(chunks) == 2
    assert "1" in chunks[0]["clauses"]
    assert "2" in chunks[1]["clauses"]
    assert "Điều 46. Trợ cấp thôi việc" in chunks[0]["text"]
    assert "Điều 46. Trợ cấp thôi việc" in chunks[1]["text"]

def test_chunk_document():
    cleaned_json = {
        "metadata": {
            "doc_number": "45/2019/QH14",
            "doc_type": "luat"
        },
        "articles": [
            {
                "article_number": "1",
                "hierarchy_path": "Chương 1",
                "content": "Điều 1. Phạm vi\nNội dung ngắn."
            }
        ]
    }
    
    chunks = chunk_document(cleaned_json)
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk["chunk_id"] == "45-2019-QH14_D1"
    assert chunk["doc_number"] == "45/2019/QH14"
    assert chunk["chunk_length"] > 0
    assert chunk["hierarchy_path"] == "Chương 1"
