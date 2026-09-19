"""Record three explicit repeal provisions from archived government text."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pymupdf

from backend.ingestion.schema import Relation


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/registry"
CASES = [
    {
        "source_doc": "45/2019/QH14", "source_article": "220", "target_doc": "10/2012/QH13",
        "effective_from": "2021-01-01", "pdf": "45-2019-QH14-congbao.pdf", "pages": [94, 95],
        "evidence": "Bộ luật Lao động số 10/2012/QH13 hết hiệu lực thi hành",
    },
    {
        "source_doc": "41/2024/QH15", "source_article": "140", "target_doc": "58/2014/QH13",
        "effective_from": "2025-07-01", "pdf": "41-2024-QH15-congbao.pdf", "pages": [88],
        "evidence": "Luật Bảo hiểm xã hội số 58/2014/QH13",
    },
    {
        "source_doc": "293/2025/NĐ-CP", "source_article": "5", "target_doc": "74/2024/NĐ-CP",
        "effective_from": "2026-01-01", "pdf": "293-2025-ND-CP-congbao.pdf", "pages": [3, 4],
        "evidence": "Nghị định số 74/2024/NĐ-CP",
    },
]


def main() -> None:
    sources = {entry["path"]: entry for entry in json.loads((REGISTRY / "sources.json").read_text(encoding="utf-8"))}
    records = []
    for case in CASES:
        path = ROOT / "data/raw/official" / case["pdf"]
        text = "\n".join(pymupdf.open(path)[page - 1].get_text() for page in case["pages"])
        if case["evidence"] not in text:
            raise ValueError(f"Evidence not found in {path}")
        source_path = path.relative_to(ROOT).as_posix()
        relation = Relation.model_validate({
            "relation_id": "rel:" + hashlib.sha256(f"{case['source_doc']}:{case['source_article']}:{case['target_doc']}".encode()).hexdigest()[:24],
            "relation_type": "repeals", "source_doc_id": f"doc:{case['source_doc']}",
            "source_provision_id": f"doc:{case['source_doc']}:body/article:{case['source_article']}",
            "target_doc_id": f"doc:{case['target_doc']}", "target_locators": [["body"]],
            "scope": "document", "operation": "expires", "effective_from": case["effective_from"],
            "evidence_source_id": sources[source_path]["source_id"],
            "evidence_locator": f"article:{case['source_article']};pdf/pages:{'-'.join(map(str, case['pages']))}",
            "review_status": "verified", "reviewed_by": "Codex source comparison",
            "reviewed_at": "2026-09-16",
            "notes": "Checked against archived government Công báo text layer. Legal reviewer sign-off remains separate.",
        })
        records.append(relation.model_dump(mode="json"))
    (REGISTRY / "relations_verified.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(records)} source-checked document expiry relations")


if __name__ == "__main__":
    main()
