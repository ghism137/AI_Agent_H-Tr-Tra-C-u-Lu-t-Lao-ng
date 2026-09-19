from pathlib import Path

from backend.ingestion.pdf_text_extractor import extract_pdf_text


ROOT = Path(__file__).resolve().parents[1]


def test_congbao_page_headers_do_not_enter_legal_text():
    cases = (
        ("188-2025-ND-CP-congbao-part1.pdf", 83),
        ("219-2025-ND-CP-congbao.pdf", 27),
    )
    for filename, page in cases:
        blocks = extract_pdf_text(ROOT / "data/raw/official" / filename,
                                  first_page=page, last_page=page)
        assert blocks
        assert all("CÔNG BÁO/Số" not in block["text"] for block in blocks)
        assert any("Phụ lục" in block["text"] for block in blocks)
        if filename.startswith("188-"):
            assert all(block["text"] != "84" for block in blocks)
