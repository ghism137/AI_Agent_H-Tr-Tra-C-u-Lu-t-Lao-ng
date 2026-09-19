import pytest
from backend.ingestion.parser import normalize_text, parse_legal_document
from backend.ingestion.docx_extractor import extract_docx
from pathlib import Path

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
    assert len(result["articles"]) == 4
    
    a1 = result["articles"][0]
    assert a1["article_number"] == "1"
    assert a1["hierarchy_path"] == "Phần I. QUY ĐỊNH CHUNG > Chương I. PHẠM VI ĐIỀU CHỈNH"
    assert "tiêu chuẩn lao động" in a1["content"]
    
    a2 = result["articles"][1]
    assert a2["article_number"] == "2"
    assert a2["structural_path"][-1] == "article:2"
    
    a2_1 = result["articles"][2]
    assert a2_1["article_number"] == "2"
    assert "1. Người lao động" in a2_1["content"]
    
    a2_2 = result["articles"][3]
    assert a2_2["article_number"] == "2"
    assert "2. Người sử dụng lao động" in a2_2["content"]


def test_docx_word_numbering_restores_atvsld_articles():
    source = Path(__file__).resolve().parents[1] / "data/raw/word/Luật-84-2015-QH13.docx"
    blocks = extract_docx(source)
    result = parse_legal_document("", {"doc_number": "84/2015/QH13"}, blocks)
    top_articles = [a for a in result["articles"] if len(a["structural_path"]) == 2 and a["structural_path"][-1].startswith("article:")]
    assert [article["article_number"] for article in top_articles[:3]] == ["1", "2", "3"]
    assert result["articles"][0].get("content_segments")


def test_annex_article_does_not_reuse_body_article_number():
    text = "Điều 1. Phạm vi\nNội dung.\nPHỤ LỤC I\nĐiều 1. Nội dung mẫu"
    result = parse_legal_document(text, {"doc_number": "145/2020/NĐ-CP"})
    assert len(result["articles"]) == 2
    assert result["articles"][0]["content_kind"] == "normative"
    assert result["articles"][1]["content_kind"] == "annex"
    assert result["articles"][1]["structural_path"] != result["articles"][0]["structural_path"]


def test_watermark_filter_preserves_legal_sentence():
    result = parse_legal_document("Điều 1. Test\n1. Tuân thủ pháp luật Việt Nam.", {"doc_number": "x"})
    assert "Tuân thủ pháp luật Việt Nam" in result["articles"][1]["content"]


def test_amendment_quoted_article_stays_inside_amending_article():
    text = "Điều 1. Sửa đổi luật\nBổ sung Điều 48b như sau:\nĐiều 48b. Trốn đóng\nNội dung sửa đổi.\nĐiều 2. Điều khoản thi hành"
    result = parse_legal_document(text, {"doc_number": "51/2024/QH15"})
    top_articles = [a for a in result["articles"] if len(a["structural_path"]) == 2 and a["structural_path"][-1].startswith("article:")]
    assert [article["article_number"] for article in top_articles] == ["1", "2"]
    assert "Điều 48b. Trốn đóng" in result["articles"][0]["content"]


def test_law_32_bare_article_number_is_parsed_without_matching_inline_citation():
    text = "Điều 1\nSửa đổi Luật Thuế thu nhập doanh nghiệp.\nĐiều 4 của Luật Bảo hiểm y tế được nhắc đến.\nĐiều 2\nLuật này có hiệu lực."
    articles = parse_legal_document(text, {"doc_number": "32/2013/QH13"})["articles"]
    top_articles = [a for a in articles if len(a["structural_path"]) == 2 and a["structural_path"][-1].startswith("article:")]
    assert [article["article_number"] for article in top_articles] == ["1", "2"]
    assert "Điều 4 của Luật Bảo hiểm y tế" in articles[0]["content"]


def test_numbered_annex_is_not_attached_to_final_normative_article():
    text = "Điều 1. Phạm vi\nNội dung.\nPHỤ LỤC SỐ 01\nDANH MỤC PHÍ, LỆ PHÍ\nPHỤ LỤC SỐ 02\nDANH MỤC CHUYỂN ĐỔI"
    articles = parse_legal_document(text, {"doc_number": "97/2015/QH13"})["articles"]
    assert [article["content_kind"] for article in articles] == ["normative", "annex", "annex"]
