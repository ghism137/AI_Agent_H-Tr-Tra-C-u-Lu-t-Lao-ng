"""Report objective Phase 1 release blockers without changing the candidate."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from scripts.build_registry import source_document
from scripts.build_phase1_stage import candidate_fingerprint


def review_hash(value: dict) -> str:
    """Canonical hash for a review input dict (canonical JSON, sorted keys)."""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/registry"
STAGE = ROOT / "data/staging/phase1-candidate"
QUEUE = ROOT / "reports/phase1-implementation/review_queue.json"
RECONCILIATION = ROOT / "reports/phase1-closeout/source_reconciliation.json"
ACQUISITION_GAPS = ROOT / "reports/phase1-closeout/acquisition_gaps.json"
OUT = ROOT / "reports/phase1-implementation/gate1_preflight.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def form_id(doc_number: str, article: dict) -> str | None:
    if article["content_kind"] != "form":
        return None
    match = re.match(r"Mẫu số\s+(\d+)", article["content"])
    return f"{doc_number}:form:{int(match[1])}" if match else None


def audit() -> dict:
    sources = read_json(REGISTRY / "sources.json")
    documents = read_json(REGISTRY / "documents.json")
    coverage = read_json(REGISTRY / "coverage.json")
    quarantine = read_json(REGISTRY / "quarantine.json")
    relations = read_json(REGISTRY / "relations_verified.json")
    manifest = read_json(STAGE / "manifest.json")
    expected_release_id, expected_code_hash = candidate_fingerprint()
    review = read_json(QUEUE)
    reconciliation = read_json(RECONCILIATION)
    acquisition_gaps = read_json(ACQUISITION_GAPS) if ACQUISITION_GAPS.exists() else {"documents": []}
    chunks = [json.loads(line) for line in (STAGE / "chunks.jsonl").read_text(encoding="utf-8").splitlines()]
    versions = [json.loads(line) for line in (STAGE / "provision_versions.jsonl").read_text(encoding="utf-8").splitlines()]
    parsed = read_json(STAGE / "parsed.json")

    bad_hashes = []
    for source in sources:
        path = ROOT / source["path"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            bad_hashes.append(source["source_id"])
    source_ids = {source["source_id"] for source in sources}
    sources_by_id = {source["source_id"]: source for source in sources}
    documents_by_number = {}
    for doc in documents:
        documents_by_number[doc["doc_number"]] = doc
        for alias in doc.get("aliases", []):
            alias_num = alias.removeprefix("doc:")
            documents_by_number[alias_num] = doc

    unresolved_dependencies = []
    for row in acquisition_gaps["documents"]:
        number = row["number"]
        if number not in documents_by_number:
            unresolved_dependencies.append(number)
        else:
            resolved_doc = documents_by_number[number]
            if resolved_doc["doc_id"] not in parsed:
                unresolved_dependencies.append(number)
    unresolved_dependencies = sorted(unresolved_dependencies)
    bad_refs = sorted({ref["source_id"] for chunk in chunks for ref in chunk["source_refs"]
                       if ref["source_id"] not in source_ids})
    chunk_ids = [chunk["chunk_id"] for chunk in chunks]
    version_ids = {version["provision_version_id"] for version in versions}
    bad_version_refs = sorted({chunk["provision_version_id"] for chunk in chunks
                               if chunk["provision_version_id"] not in version_ids})
    bad_version_content = sorted(version["provision_version_id"] for version in versions
                                 if not version["provision_version_id"].endswith(
                                     "@" + hashlib.sha256(version["content"].encode("utf-8")).hexdigest()[:16])
                                 or any(ref["source_id"] not in source_ids for ref in version["source_refs"]))
    pending_reviews = {
        "random_chunks": sum(item["review_status"] != "verified" for item in review["random_chunks"]),
        "boundaries": sum(item["review_status"] != "verified" for item in review["boundaries"]),
        "relations": sum(item["legal_signoff"] != "verified" for item in review["relations"]),
        "required_artifacts": sum(item["review_status"] != "verified" for item in review.get("required_artifacts", [])),
    }
    unsupported_signoffs = []
    for category, status_key in (("random_chunks", "review_status"), ("boundaries", "review_status"),
                                 ("relations", "legal_signoff"), ("required_artifacts", "review_status")):
        for item in review.get(category, []):
            if item.get(status_key) == "verified" and not all(item.get(key) for key in ("reviewed_by", "reviewed_at", "comparison_note")):
                unsupported_signoffs.append(item.get("chunk_id") or item.get("artifact_id") or item.get("doc_number") or item.get("relation_id"))
    chunks_by_id = {chunk["chunk_id"]: chunk for chunk in chunks}
    stale_reviews = []
    for item in review["random_chunks"]:
        chunk = chunks_by_id.get(item["chunk_id"])
        if not chunk:
            stale_reviews.append(item["chunk_id"])
            continue
        expected = review_hash({"content": chunk["content"], "refs": chunk["source_refs"],
                                "source_hashes": [sources_by_id[ref["source_id"]]["sha256"]
                                                  for ref in chunk["source_refs"] if ref["source_id"] in sources_by_id]})
        if item.get("review_input_sha256") != expected:
            stale_reviews.append(item["chunk_id"])
    for item in review["boundaries"]:
        number = item["doc_number"]
        if number not in documents_by_number or f"doc:{number}" not in parsed:
            stale_reviews.append(number)
            continue
        articles = parsed[f"doc:{number}"]["articles"]
        transition = next(((a, b) for a, b in zip(articles, articles[1:])
                           if a["content_kind"] != b["content_kind"]), None)
        if transition is None:
            middle = len(articles) // 2
            transition = (articles[middle - 1], articles[middle])
        expected = review_hash({"before": transition[0], "after": transition[1],
                                "source_hashes": sorted(sources_by_id[sid]["sha256"]
                                                        for sid in documents_by_number[number]["source_ids"])})
        if item.get("review_input_sha256") != expected:
            stale_reviews.append(number)
    for item in review.get("required_artifacts", []):
        source = sources_by_id.get(item["source_id"])
        comparison = sources_by_id.get(item.get("comparison_source_id"))
        articles = parsed.get(f"doc:{item['doc_number']}", {}).get("articles", [])
        match = next((article for article in articles if form_id(item["doc_number"], article) == item["artifact_id"]), None)
        expected = (review_hash({"content": match["content"], "source_sha256": source["sha256"],
                                 "comparison_sha256": comparison["sha256"]})
                    if source and comparison and match else None)
        if item.get("review_input_sha256") != expected:
            stale_reviews.append(item["artifact_id"])
    relations_by_id = {row["relation_id"]: row for row in relations}
    for item in review["relations"]:
        relation = relations_by_id.get(item["relation_id"])
        source = sources_by_id.get(relation.get("evidence_source_id")) if relation else None
        expected = review_hash({"relation": relation, "evidence_sha256": source["sha256"]}) if source else None
        if item.get("review_input_sha256") != expected:
            stale_reviews.append(item["relation_id"])
    bad_dispositions = []
    for item in reconciliation["sources"]:
        source = sources_by_id.get(item["source_id"])
        if (not source or source["sha256"] != item["sha256"] or
                item["disposition"] not in {"duplicate_derivative_excluded", "mapped"} or
                item.get("mapped_doc_number") not in documents_by_number):
            bad_dispositions.append(item["source_id"])
    blockers = []
    # Operations integrity: reject ops with verified status but unverifiable provenance
    operations_path = REGISTRY / "operations.json"
    operations = json.loads(operations_path.read_text(encoding="utf-8")) if operations_path.exists() else []
    ops_missing_id = [op.get("operation_id", "<no id>") for op in operations if "operation_id" not in op]
    ops_verified_unknown_hash = [
        op.get("operation_id", "<no id>") for op in operations
        if op.get("review_status") == "verified"
        and (op.get("source_hash") == "unknown" or op.get("target_hash") == "unknown")
    ]
    if ops_missing_id:
        blockers.append(f"operations missing operation_id field: {ops_missing_id}")
    if ops_verified_unknown_hash:
        blockers.append(
            f"operations marked verified but have unknown source/target hash "
            f"(unprovable provenance): {ops_verified_unknown_hash}"
        )
    if (
        manifest["release_id"] != expected_release_id or
        manifest["parser_code_sha256"] != expected_code_hash or
        manifest["sources_sha256"] != hashlib.sha256((REGISTRY / "sources.json").read_bytes()).hexdigest() or
        manifest["verified_relations_sha256"] != hashlib.sha256((REGISTRY / "relations_verified.json").read_bytes()).hexdigest() or
        manifest.get("operations_sha256") != (
            hashlib.sha256(operations_path.read_bytes()).hexdigest() if operations_path.exists() else "absent"
        )
    ):
        blockers.append("candidate was built from stale registry or code inputs")
    if (manifest["quarantined_documents"] or manifest["missing_required_parsed_documents"]
            or manifest["documents_parsed"] != len(documents) or manifest["chunks"] != len(chunks)
            or manifest.get("provision_versions") != len(versions)):
        blockers.append("staging parse counts or required coverage are incomplete")
    if (bad_hashes or bad_refs or len(chunk_ids) != len(set(chunk_ids)) or
            bad_version_refs or bad_version_content or len(version_ids) != len(versions)):
        blockers.append("source integrity, lineage or chunk identity failed")
    if any(doc["verification_status"] != "verified" for doc in documents):
        blockers.append("document identity and metadata verification incomplete")
    if any(doc["issued_date"] is None or doc["title"] == doc["doc_number"] for doc in documents):
        blockers.append("document issue dates or titles are placeholders")
    if any(item["verification_status"] != "verified" or item["gap"] for item in coverage):
        blockers.append("required coverage and temporal scope not verified")
    if any(chunk["verification_status"] != "verified" for chunk in chunks):
        blockers.append("candidate chunks have not been verified")
    if any(version["verification_status"] != "verified" for version in versions):
        blockers.append("provision versions have not been verified")
    if any(pending_reviews.values()):
        blockers.append("manual source comparison lacks sign-off")
    if (len(review["random_chunks"]) < 10 or len(review["boundaries"]) < 5 or
            len(review["relations"]) < 3 or len(review.get("required_artifacts", [])) < 12 or
            stale_reviews or unsupported_signoffs):
        blockers.append("source comparison sample is incomplete or stale")
    manual_md_ids = {source["source_id"] for source in sources
                     if source["path"].startswith("data/raw/manual_md/") and source_document(source) is None}
    disposition_ids = {row["source_id"] for row in reconciliation["sources"]}
    if bad_dispositions or manual_md_ids != disposition_ids:
        blockers.append("manual Markdown source dispositions are incomplete or stale")
    if quarantine:
        blockers.append("unresolved source identities remain quarantined")
    if unresolved_dependencies:
        blockers.append("known amendment or historical dependencies have no parsed primary source")
    return {
        "gate1": "FAIL" if blockers else "PASS",
        "manifest_release_id": manifest["release_id"],
        "counts": {
            "sources": len(sources), "documents": len(documents), "coverage": len(coverage),
            "chunks": len(chunks), "quarantined_sources": len(quarantine),
            "provision_versions": len(versions),
            "verified_relations": sum(row["review_status"] == "verified" for row in relations),
            "documents_by_status": dict(Counter(row["verification_status"] for row in documents)),
            "chunks_by_status": dict(Counter(row["verification_status"] for row in chunks)),
        },
        "source_hash_mismatches": bad_hashes,
        "missing_source_references": bad_refs,
        "duplicate_chunk_ids": len(chunk_ids) - len(set(chunk_ids)),
        "bad_version_references": bad_version_refs,
        "bad_version_content": bad_version_content,
        "missing_issued_dates": sum(row["issued_date"] is None for row in documents),
        "placeholder_titles": sum(row["title"] == row["doc_number"] for row in documents),
        "pending_reviews": pending_reviews,
        "stale_reviews": stale_reviews,
        "unsupported_signoffs": unsupported_signoffs,
        "bad_source_dispositions": bad_dispositions,
        "unresolved_dependencies": unresolved_dependencies,
        "blockers": blockers,
    }


def main() -> None:
    result = audit()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True))


if __name__ == "__main__":
    main()
