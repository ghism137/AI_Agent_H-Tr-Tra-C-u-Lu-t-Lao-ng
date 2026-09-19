"""Compare the two newly supplied DOCX files with Gazette PDF extraction."""

from __future__ import annotations

import difflib
import json
import re
from collections import Counter
from pathlib import Path

from backend.ingestion.docx_extractor import extract_docx
from backend.ingestion.parser import parse_legal_document
from backend.ingestion.pdf_text_extractor import extract_pdf_text


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/phase1-closeout/new_docx_comparison.json"


def parsed(path: str, number: str, kind: str, first: int | None = None, last: int | None = None):
    full = ROOT / path
    blocks = extract_docx(full) if full.suffix == ".docx" else extract_pdf_text(full, first_page=first, last_page=last)
    return parse_legal_document("", {"doc_id": f"doc:{number}", "doc_number": number,
                                     "doc_title": number, "doc_type": "nghi_dinh", "content_kind": kind}, blocks)["articles"]


def ratio(left: str, right: str) -> float:
    normalize = lambda value: re.sub(r"\s+", "", value).casefold()
    return round(difflib.SequenceMatcher(None, normalize(left), normalize(right)).ratio(), 4)


def containment(left: str, right: str) -> float:
    tokens = lambda value: re.findall(r"\w+", value.casefold(), flags=re.UNICODE)
    a, b = Counter(tokens(left)), Counter(tokens(right))
    return round(sum((a & b).values()) / sum(a.values()), 4) if a else 0.0


def main() -> None:
    word219 = parsed("data/raw/word/2025_1073 + 1074_219-2025-NĐ-CP.docx", "219/2025/NĐ-CP", "normative")
    pdf219 = parsed("data/raw/official/219-2025-ND-CP-congbao.pdf", "219/2025/NĐ-CP", "normative", 2, 37)
    a = {row["article_number"]: row["content"] for row in word219 if row["content_kind"] == "normative"}
    b = {row["article_number"]: row["content"] for row in pdf219 if row["content_kind"] == "normative"}
    articles = [{"article": number, "similarity": ratio(a[number], b[number])}
                for number in sorted(a, key=int) if number in b]
    word188 = parsed("data/raw/word/2025_979 + 980_188-2025-NĐ-CP.docx", "188/2025/NĐ-CP", "form")
    pdf188 = parsed("data/raw/official/188-2025-ND-CP-congbao-part2.pdf", "188/2025/NĐ-CP", "form", 3, 20)
    form_number = lambda row: re.match(r"Mẫu số\s+(\d+)", row["content"], flags=re.I)
    c = {form_number(row)[1]: row["content"] for row in word188 if row["content_kind"] == "form" and form_number(row)}
    d = {form_number(row)[1]: row["content"] for row in pdf188 if row["content_kind"] == "form" and form_number(row)}
    forms = [{"form": number, "similarity": ratio(c[number], d[number]),
              "docx_token_containment_in_pdf": containment(c[number], d[number]),
              "docx_length": len(c[number]), "pdf_extraction_length": len(d[number])}
             for number in sorted(c, key=int) if number in d]
    report = {"status": "automated_comparison_only", "not_legal_signoff": True,
              "decree_219": {"docx_normative_articles": len(a), "pdf_normative_articles": len(b),
                             "docx_forms": sum(row["content_kind"] == "form" for row in word219),
                             "article_comparison": articles},
              "decree_188_continuation": {"docx_forms": sorted(c, key=int), "pdf_forms": sorted(d, key=int),
                                           "pdf_page_interval": [3, 20],
                                           "form_comparison": forms}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"articles": len(articles), "min_article_similarity": min(row["similarity"] for row in articles),
                      "forms": len(forms), "min_form_similarity": min(row["similarity"] for row in forms)}))


if __name__ == "__main__":
    main()
