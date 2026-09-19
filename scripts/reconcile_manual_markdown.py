"""Trace flattened Markdown forms back to DOCX candidates without legal sign-off."""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from backend.ingestion.docx_extractor import extract_docx
from scripts.build_registry import source_document


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "reports/phase1-implementation/inventory.json"
OUT = ROOT / "reports/phase1-closeout/source_reconciliation.json"


def words(text: str) -> list[str]:
    text = unicodedata.normalize("NFC", text).casefold()
    return re.findall(r"\w+", text, flags=re.UNICODE)


def docx_text(path: Path) -> str:
    lines = []
    for block in extract_docx(path):
        if block["kind"] == "paragraph":
            lines.append(block["text"])
        else:
            lines.extend(" ".join(row) for row in block["rows"])
    return "\n".join(lines)


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    docx_by_stem = defaultdict(list)
    for source in inventory["sources"]:
        if source["format"] == "docx":
            docx_by_stem[Path(source["path"]).stem.casefold()].append(source)
    rows = []
    for source in inventory["sources"]:
        if not source["path"].startswith("data/raw/manual_md/") or source_document(source):
            continue
        md_words = words((ROOT / source["path"]).read_text(encoding="utf-8-sig"))
        candidates = []
        for docx in docx_by_stem[Path(source["path"]).stem.casefold()]:
            other_words = words(docx_text(ROOT / docx["path"]))
            ratio = difflib.SequenceMatcher(None, md_words, other_words, autojunk=False).ratio()
            shared = sum((Counter(md_words) & Counter(other_words)).values())
            containment = shared / len(md_words) if md_words else 0
            candidates.append({"source_id": docx["source_id"], "path": docx["path"],
                               "sha256": docx["sha256"], "doc_number_candidate": source_document(docx),
                               "token_sequence_similarity": round(ratio, 4),
                               "markdown_token_containment": round(containment, 4)})
        candidates.sort(key=lambda x: (x["markdown_token_containment"], x["token_sequence_similarity"]), reverse=True)
        best = candidates[0] if candidates else None
        runner_up = candidates[1] if len(candidates) > 1 else None
        # Identical basename alone is not identity evidence. Require substantial
        # ordered text agreement and separation from competing same-name forms.
        accepted = bool(best and best["doc_number_candidate"] and
                        best["markdown_token_containment"] >= 0.90 and
                        (runner_up is None or best["markdown_token_containment"] - runner_up["markdown_token_containment"] >= 0.08))
        rows.append({"source_id": source["source_id"], "path": source["path"],
                     "sha256": source["sha256"],
                     "disposition": "duplicate_derivative_excluded" if accepted else "unresolved_quarantine",
                     "mapped_doc_number": best["doc_number_candidate"] if accepted else None,
                     "evidence": {"method": "same basename plus normalized token containment and sequence comparison",
                                  "candidates": candidates},
                     "reason": "DOCX parent identified; Markdown is a flattened derivative and is excluded from extraction" if accepted
                               else "Identity or content match needs manual comparison"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"schema_version": 1, "sources": rows,
                               "counts": {status: sum(row["disposition"] == status for row in rows)
                                          for status in ("duplicate_derivative_excluded", "unresolved_quarantine")}},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"total": len(rows), "counts": json.loads(OUT.read_text(encoding="utf-8"))["counts"]}))


if __name__ == "__main__":
    main()
