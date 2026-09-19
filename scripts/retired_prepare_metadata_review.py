"""Collect source headers for human review of document metadata."""

from __future__ import annotations

import json
from pathlib import Path

import pymupdf

from backend.ingestion.docx_extractor import extract_docx
from backend.ingestion.html_extractor import extract_government_html


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/registry"
STAGE = ROOT / "data/staging/phase1-candidate"
OUT = ROOT / "reports/phase1-implementation/metadata_review_queue.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_header(source: dict) -> list[str]:
    path = ROOT / source["path"]
    if source["format"] == "pdf":
        with pymupdf.open(path) as pdf:
            text = "\n".join(pdf[index].get_text(sort=True) for index in range(min(3, len(pdf))))
        return [line.strip() for line in text.splitlines() if line.strip()][:45]
    if source["format"] == "html":
        blocks = extract_government_html(path)
    else:
        blocks = extract_docx(path)
    return [block.get("text", "")[:300] for block in blocks if block.get("text", "").strip()][:35]


def main() -> None:
    previous = {item["doc_number"]: item for item in read_json(OUT)} if OUT.exists() else {}
    sources = {source["source_id"]: source for source in read_json(REGISTRY / "sources.json")}
    documents = read_json(REGISTRY / "documents.json")
    coverage = {entry["doc_number"] for entry in read_json(REGISTRY / "coverage.json")}
    parsed = read_json(STAGE / "parsed.json")
    chunks = [json.loads(line) for line in (STAGE / "chunks.jsonl").read_text(encoding="utf-8").splitlines()]
    body_source = {}
    for chunk in chunks:
        if chunk["content_kind"] == "normative":
            body_source.setdefault(chunk["doc_id"], chunk["source_refs"][0]["source_id"])
    queue = []
    for doc in sorted(documents, key=lambda row: (row["doc_number"] not in coverage, row["doc_number"])):
        source = sources[body_source[doc["doc_id"]]]
        articles = [article for article in parsed[doc["doc_id"]]["articles"]
                    if article["content_kind"] == "normative"]
        item = {
            "doc_number": doc["doc_number"], "required_coverage": doc["doc_number"] in coverage,
            "source_id": source["source_id"], "source_path": source["path"],
            "source_url": source["source_url"], "source_sha256": source["sha256"],
            "source_header": source_header(source),
            "first_article": articles[0]["article_number"],
            "last_article": articles[-1]["article_number"],
            "title_review": "pending", "issued_date_review": "pending",
            "effective_date_review": "pending", "applicability_review": "pending",
        }
        old = previous.get(doc["doc_number"])
        if old and old["source_sha256"] == item["source_sha256"] and old["source_header"] == item["source_header"]:
            item.update({key: value for key, value in old.items() if key not in item or key.endswith("_review")})
        queue.append(item)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Metadata review queue: {len(queue)} documents; {len(coverage)} required coverage documents")


if __name__ == "__main__":
    main()
