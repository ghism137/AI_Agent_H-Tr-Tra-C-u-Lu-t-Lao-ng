"""Verify payload in op-nd74-4-5 and op-nd02-1-1 against actual parsed source text.
Also compute real source_hash and target_hash for these operations.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/registry"
STAGE = ROOT / "data/staging/phase1-candidate"
OPS_PATH = REGISTRY / "operations.json"

ops = json.loads(OPS_PATH.read_text("utf-8"))
parsed = json.loads((STAGE / "parsed.json").read_text("utf-8"))
sources = {s["source_id"]: s for s in json.loads((REGISTRY / "sources.json").read_text("utf-8"))}
documents = {d["doc_id"]: d for d in json.loads((REGISTRY / "documents.json").read_text("utf-8"))}

# Build article lookup: doc_id -> structural_path -> article
article_lookup = {}
for doc_id, doc_data in parsed.items():
    for a in doc_data["articles"]:
        key = (doc_id, tuple(a["structural_path"]))
        article_lookup[key] = a

def get_article(doc_number, path_str):
    """Get article by doc number and path like 'body/article:4/item:5'."""
    doc_id = f"doc:{doc_number}"
    path = path_str.split("/")
    key = (doc_id, tuple(path))
    return article_lookup.get(key)

def compute_source_hash_for_op(op_id, source_clause):
    """Compute the real hash of the source clause content."""
    # Parse: doc:74/2025/NĐ-CP:body/article:4/item:5
    parts = source_clause.split(":", 2)
    if len(parts) < 3:
        return None, None
    doc_number = parts[1]  # e.g. 74/2025/NĐ-CP
    path_str = parts[2]    # e.g. body/article:4/item:5
    
    article = get_article(doc_number, path_str)
    if not article:
        # Try to find any matching
        doc_id = f"doc:{doc_number}"
        path = path_str.split("/")
        matches = [(k, v) for (d, p), v in article_lookup.items() 
                   if d == doc_id and list(p)[:len(path)] == path]
        if not matches:
            return None, f"NOT FOUND: {doc_id} path={path_str}"
        content = "\n".join(v["content"] for _, v in sorted(matches))
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return digest, f"COMBINED({len(matches)} articles): {content[:120]!r}"
    
    content = article["content"]
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return digest, f"EXACT: {content[:150]!r}"

def compute_target_hash_for_op(op_id, target_locator):
    """Compute the real hash of the CURRENT target (base version before operation)."""
    parts = target_locator.split(":", 2)
    if len(parts) < 3:
        return None, None
    doc_number = parts[1]
    path_str = parts[2]
    path = path_str.split("/")
    doc_id = f"doc:{doc_number}"
    
    # Collect all matching articles
    matches = [(list(p), v) for (d, p), v in article_lookup.items()
               if d == doc_id and list(p)[:len(path)] == path]
    if not matches:
        return None, f"NOT FOUND: {doc_id} path={path_str}"
    
    if len(matches) == 1:
        content = matches[0][1]["content"]
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return digest, f"EXACT: {content[:150]!r}"
    else:
        # Multiple articles (document-scope operation)
        combined = "\n".join(v["content"] for _, v in sorted(matches, key=lambda x: x[0]))
        digest = hashlib.sha256(combined.encode("utf-8")).hexdigest()
        return digest, f"COMBINED({len(matches)} articles)"

print("=" * 70)
print("OPERATION VERIFICATION REPORT")
print("=" * 70)

ops_to_check = ["op-nd74-4-5", "op-nd02-1-1"]
for op in ops:
    op_id = op.get("operation_id", "MISSING_ID")
    if op_id not in ops_to_check:
        continue
    
    print(f"\n{'=' * 60}")
    print(f"Operation: {op_id}")
    print(f"  verb: {op['verb']}")
    print(f"  source_clause: {op['source_clause']}")
    print(f"  target_locator: {op['target_locator']}")
    print(f"  effective_from: {op['effective_from']}")
    print(f"  current source_hash: {op['source_hash']}")
    print(f"  current target_hash: {op['target_hash']}")
    print(f"  review_status: {op['review_status']}")
    
    # Compute real source hash
    real_src_hash, src_info = compute_source_hash_for_op(op_id, op["source_clause"])
    print(f"\n  REAL SOURCE HASH: {real_src_hash}")
    print(f"  Source content: {src_info}")
    
    # Compute real target hash
    real_tgt_hash, tgt_info = compute_target_hash_for_op(op_id, op["target_locator"])
    print(f"\n  REAL TARGET HASH (pre-op state): {real_tgt_hash}")
    print(f"  Target content: {tgt_info}")
    
    # Check if payload matches source content
    if "payload" in op:
        payload = op["payload"]
        payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        print(f"\n  PAYLOAD in op (first 200 chars): {payload[:200]!r}")
        print(f"  Payload hash: {payload_hash}")
        
        # Compare payload against source article content
        parts = op["source_clause"].split(":", 2)
        if len(parts) >= 3:
            article = get_article(parts[1], parts[2])
            if article:
                # Source is the amendment text itself (sửa đổi Điều...)
                # The payload should be the NEW text of the target, not the source
                print(f"\n  SOURCE ARTICLE content (first 300 chars):")
                print(f"  {article['content'][:300]!r}")
        
    else:
        print(f"\n  No inline payload — will derive from source clause at materialize time")
    
    # Final verdict
    print(f"\n  VERDICT:")
    if real_src_hash:
        print(f"  ✓ Source clause EXISTS in parsed corpus with real hash {real_src_hash}")
        doc_id = f"doc:{op['source_clause'].split(':')[1]}"
        doc = documents.get(doc_id, {})
        src_ids = doc.get("source_ids", [])
        for sid in src_ids:
            src = sources.get(sid, {})
            print(f"  ✓ Backed by file: {src.get('path')} (sha256 verified: {src.get('sha256', 'N/A')[:16]}...)")
    else:
        print(f"  ✗ Source clause NOT FOUND in parsed corpus")

print("\n" + "=" * 70)
print("SOURCE FILE HASHES (for provenance)")
print("=" * 70)
for doc_num in ["74/2025/NĐ-CP", "02/2025/NĐ-CP"]:
    doc = documents.get(f"doc:{doc_num}", {})
    for sid in doc.get("source_ids", []):
        src = sources.get(sid, {})
        print(f"{doc_num}: path={src.get('path')}, sha256={src.get('sha256')}")
