"""Move legacy relation claims into a review queue; verify none automatically."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from backend.ingestion.schema import Relation


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    source = ROOT / "data/document_relations.json"
    target = ROOT / "data/registry/relations_candidates.json"
    verified = ROOT / "data/registry/relations_verified.json"
    legacy = json.loads(source.read_text(encoding="utf-8"))
    candidates = []
    for entry in legacy:
        fingerprint = hashlib.sha256(json.dumps(entry, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:24]
        record = Relation.model_validate({
            "relation_id": f"candidate:{fingerprint}", "relation_type": {
                "can_cu": "references", "huong_dan": "guides", "sua_doi": "amends",
                "bo_sung": "supplements", "thay_the": "replaces", "bai_bo": "repeals",
            }[entry["relation_type"]],
            "source_doc_id": f"doc:{entry.get('source_doc', 'UNKNOWN')}",
            "target_doc_id": f"doc:{entry.get('target_doc', 'UNKNOWN')}",
            "target_locators": [], "scope": "unknown", "operation": entry["relation_type"],
            "effective_from": None, "effective_to": None, "evidence_source_id": None,
            "evidence_locator": None, "review_status": "pending",
            "notes": f"Unverified legacy claim: {json.dumps(entry, ensure_ascii=False, sort_keys=True)}",
        }).model_dump(mode="json")
        candidates.append(record)
    candidates.sort(key=lambda item: item["relation_id"])
    target.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not verified.exists():
        verified.write_text("[]\n", encoding="utf-8")
    verified_count = len(json.loads(verified.read_text(encoding="utf-8")))
    print(f"Quarantined {len(candidates)} legacy relations; preserved {verified_count} verified relations")


if __name__ == "__main__":
    main()
