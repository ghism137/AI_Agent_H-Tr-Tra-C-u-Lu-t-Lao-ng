import json
import os
import pytest
import sys

# Thêm root path để import được backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.retrieval.graph_utils import is_valid, get_supplementary_docs
from backend.ingestion.extract_relations import _normalize_doc_number

def test_normalize_doc_number():
    """Kiểm tra hàm _normalize_doc_number"""
    assert _normalize_doc_number("145-2020-NĐ-CP") == "145/2020/NĐ-CP"
    assert _normalize_doc_number("45-2019-QH14") == "45/2019/QH14"
    assert _normalize_doc_number("06-2021-TT-BLĐTBXH") == "06/2021/TT-BLĐTBXH"

def test_chunks_jsonl_quality():
    """Kiểm tra file chunks.jsonl có tồn tại, không rỗng và đúng schema cơ bản"""
    chunks_path = 'data/chunks.jsonl'
    assert os.path.exists(chunks_path), "File chunks.jsonl không tồn tại"
    
    with open(chunks_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    assert len(lines) > 0, "File chunks.jsonl trống"
    
    # Check sample
    sample_chunk = json.loads(lines[0])
    assert 'chunk_id' in sample_chunk
    assert 'content' in sample_chunk
    assert 'doc_number' in sample_chunk

def test_document_relations_quality():
    """Kiểm tra schema của relations"""
    relations_path = 'data/document_relations.json'
    assert os.path.exists(relations_path), "File document_relations.json không tồn tại"
    
    with open(relations_path, 'r', encoding='utf-8') as f:
        relations = json.load(f)
        
    assert isinstance(relations, list)
    
    if len(relations) > 0:
        sample = relations[0]
        assert 'source_doc' in sample
        assert 'target_doc' in sample
        assert 'relation_type' in sample
        assert 'scope' in sample
        assert sample['relation_type'] in ['can_cu', 'huong_dan', 'sua_doi', 'bo_sung', 'thay_the', 'bai_bo']

def test_is_valid_logic():
    """Kiểm tra hàm lọc logic is_valid"""
    mock_relations = [
        {
            "source_doc": "145/2020/NĐ-CP",
            "target_doc": "45/2019/QH14",
            "relation_type": "sua_doi",
            "scope": "dieu_khoan_cu_the",
            "target_article": "Điều 36"
        },
        {
            "source_doc": "12/2022/NĐ-CP",
            "target_doc": "11/2013/NĐ-CP",
            "relation_type": "thay_the",
            "scope": "toan_bo",
            "target_article": None
        }
    ]
    
    # Điều 36 bị sửa đổi -> False
    assert is_valid("45/2019/QH14", "Điều 36", mock_relations) == False
    
    # Điều 37 không bị sửa đổi -> True
    assert is_valid("45/2019/QH14", "Điều 37", mock_relations) == True
    
    # Văn bản bị thay thế toàn bộ -> False
    assert is_valid("11/2013/NĐ-CP", "Điều 1", mock_relations) == False
    
    # Test effective_date trong tương lai (chưa có hiệu lực)
    mock_relations_future = [
        {
            "source_doc": "99/2026/NĐ-CP",
            "target_doc": "45/2019/QH14",
            "relation_type": "thay_the",
            "scope": "toan_bo",
            "effective_date": "2026-12-31"
        }
    ]
    # Ngày hiện tại giả lập là 2026-09-01, văn bản chưa bị thay thế
    assert is_valid("45/2019/QH14", "Điều 1", mock_relations_future, reference_date="2026-09-01") == True
    # Ngày hiện tại giả lập là 2027-01-01, văn bản đã bị thay thế
    assert is_valid("45/2019/QH14", "Điều 1", mock_relations_future, reference_date="2027-01-01") == False

def test_get_supplementary_docs():
    """Kiểm tra logic 1-hop expansion"""
    mock_relations = [
        {
            "source_doc": "145/2020/NĐ-CP",
            "target_doc": "45/2019/QH14",
            "relation_type": "huong_dan"
        },
        {
            "source_doc": "74/2024/NĐ-CP",
            "target_doc": "45/2019/QH14",
            "relation_type": "huong_dan"
        }
    ]
    
    supp_docs = get_supplementary_docs("45/2019/QH14", mock_relations)
    assert len(supp_docs) == 2
    assert "145/2020/NĐ-CP" in supp_docs
    assert "74/2024/NĐ-CP" in supp_docs
