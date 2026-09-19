"""Q3 Before/after reconciliation: corpus count deltas and invariant checks.

Run after rebuild to validate corpus integrity.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "data/staging/phase1-candidate"
REGISTRY = ROOT / "data/registry"

BEFORE = {
    "documents_parsed": 61,
    "chunks": 20416,
    "provision_versions": 20340,
    "quarantined_documents": 0,
    "versions_with_applied_relation_ids": 22,
    "gate1": "PASS",
    "gate2": "PASS",
    "gate3": "PASS",
}

print("=" * 70)
print("Q3 CORPUS RECONCILIATION REPORT")
print("=" * 70)

# Load after state
manifest = json.loads((STAGE / "manifest.json").read_text("utf-8"))

with open(STAGE / "chunks.jsonl", encoding="utf-8") as f:
    chunk_lines = [l for l in f if l.strip()]
with open(STAGE / "provision_versions.jsonl", encoding="utf-8") as f:
    version_lines = [l for l in f if l.strip()]

chunks = [json.loads(l) for l in chunk_lines]
versions = [json.loads(l) for l in version_lines]

print("\n--- BEFORE/AFTER DELTA ---")
after = {
    "documents_parsed": manifest["documents_parsed"],
    "chunks": manifest["chunks"],
    "provision_versions": manifest["provision_versions"],
    "quarantined_documents": manifest["quarantined_documents"],
    "versions_with_applied_relation_ids": len([v for v in versions if v.get("applied_relation_ids")]),
    "gate1": manifest["gate1"],
    "gate2": manifest["gate2"],
    "gate3": manifest["gate3"],
}

for key in BEFORE:
    b = BEFORE[key]
    a = after[key]
    delta = ""
    if isinstance(b, int) and isinstance(a, int):
        d = a - b
        delta = f" (delta: {d:+d})"
    same = " ✓" if b == a else " ← CHANGED"
    print(f"  {key}: {b} → {a}{delta}{same}")

print("\n--- CHANGE EXPLANATIONS ---")
# Explain expected changes
print("  Expected changes:")
print("  - versions_with_applied_relation_ids: was 22 (stubs materialized), now should be 0")
print("    Reason: 13 stub applicability ops downgraded to pending, 2 replace ops blocked.")
print("    materialize_versions only applies verified ops without unknown hashes.")
print("  - chunks/provision_versions: may differ due to stubs not being applied")

# Unexpected changes investigation
delta_chunks = after["chunks"] - BEFORE["chunks"]
delta_versions = after["provision_versions"] - BEFORE["provision_versions"]

if delta_chunks != 0:
    print(f"\n  INVESTIGATE: chunk count changed by {delta_chunks:+d}")
    print("  This may indicate parser or chunker behavior change after code fixes.")

if delta_versions != 0:
    print(f"\n  INVESTIGATE: provision_version count changed by {delta_versions:+d}")

print("\n--- CORPUS INVARIANTS ---")
invariant_failures = []

# Invariant 1: Zero materialized stubs
stubs_materialized = [v for v in versions if v.get("applied_relation_ids")]
# Check each applied_relation_id corresponds to a non-stub, non-blocked op
ops = json.loads((REGISTRY / "operations.json").read_text("utf-8"))
blocked_pending_ids = {op.get("relation_id") for op in ops if op.get("review_status") in ("blocked", "pending")}
stub_contamination = [
    v["provision_id"] for v in stubs_materialized
    if any(rid in blocked_pending_ids for rid in v.get("applied_relation_ids", []))
]
if stub_contamination:
    invariant_failures.append(f"FAIL: {len(stub_contamination)} versions materialized from blocked/pending ops: {stub_contamination[:3]}")
    print(f"  [FAIL] Zero stub materialization: {len(stub_contamination)} violations")
else:
    print(f"  [PASS] Zero materialized stubs: no blocked/pending ops in applied_relation_ids")

# Invariant 2: No orphan chunks (all chunks must have corresponding provision_version)
chunk_version_ids = {c["provision_version_id"] for c in chunks}
version_ids_set = {v["provision_version_id"] for v in versions}
orphan_chunks = chunk_version_ids - version_ids_set
if orphan_chunks:
    invariant_failures.append(f"FAIL: {len(orphan_chunks)} orphan chunks (chunk.provision_version_id not in versions)")
    print(f"  [FAIL] No orphan chunks: {len(orphan_chunks)} orphans")
    for oc in list(orphan_chunks)[:3]:
        print(f"    orphan: {oc}")
else:
    print(f"  [PASS] No orphan chunks: all chunk.provision_version_ids match versions")

# Invariant 3: No duplicate canonical article numbers within a document
doc_articles: dict[str, set] = {}
dup_canonical = []
for v in versions:
    doc_id = v.get("doc_id", "")
    path = v.get("structural_path", [])
    if len(path) == 2 and path[0] == "body" and path[1].startswith("article:"):
        if doc_id not in doc_articles:
            doc_articles[doc_id] = set()
        art_num = path[1]
        if art_num in doc_articles[doc_id]:
            dup_canonical.append(f"{doc_id}:{art_num}")
        doc_articles[doc_id].add(art_num)

if dup_canonical:
    invariant_failures.append(f"FAIL: {len(dup_canonical)} duplicate canonical articles")
    print(f"  [FAIL] No duplicate canonical articles: {len(dup_canonical)} dupes")
    for d in dup_canonical[:5]:
        print(f"    dup: {d}")
else:
    print(f"  [PASS] No duplicate canonical articles across {len(doc_articles)} documents")

# Invariant 4: Valid source references (every chunk must have source_id matching sources.json)
sources = json.loads((REGISTRY / "sources.json").read_text("utf-8"))
valid_src_ids = {s["source_id"] for s in sources}
invalid_src_refs = [c for c in chunks if c.get("source_id") not in valid_src_ids]
if invalid_src_refs:
    invariant_failures.append(f"FAIL: {len(invalid_src_refs)} chunks with invalid source_id")
    print(f"  [FAIL] Valid source references: {len(invalid_src_refs)} invalid")
else:
    print(f"  [PASS] Valid source references: all {len(chunks)} chunks have valid source_id")

# Invariant 5: Manifest/corpus consistency
mismatch = []
if manifest["chunks"] != len(chunks):
    mismatch.append(f"manifest.chunks={manifest['chunks']} != actual={len(chunks)}")
if manifest["provision_versions"] != len(versions):
    mismatch.append(f"manifest.provision_versions={manifest['provision_versions']} != actual={len(versions)}")
if mismatch:
    invariant_failures.append(f"FAIL: manifest/corpus mismatch: {mismatch}")
    print(f"  [FAIL] Manifest/corpus consistency: {mismatch}")
else:
    print(f"  [PASS] Manifest/corpus consistency: counts match")

# Invariant 6: Deterministic rebuild detection
print(f"\n--- DETERMINISM CHECK ---")
print(f"  release_id: {manifest['release_id']}")
print(f"  sources_sha256: {manifest['sources_sha256'][:16]}...")
print(f"  parser_code_sha256: {manifest['parser_code_sha256'][:16]}...")
print(f"  verified_relations_sha256: {manifest['verified_relations_sha256'][:16]}...")
print(f"  operations_sha256: {manifest.get('operations_sha256', 'ABSENT')[:16] if manifest.get('operations_sha256') else 'ABSENT'}...")
print(f"  (Second rebuild with same inputs must produce identical release_id and counts)")

print("\n--- SUMMARY ---")
if not invariant_failures:
    print("  ALL INVARIANTS PASS")
else:
    print(f"  {len(invariant_failures)} INVARIANT FAILURES:")
    for f in invariant_failures:
        print(f"    {f}")

print(f"\n  Gates: gate1={manifest['gate1']}, gate2={manifest['gate2']}, gate3={manifest['gate3']}")
