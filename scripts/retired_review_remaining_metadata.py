"""Write individually evidenced metadata decisions for the 22 baseline documents.

These decisions cover identity, title and general effective date only. They do
not verify legal currency, amendments, provision content or topic coverage.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from backend.ingestion.docx_extractor import extract_docx
from scripts.review_decisions import ReviewDecision, input_hash


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/registry"
OUT = REGISTRY / "reviews"


# Each URL is an official government or national VBPL page inspected on 2026-09-17.
# Dates are transcribed from its attributes and checked against the local document.
FACTS = {
    "06/2021/TT-BLĐTBXH": ("2021-07-07", "2021-09-01", "https://vbpl.vn/TW/Pages/vbpq-thuoctinh.aspx?ItemID=151294", "Expired 2025-07-01; amendment to TT 59/2015."),
    "09/2020/TT-BLĐTBXH": ("2020-11-12", "2021-03-15", "https://vbpl.vn/TW/Pages/vbpq-thuoctinh.aspx?ItemID=152670", "Partially expired; chain review pending."),
    "10/2012/QH13": ("2012-06-18", "2013-05-01", "https://vbpl.vn/bolaodong/Pages/ivbpq-thuoctinh.aspx?ItemID=27615", "Expired 2021-01-01; retain historical provisions."),
    "10/2020/TT-BLĐTBXH": ("2020-11-12", "2021-01-01", "https://vbpl.vn/tw/Pages/vbpq-thuoctinh.aspx?ItemID=146696", "Amendment chain and appendices pending."),
    "11/2020/TT-BLĐTBXH": ("2020-11-12", "2021-03-01", "https://vbpl.vn/TW/Pages/ivbpq-lichsu.aspx?ItemID=146697", "Occupation list appendices need fidelity review."),
    "11/2022/TT-BLĐTBXH": ("2022-06-30", "2022-08-15", "https://vbpl.vn/TW/Pages/ivbpq-thuoctinh.aspx?ItemID=159189", "VBPL reports partial expiry; cited NĐ 09/2025 needs chain review."),
    "115/2015/NĐ-CP": ("2015-11-11", "2016-01-01", "https://vbpl.vn/botuphap/Pages/vbpq-thuoctinh.aspx?ItemID=94953", "Point b clause 1 Article 2 took effect 2018-01-01; general date must not propagate to that provision. Expired 2025-07-01."),
    "12/2012/QH13": ("2012-06-20", "2013-01-01", "https://vbpl.vn/TW/Pages/vbpq-thuoctinh.aspx?ItemID=27625", "Replaced by Law 50/2024 effective 2025-07-01; historical only thereafter."),
    "12/2022/NĐ-CP": ("2022-01-17", "2022-01-17", "https://vanban.chinhphu.vn/?docid=205182&lang=vi&pageid=27160", "Official government page and signed Article 75 give 2022-01-17."),
    "135/2020/NĐ-CP": ("2020-11-18", "2021-01-01", "https://vbpl.vn/hanoi/Pages/vbpq-thuoctinh.aspx?ItemID=152734", "VBPL reports partial expiry due to NĐ 158/2025; scope review pending."),
    "143/2018/NĐ-CP": ("2018-10-15", "2018-12-01", "https://vbpl.vn/boyte/Pages/vbpq-thuoctinh.aspx?ItemID=131592", "Expired 2025-07-01; applicability to foreign workers is specific."),
    "152/2020/NĐ-CP": ("2020-12-30", "2021-02-15", "https://vbpl.vn/TW/Pages/vbpq-thuoctinh.aspx?ItemID=152669", "Partial expiry and amendments by NĐ 70/2023, 128/2025 and 219/2025 require provision review."),
    "191/2013/NĐ-CP": ("2013-11-21", "2014-01-10", "https://vbpl.vn/hanoi/Pages/ivbpq-thuoctinh.aspx?ItemID=32634", "VBPL current-status claim is not a complete amendment-chain review."),
    "23/2021/QĐ-TTg": ("2021-07-07", "2021-07-07", "https://vanban.chinhphu.vn/default.aspx?docid=203559&pageid=27160", "Conflict: Công báo listing says 2021-07-01, while government attributes and local Article 46 say effective from signing on 2021-07-07. Separate program eligibility dates need review."),
    "28/2015/NĐ-CP": ("2015-03-12", "2015-05-01", "https://vbpl.vn/TW/Pages/vbpq-thuoctinh.aspx?ItemID=55726", "Modified by NĐ 61/2020, expired 2026-01-01 under NĐ 374/2025; chain pending."),
    "28/2015/TT-BLĐTBXH": ("2015-07-31", "2015-09-15", "https://vbpl.vn/TW/Pages/vbpq-thuoctinh.aspx?ItemID=95800", "Article 28 applies regimes from 2015-01-01, earlier than general effective date; amended by TT 15/2023."),
    "39/2016/NĐ-CP": ("2016-05-15", "2016-07-01", "https://vbpl.vn/bokehoachvadautu/Pages/ivbpq-thuoctinh.aspx?ItemID=105821", "Occupational-safety chain review pending."),
    "43/2013/NĐ-CP": ("2013-05-10", "2013-07-01", "https://vbpl.vn/tw/Pages/vbpq-thuoctinh.aspx?ItemID=32525", "Guides older union law; effect of replacement Law 50/2024 requires review."),
    "59/2015/TT-BLĐTBXH": ("2015-12-29", "2016-02-15", "https://vbpl.vn/TW/Pages/vbpq-thuoctinh.aspx?ItemID=97369", "Some provisions apply from 2016-01-01 and 1–3 month contracts from 2018-01-01; replaced by TT 12/2025 effective 2025-07-01."),
    "70/2023/NĐ-CP": ("2023-09-18", "2023-09-18", "https://vbpl.vn/TW/Pages/vbpq-thuoctinh.aspx?ItemID=162330", "Amends NĐ 152/2020; later NĐ 219/2025 impact pending."),
    "84/2015/QH13": ("2015-06-25", "2016-07-01", "https://vbpl.vn/TW/Pages/vbpq-thuoctinh.aspx?ItemID=70811", "VBPL reports partial expiry; amendment-chain review pending."),
    "88/2020/NĐ-CP": ("2020-07-28", "2020-09-15", "https://vbpl.vn/botuphap/Pages/vbpq-thuoctinh.aspx?ItemID=143470", "VBPL reports partial expiry and consolidation; chain review pending."),
}

TITLES = {
    "10/2012/QH13": "Bộ luật Lao động",
    "12/2012/QH13": "Luật Công đoàn",
    "84/2015/QH13": "Luật An toàn, vệ sinh lao động",
}


def local_title(path: Path, number: str) -> str:
    if number in TITLES:
        return TITLES[number]
    paragraphs = [block["text"].strip() for block in extract_docx(path)
                  if block["kind"] == "paragraph" and block["text"].strip()]
    marker = next(index for index, line in enumerate(paragraphs)
                  if line.upper() in {"NGHỊ ĐỊNH", "THÔNG TƯ", "QUYẾT ĐỊNH"})
    parts = []
    for line in paragraphs[marker + 1:]:
        if line.startswith(("Căn cứ", "Theo đề nghị", "Chính phủ ban hành", "Bộ trưởng", "Thủ tướng")) or re.fullmatch(r"[_\s]+", line):
            break
        parts.append(line)
    if not parts:
        raise ValueError(f"Cannot extract title from {path}")
    return " ".join(parts).strip()


def main() -> None:
    documents = {row["doc_number"]: row for row in json.loads((REGISTRY / "documents.json").read_text(encoding="utf-8"))}
    sources = {row["source_id"]: row for row in json.loads((REGISTRY / "sources.json").read_text(encoding="utf-8"))}
    chunks = [json.loads(line) for line in (ROOT / "data/staging/phase1-candidate/chunks.jsonl").read_text(encoding="utf-8").splitlines()]
    body_sources = {}
    for chunk in chunks:
        if chunk["content_kind"] == "normative":
            body_sources.setdefault(chunk["doc_id"], chunk["source_refs"][0]["source_id"])
    parsed = json.loads((ROOT / "data/staging/phase1-candidate/parsed.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for number, (issued, effective, url, notes) in FACTS.items():
        doc = documents[number]
        source = sources[body_sources[doc["doc_id"]]]
        if source["format"] != "docx" or source["source_id"] not in doc["source_ids"]:
            raise ValueError(f"Invalid registered DOCX body source for {number}")
        title = local_title(ROOT / source["path"], number)
        articles = parsed[doc["doc_id"]]["articles"]
        effective_article = next((row for row in reversed(articles)
                                  if row["content_kind"] == "normative" and "hiệu lực" in row["content"].lower()), None)
        locator = effective_article["source_locators"][0] if effective_article else "body/header"
        decision = ReviewDecision.model_validate({
            "subject_type": "document", "subject_id": doc["doc_id"], "review_type": "metadata",
            "input_sha256": input_hash(doc, sources), "conclusion": "verified",
            "evidence_source_id": source["source_id"],
            "evidence_locator": f"body/header; {locator}", "evidence_url": url,
            "reviewer": "Codex sol-medium (metadata review)", "reviewed_at": "2026-09-17",
            "values": {"title": title, "issued_date": issued, "valid_from": effective},
            "notes": notes + " Metadata only; content, applicability and amendment chain remain pending.",
        })
        filename = "metadata_" + re.sub(r"[^a-z0-9]+", "_", number.casefold().replace("đ", "d")).strip("_") + ".json"
        path = OUT / filename
        if path.exists():
            raise FileExistsError(f"Will not replace another review: {path}")
        path.write_text(decision.model_dump_json(indent=2) + "\n", encoding="utf-8")
        written.append({"doc_number": number, "title": title, "source": source["path"],
                        "official_url": url, "issued_date": issued, "valid_from": effective,
                        "review_file": path.relative_to(ROOT).as_posix(), "notes": notes})
    report = ROOT / "reports/phase1-closeout/remaining_metadata_review.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(written, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(written)} hash-bound metadata decisions")


if __name__ == "__main__":
    main()
