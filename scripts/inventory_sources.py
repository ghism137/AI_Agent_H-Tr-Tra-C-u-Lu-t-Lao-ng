"""Inventory immutable inputs without inferring legal validity from filenames."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NUMBER = re.compile(r"(?<!\d)(\d{1,4})[/-](20\d{2}|19\d{2})[/-](QH\d+|NĐ-CP|ND-CP|TT-[A-ZĐ]+|QĐ-TTg)(?![A-Z\d])", re.I)
DOCX_EXT = ".docx"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def numbers(text: str) -> list[str]:
    return sorted({f"{m[1]}/{m[2]}/{m[3].upper().replace('ND-CP', 'NĐ-CP')}" for m in NUMBER.finditer(text)})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "phase1-implementation" / "inventory.json")
    args = parser.parse_args()
    records = []
    basename_groups: dict[str, list[dict]] = defaultdict(list)
    for path in sorted(RAW.rglob("*"), key=lambda item: item.as_posix().casefold()):
        if not path.is_file() or path.suffix.lower() not in {".md", DOCX_EXT, ".html", ".pdf"}:
            continue
        relative = path.relative_to(ROOT).as_posix()
        content_numbers = []
        if path.suffix.lower() == ".md":
            head = path.read_text(encoding="utf-8-sig", errors="replace")[:3000]
            content_numbers = numbers(head)
        digest = sha256(path)
        source_key = hashlib.sha256(f"{relative}\0{digest}".encode("utf-8")).hexdigest()
        entry = {
            "source_id": f"src:{source_key}",
            "path": relative,
            "format": path.suffix.lower().lstrip("."),
            "sha256": digest,
            "bytes": path.stat().st_size,
            "filename_numbers": numbers(path.stem),
            "header_numbers": content_numbers,
            "source_url": None,
            "collected_at": None,
            "verification_status": "pending",
        }
        if entry["filename_numbers"] and content_numbers and not set(entry["filename_numbers"]) & set(content_numbers):
            entry["identity_conflict"] = True
        records.append(entry)
        if path.suffix.lower() == DOCX_EXT:
            basename_groups[path.name.casefold()].append(entry)
    collisions = [
        {"basename": name, "sources": [entry["path"] for entry in group], "hashes": sorted({entry["sha256"] for entry in group})}
        for name, group in sorted(basename_groups.items()) if len(group) > 1
    ]
    output = {
        "schema_version": 1,
        "sources": records,
        "same_basename_docx": collisions,
        "identity_review_candidates": [entry["path"] for entry in records if entry.get("identity_conflict")],
        "counts": {extension: sum(item["format"] == extension for item in records) for extension in ("docx", "md", "html", "pdf")},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Inventory: {output['counts']}, {len(collisions)} duplicate basename groups, {len(output['identity_review_candidates'])} identity review candidates")


if __name__ == "__main__":
    main()
