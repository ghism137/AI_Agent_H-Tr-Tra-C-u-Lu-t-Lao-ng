"""Prepare a reproducible source-comparison queue; this is not legal sign-off."""

from __future__ import annotations

import json
import hashlib
import random
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/registry"
STAGE = ROOT / "data/staging/phase1-candidate"
OUT = ROOT / "reports/phase1-implementation/review_queue.json"


def review_hash(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def main() -> None:
    previous = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    sources = {item["source_id"]: item for item in json.loads((REGISTRY / "sources.json").read_text(encoding="utf-8"))}
    documents = {item["doc_number"]: item for item in json.loads((REGISTRY / "documents.json").read_text(encoding="utf-8"))}
    parsed = json.loads((STAGE / "parsed.json").read_text(encoding="utf-8"))
    chunks = [json.loads(line) for line in (STAGE / "chunks.jsonl").read_text(encoding="utf-8").splitlines()]
    normative = [item for item in chunks if item["content_kind"] == "normative"]
    sample = sorted(random.Random(1).sample(normative, 10), key=lambda item: item["chunk_id"])

    def entry(item: dict) -> dict:
        return {"chunk_id": item["chunk_id"], "doc_number": item["doc_number"],
                "structural_path": item["structural_path"], "content_excerpt": item["content"][:350],
                "review_input_sha256": review_hash({"content": item["content"], "refs": item["source_refs"],
                                                       "source_hashes": [sources[ref["source_id"]]["sha256"] for ref in item["source_refs"]]}),
                "sources": [{"path": sources[ref["source_id"]]["path"], "url": sources[ref["source_id"]]["source_url"],
                             "locator": ref["locator"]} for ref in item["source_refs"][:3]],
                "review_status": "pending"}

    boundaries = []
    for number in ("51/2024/QH15", "188/2025/NĐ-CP", "219/2025/NĐ-CP", "374/2025/NĐ-CP", "84/2015/QH13"):
        articles = parsed[f"doc:{number}"]["articles"]
        transition = next(((a, b) for a, b in zip(articles, articles[1:]) if a["content_kind"] != b["content_kind"]), None)
        if transition is None:
            middle = len(articles) // 2
            transition = (articles[middle - 1], articles[middle])
        boundaries.append({"doc_number": number,
                           "before": {"path": transition[0]["structural_path"], "end": transition[0]["content"][-180:],
                                      "locator": transition[0]["source_locators"][-1]},
                           "after": {"path": transition[1]["structural_path"], "start": transition[1]["content"][:180],
                                     "locator": transition[1]["source_locators"][0]},
                           "review_input_sha256": review_hash({"before": transition[0], "after": transition[1],
                                                                  "source_hashes": sorted(sources[sid]["sha256"] for sid in documents[number]["source_ids"])}),
                           "review_status": "pending"})
    relations = json.loads((REGISTRY / "relations_verified.json").read_text(encoding="utf-8"))
    relation_queue = [{"relation_id": item["relation_id"], "source_doc_id": item["source_doc_id"],
                       "target_doc_id": item["target_doc_id"], "effective_from": item["effective_from"],
                       "evidence_path": sources[item["evidence_source_id"]]["path"],
                       "evidence_locator": item["evidence_locator"],
                       "review_input_sha256": review_hash({"relation": item, "evidence_sha256": sources[item["evidence_source_id"]]["sha256"]}),
                       "legal_signoff": "pending"} for item in relations]
    required_artifacts = []
    selected = json.loads((REGISTRY / "source_selection.json").read_text(encoding="utf-8"))
    source_by_path = {row["path"]: row for row in sources.values()}
    comparison_pdf = {
        "188/2025/NĐ-CP": source_by_path["data/raw/official/188-2025-ND-CP-congbao-part2.pdf"],
        "219/2025/NĐ-CP": source_by_path["data/raw/official/219-2025-ND-CP-congbao.pdf"],
    }
    for number in ("188/2025/NĐ-CP", "219/2025/NĐ-CP"):
        selection = selected[f"doc:{number}"]
        for article in parsed[f"doc:{number}"]["articles"]:
            if article["content_kind"] != "form":
                continue
            source_path = selection.get("continuation", [selection["body"]])[0] if number.startswith("188/") and article["content"].startswith(tuple(f"Mẫu số {n}" for n in range(5, 13))) else selection["body"]
            source = source_by_path[source_path]
            match = re.match(r"Mẫu số\s+(\d+)", article["content"])
            if not match:
                continue
            number_label = int(match[1])
            if number.startswith("188/") and number_label < 5:
                continue
            artifact_id = f"{number}:form:{number_label}"
            comparison = comparison_pdf[number]
            required_artifacts.append({"artifact_id": artifact_id, "doc_number": number,
                                       "source_id": source["source_id"], "source_path": source_path,
                                       "comparison_source_id": comparison["source_id"],
                                       "comparison_source_path": comparison["path"],
                                       "source_locator": article["source_locators"][0],
                                       "content_excerpt": article["content"][:350],
                                       "review_input_sha256": review_hash({"content": article["content"],
                                                                           "source_sha256": source["sha256"],
                                                                           "comparison_sha256": comparison["sha256"]}),
                                       "review_status": "pending"})
    random_chunks = [entry(item) for item in sample]
    old_chunks = {item["chunk_id"]: item for item in previous.get("random_chunks", [])}
    for item in random_chunks:
        old = old_chunks.get(item["chunk_id"])
        if old and old.get("review_input_sha256") == item["review_input_sha256"]:
            item.update({key: value for key, value in old.items() if key not in item or key == "review_status"})
    old_boundaries = {item["doc_number"]: item for item in previous.get("boundaries", [])}
    for item in boundaries:
        old = old_boundaries.get(item["doc_number"])
        if old and old.get("review_input_sha256") == item["review_input_sha256"]:
            item.update({key: value for key, value in old.items() if key not in item or key == "review_status"})
    old_relations = {item["relation_id"]: item for item in previous.get("relations", [])}
    for item in relation_queue:
        old = old_relations.get(item["relation_id"])
        if old and all(old.get(key) == value for key, value in item.items() if key != "legal_signoff"):
            item.update({key: value for key, value in old.items() if key not in item or key == "legal_signoff"})
    old_artifacts = {item["artifact_id"]: item for item in previous.get("required_artifacts", [])}
    for item in required_artifacts:
        old = old_artifacts.get(item["artifact_id"])
        if old and old.get("review_input_sha256") == item["review_input_sha256"]:
            item.update({key: value for key, value in old.items() if key not in item or key == "review_status"})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"random_chunks": random_chunks,
                               "boundaries": boundaries, "relations": relation_queue,
                               "required_artifacts": required_artifacts},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Review queue: {len(sample)} chunks, {len(boundaries)} boundaries, {len(relation_queue)} relations")


if __name__ == "__main__":
    main()
