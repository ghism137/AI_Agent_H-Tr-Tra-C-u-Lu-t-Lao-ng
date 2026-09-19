"""Record an auditable Phase 1 baseline and work checklist from current artifacts."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/phase1-closeout"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def main() -> None:
    registry = ROOT / "data/registry"
    stage = ROOT / "data/staging/phase1-candidate"
    inventory = read(ROOT / "reports/phase1-implementation/inventory.json")
    documents = read(registry / "documents.json")
    coverage = read(registry / "coverage.json")
    relations = read(registry / "relations_verified.json")
    review = read(ROOT / "reports/phase1-implementation/review_queue.json")
    reconciliation = read(OUT / "source_reconciliation.json")
    status = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True,
                            text=True, encoding="utf-8", check=True).stdout.splitlines()
    tracked = [ROOT / name for name in ("data/chunks.jsonl", "data/document_relations.json",
                                         "data/staging/phase1-candidate/manifest.json",
                                         "data/staging/phase1-candidate/chunks.jsonl")]
    baseline = {"schema_version": 1, "observed_at": "2026-09-17", "git_status": status,
                "preexisting_worktree_note": "At task start README.md was staged; ingestion, docs, tests, data/registry, data/staging, reports and scripts already had uncommitted changes. No reset or blanket staging was performed. This snapshot was recorded after source inventory integration; see prior_reported_baseline for pre-closeout counts.",
                "sha256": {str(path.relative_to(ROOT)).replace('\\', '/'): digest(path) for path in tracked},
                "inventory_count": len(inventory["sources"]), "document_count": len(documents),
                "coverage_count": len(coverage), "verified_relation_count": len(relations),
                "review_counts": {key: len(review.get(key, [])) for key in ("random_chunks", "boundaries", "relations", "required_artifacts")},
                "prior_reported_baseline": {"source_count": 231, "document_count": 37, "chunk_count": 2440,
                                            "gate1": "FAIL", "note": "Pre-closeout handoff; current hashes above are observed after P1/P2 rebuild."}}
    checklist = {
        "schema_version": 1,
        "documents": [{"doc_id": doc["doc_id"], "status": doc["verification_status"],
                       "evidence": [], "blocker": "metadata, fidelity, amendment chain and applicability review",
                       "output": "document review decision"} for doc in documents],
        "coverage": [{"topic": item["topic"], "doc_number": item["doc_number"],
                      "status": item["verification_status"], "evidence": [],
                      "blocker": "date interval, population and amendment-chain review",
                      "output": "coverage decision"} for item in coverage],
        "source_reconciliation": [{"source_id": item["source_id"], "status": item["disposition"],
                                   "evidence": item["evidence"], "blocker": None,
                                   "output": "source_reconciliation.json"} for item in reconciliation["sources"]],
        "relations": [{"relation_id": item["relation_id"], "status": item["review_status"],
                       "evidence": [item.get("evidence_source_id"), item.get("evidence_locator")],
                       "blocker": "legal sign-off and chain scope review", "output": "relation decision"} for item in relations],
        "sample_reviews": [{"type": category, "id": item.get("chunk_id") or item.get("artifact_id") or item.get("doc_number") or item.get("relation_id"),
                            "status": item.get("review_status", item.get("legal_signoff", "pending")),
                            "evidence": [], "blocker": "full source comparison", "output": "review decision"}
                           for category in ("random_chunks", "boundaries", "relations", "required_artifacts")
                           for item in review.get(category, [])],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "baseline.json").write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "checklist.json").write_text(json.dumps(checklist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Baseline: {len(documents)} documents, {len(coverage)} coverage, {len(reconciliation['sources'])} source dispositions")


if __name__ == "__main__":
    main()
