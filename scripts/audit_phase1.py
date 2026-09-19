"""Read-only Phase 1 audit; writes evidence only to the requested report directory.

Run from the repository root with: python scripts/audit_phase1.py
This is an audit aid, not a legal verification or production ingestion gate.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

from backend.ingestion.parser import parse_legal_document, remove_watermarks
from backend.ingestion.extract_relations import extract_relations
from backend.retrieval.graph_utils import is_valid


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/phase1-review-2026-09-16")
    args = parser.parse_args()
    data = ROOT / "data"
    chunks_path = data / "chunks.jsonl"
    chunks = [json.loads(s) for s in chunks_path.read_text(encoding="utf-8").splitlines() if s.strip()]
    relations = read_json(data / "document_relations.json")
    review = read_json(data / "relations_needs_review.json")
    raw_files = sorted((data / "raw/manual_md").glob("*.md"))
    word_files = sorted((data / "raw/word").rglob("*.docx"))
    cleaned = [(f, read_json(f)) for f in sorted((data / "cleaned").glob("*.json"))]
    docs = Counter(c["doc_number"] for c in chunks)
    id_rows = defaultdict(list)
    text_rows = defaultdict(list)
    for row, chunk in enumerate(chunks, 1):
        id_rows[chunk["chunk_id"]].append(row)
        text_rows[hashlib.sha256(chunk["content"].encode()).hexdigest()].append(row)
    missing_fields = ["issued_date", "expiry_date", "clause_range", "content_length", "source_url", "crawled_at"]
    raw_by_name = {f.stem: f for f in raw_files}
    cleaned_by_doc = defaultdict(list)
    for f, d in cleaned:
        cleaned_by_doc[d["metadata"]["doc_number"]].append(f)
    word_by_name = defaultdict(list)
    for f in word_files:
        word_by_name[f.name].append({"path": f.relative_to(ROOT).as_posix(), "sha256": sha(f)})
    canonical = re.compile(r"\d+/\d{4}/[A-ZĐ0-9]+(?:-[A-ZĐ0-9]+)*", re.I)
    plan = (data / "crawl_plan.md").read_text(encoding="utf-8")
    plan_ids = re.findall(r"\| (\d+/\d{4}/[A-Za-zĐđ0-9-]+) \|", plan)

    def sample(row):
        c = chunks[row - 1]
        source_files = [raw_by_name[f.stem] for f in cleaned_by_doc[c["doc_number"]] if f.stem in raw_by_name]
        normalized_sources = ["\n".join(" ".join(s.split()) for s in f.read_text(encoding="utf-8").splitlines() if s.strip()) for f in source_files]
        lines = c["content"].splitlines()
        return {
            "row": row, "chunk_id": c["chunk_id"], "doc_number": c["doc_number"],
            "hierarchy_path": c["hierarchy_path"], "chars": len(c["content"]),
            "raw_candidates": [f.relative_to(ROOT).as_posix() for f in source_files],
            "all_content_lines_found_in_candidate_raw": any(all(line in s for line in lines) for s in normalized_sources),
            "unique_id": len(id_rows[c["chunk_id"]]) == 1,
            "has_effective_date": bool(c.get("effective_date")),
            "has_source_url": bool(c.get("source_url") or c.get("url")),
            "official_source_verification": "not_completed",
            "excerpt": c["content"][:350],
        }

    boundary_ids = ["145-2020-NĐ-CP_D1", "145-2020-NĐ-CP_D115_K1-K2", "11-2020-TT-BLĐTBXH_D3_K3-K4", "152-2020-NĐ-CP_D4_K3", "135-2020-NĐ-CP_D9_K8-K24"]
    boundaries = [sample(id_rows[i][-1]) for i in boundary_ids if i in id_rows]
    alpha = parse_legal_document("Điều 1. Gốc\nA\nĐiều 1a. Bổ sung\nB", {})
    hierarchy = parse_legal_document("Chương I\nMục 1\nĐiều 1. A\nX\nChương II\nĐiều 2. B\nY", {})
    relation = {"source_doc": "NEW", "target_doc": "OLD", "relation_type": "bai_bo", "scope": "dieu_khoan_cu_the", "target_article": "Điều 1 và 2", "status": "active", "effective_date": "2020-01-01"}
    cases = {
        "alphanumeric_article": {"expected_articles": ["1", "1a"], "actual_articles": [a["article_number"] for a in alpha["articles"]]},
        "chapter_reset": {"expected_path": "Chương II", "actual_path": hierarchy["articles"][1]["hierarchy_path"]},
        "watermark_removes_legal_sentence": {"input": "1. Tuân thủ pháp luật Việt Nam.", "expected": "1. Tuân thủ pháp luật Việt Nam.", "actual": remove_watermarks("1. Tuân thủ pháp luật Việt Nam.")},
        "citation_mistaken_for_amendment": {"input": "Căn cứ Hiến pháp năm 1992 đã được sửa đổi, bổ sung theo Nghị quyết số 51/2001/QH10;", "expected": "no amendment issued by 10/2012/QH13", "actual": extract_relations("Căn cứ Hiến pháp năm 1992 đã được sửa đổi, bổ sung theo Nghị quyết số 51/2001/QH10;", "10/2012/QH13")[0]},
        "multiple_article_target": {"expected_valid": False, "actual_valid": is_valid("OLD", "Điều 1", [relation], "2026-09-16")},
    }
    relation.update(scope="toan_bo", status="rejected")
    relation.pop("effective_date")
    cases["rejected_undated_relation"] = {"expected_valid": True, "actual_valid": is_valid("OLD", "Điều 1", [relation], "1900-01-01")}
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    numbering = {}
    law84 = next((f for f in word_files if f.name == "Luật-84-2015-QH13.docx"), None)
    if law84:
        with zipfile.ZipFile(law84) as z:
            xml = ET.fromstring(z.read("word/document.xml"))
            nums = ET.fromstring(z.read("word/numbering.xml"))
            for para in xml.findall(".//w:p", ns):
                text = "".join(n.text or "" for n in para.findall(".//w:t", ns)).strip()
                if text == "Phạm vi điều chỉnh":
                    num = para.find("w:pPr/w:numPr/w:numId", ns)
                    if num is not None:
                        num_id = num.get("{" + ns["w"] + "}val")
                        abstract = nums.find(f"w:num[@w:numId='{num_id}']/w:abstractNumId", ns)
                        aid = abstract.get("{" + ns["w"] + "}val")
                        fmt = nums.find(f"w:abstractNum[@w:abstractNumId='{aid}']/w:lvl[@w:ilvl='0']/w:lvlText", ns)
                        numbering = {"path": law84.relative_to(ROOT).as_posix(), "paragraph_text": text, "num_id": num_id, "format": fmt.get("{" + ns["w"] + "}val")}
                    break
    report = {
        "review_date": "2026-09-16", "scope": "local artifacts; official-source sign-off incomplete",
        "counts": {
            "word_files_recursive": len(word_files), "raw_markdown": len(raw_files), "cleaned_json": len(cleaned),
            "chunks": len(chunks), "unique_chunk_ids": len(id_rows), "document_identifiers_not_verified_documents": len(docs),
            "duplicate_id_groups": sum(len(r) > 1 for r in id_rows.values()),
            "duplicate_id_excess_rows": sum(len(r) - 1 for r in id_rows.values()),
            "duplicate_content_groups": sum(len(r) > 1 for r in text_rows.values()),
            "duplicate_content_excess_rows": sum(len(r) - 1 for r in text_rows.values()),
            "empty_effective_date": sum(not c.get("effective_date") for c in chunks),
            "empty_source_url": sum(not (c.get("source_url") or c.get("url")) for c in chunks),
            "malformed_decree_circular_decision_ids": sum(bool(re.fullmatch(r"\d+/\d{4}/.+", c["doc_number"])) and c["doc_number"].count("/") > 2 for c in chunks),
            "invalid_canonical_doc_number": sum(not canonical.fullmatch(c["doc_number"]) for c in chunks),
            "over_2000_chars": sum(len(c["content"]) > 2000 for c in chunks),
            "max_chars": max(len(c["content"]) for c in chunks),
            "article_all_chunks": sum(c["article_number"].startswith("ALL") for c in chunks),
            "non_nfc_content": sum(unicodedata.normalize("NFC", c["content"]) != c["content"] for c in chunks),
            "relations": len(relations), "undated_relations": sum(not r.get("effective_date") for r in relations),
            "relations_needing_review": len(review), "plan_rows": len(plan_ids), "plan_unique_doc_numbers": len(set(plan_ids)),
        },
        "missing_original_schema_fields": {k: sum(k not in c for c in chunks) for k in missing_fields},
        "status_counts": dict(Counter(c["status"] for c in chunks)), "doc_counts": dict(docs),
        "core_absent_as_canonical_ids": [i for i in ["45/2019/QH14", "25/2008/QH12", "41/2024/QH15", "74/2025/QH15", "293/2025/NĐ-CP"] if i not in docs],
        "orphan_cleaned": [f.relative_to(ROOT).as_posix() for f, d in cleaned if d["metadata"]["doc_number"] not in docs],
        "duplicate_ids": {k: r for k, r in id_rows.items() if len(r) > 1},
        "colliding_word_filenames": {k: fs for k, fs in word_by_name.items() if len(fs) > 1},
        "random_seed": 20260916,
        "random_samples": [sample(r) for r in sorted(random.Random(20260916).sample(range(1, len(chunks) + 1), 10))],
        "boundary_samples": boundaries, "reproductions": cases, "docx_numbering_evidence": numbering,
        "input_sha256": {f.relative_to(ROOT).as_posix(): sha(f) for f in [chunks_path, data / "document_relations.json", data / "relations_needs_review.json", data / "documents_metadata.json", *raw_files, *word_files, *[f for f, _ in cleaned], *sorted((ROOT / "backend").rglob("*.py")), *sorted((ROOT / "tests").glob("*.py"))]},
    }
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "audit.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], ensure_ascii=False, indent=2))
    print(f"Evidence: {path}")


if __name__ == "__main__":
    main()
