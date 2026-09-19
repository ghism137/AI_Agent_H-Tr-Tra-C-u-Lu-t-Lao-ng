"""Check sources for op-nd74-4-5 and op-nd02-1-1."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/registry"

sources = json.loads((REGISTRY / "sources.json").read_text("utf-8"))
documents = json.loads((REGISTRY / "documents.json").read_text("utf-8"))

target_docs = {"74/2025/NĐ-CP", "02/2025/NĐ-CP", "146/2018/NĐ-CP"}

print("=== DOCUMENTS ===")
src_ids_of_interest = set()
for doc in documents:
    if doc["doc_number"] in target_docs:
        print(f'  doc_number: {doc["doc_number"]}')
        print(f'  doc_id: {doc["doc_id"]}')
        print(f'  verification_status: {doc["verification_status"]}')
        print(f'  issued_date: {doc.get("issued_date")}')
        print(f'  source_ids: {doc["source_ids"]}')
        src_ids_of_interest.update(doc["source_ids"])
        print()

print("=== SOURCES ===")
for src in sources:
    if src["source_id"] in src_ids_of_interest:
        p = ROOT / src["path"]
        exists = p.exists()
        print(f'  source_id: {src["source_id"]}')
        print(f'  path: {src["path"]}')
        print(f'  format: {src["format"]}')
        print(f'  exists: {exists}')
        print(f'  registered_sha256: {src["sha256"]}')
        if exists:
            actual_sha = hashlib.sha256(p.read_bytes()).hexdigest()
            print(f'  actual_sha256:     {actual_sha}')
            print(f'  hash_match: {actual_sha == src["sha256"]}')
            print(f'  size_bytes: {p.stat().st_size}')
        print()

print("=== CHECKING SPECIFIC OPERATION SOURCE CLAUSES ===")
ops_to_check = {
    "op-nd74-4-5": {
        "source_clause": "doc:74/2025/NĐ-CP:body/article:4/item:5",
        "target_locator": "doc:146/2018/NĐ-CP:body/article:14/item:5/point:a",
    },
    "op-nd02-1-1": {
        "source_clause": "doc:02/2025/NĐ-CP:body/article:1/item:1",
        "target_locator": "doc:146/2018/NĐ-CP:body/article:14",
    },
}

# Check staging parsed to see if source clauses resolve
STAGE = ROOT / "data/staging/phase1-candidate"
parsed_path = STAGE / "parsed.json"
if parsed_path.exists():
    parsed = json.loads(parsed_path.read_text("utf-8"))
    for op_id, info in ops_to_check.items():
        print(f"Op: {op_id}")
        src_clause = info["source_clause"]
        parts = src_clause.split(":", 2)
        src_doc_id = f"{parts[0]}:{parts[1]}"  # e.g. doc:74/2025/NĐ-CP
        src_path = parts[2].split("/") if len(parts) > 2 else []
        
        if src_doc_id in parsed:
            articles = parsed[src_doc_id]["articles"]
            # Find matching article
            found_articles = [a for a in articles if a["structural_path"][:len(src_path)] == src_path]
            print(f"  Source doc found in parsed: YES ({len(articles)} articles)")
            print(f"  Matching articles for {src_path}: {len(found_articles)}")
            for a in found_articles[:3]:
                print(f"    path={a['structural_path']}, content_preview={a['content'][:80]!r}")
        else:
            print(f"  Source doc {src_doc_id}: NOT IN PARSED")
        print()
else:
    print("WARNING: parsed.json not found in staging")
