"""Fix operations.json: downgrade stubs and block invalid ops with real evidence.

Changes:
- op-nd74-4-5: blocked (target locator doc:146/2018/ND-CP:article:14/item:5/point:a not in parsed corpus)
- op-nd02-1-1: blocked (payload does not match source clause content, provenance contract violated)
- 13 applicability stubs: downgraded from verified to pending
- All changes preserve audit trail (no records deleted)
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPS_PATH = ROOT / "data/registry/operations.json"

ops = json.loads(OPS_PATH.read_text("utf-8"))

DOWNGRADE_TS = "2026-09-19T23:20:00+07:00"

# Real source clause hashes computed from parsed corpus (2026-09-19 verification)
OP_PROVENANCE = {
    "op-nd74-4-5": {
        "real_source_clause_hash": "4d1e12cb78edd1025d7e0ccc90eb8843ed505dfda5ef6fc6bf5a508a91552134",
        "source_file_sha256": "c181cbb10136dc9e856e45e1134487d5d77278179308b7552da48dc322511d4d",
        "source_file_path": "data/raw/official/74-2025-ND-CP-congbao.pdf",
    },
    "op-nd02-1-1": {
        "real_source_clause_hash": "8d08c35d591a088e59caf51756913258c4f6471df5bc8905771dddbbf1a98a1f",
        "source_file_sha256": "e7d5d66154cd8f43c0d7ac441e312d9511cfc2dac0005e3fcebf58048a0d9072",
        "source_file_path": "data/raw/official/02-2025-ND-CP-congbao.pdf",
    },
}

updated_ops = []
changes = []

for op in ops:
    op_id = op.get("operation_id", "")
    verb = op.get("verb", "")
    notes = op.get("notes", "")

    if op_id == "op-nd74-4-5":
        # Source file and clause exist but target locator not resolvable in parsed corpus
        prov = OP_PROVENANCE[op_id]
        op["review_status"] = "blocked"
        op["source_hash"] = prov["real_source_clause_hash"]
        # target_hash stays unknown - cannot be computed as target not in corpus
        op["block_reason"] = (
            "Target locator doc:146/2018/ND-CP:body/article:14/item:5/point:a not found "
            "in parsed corpus of ND 146/2018. Parsed corpus has article:14 with items but no "
            "point:a sub-provision. Cannot materialize replace without verified target. "
            "Source clause and file verified (source_hash populated)."
        )
        op["block_evidence"] = {
            "source_file": prov["source_file_path"],
            "source_file_sha256": prov["source_file_sha256"],
            "source_clause_hash_verified": prov["real_source_clause_hash"],
            "target_resolution": "FAILED - not in parsed corpus",
            "verified_at": DOWNGRADE_TS,
            "verified_by": "builder:sonnet-4.6",
        }
        op["blocked_at"] = DOWNGRADE_TS
        changes.append(f"BLOCKED: {op_id} - target not resolvable")

    elif op_id == "op-nd02-1-1":
        # Source file and clause exist but payload content does not match source clause
        prov = OP_PROVENANCE[op_id]
        op["review_status"] = "blocked"
        op["source_hash"] = prov["real_source_clause_hash"]
        # Keep payload as audit evidence but mark blocked
        op["block_reason"] = (
            "Payload mismatch: source_clause doc:02/2025/ND-CP:body/article:1/item:1 resolves to "
            "text about BHYT card presentation requirements. Inline payload contains full text of "
            "Dieu 14 ND 146/2018 (co che huong BHYT) - this is the target document content, not "
            "derived from the source clause. A replace operation must derive new text from source "
            "clause, not embed target text. Legal review required to identify correct source clause "
            "for the replacement payload."
        )
        op["block_evidence"] = {
            "source_file": prov["source_file_path"],
            "source_file_sha256": prov["source_file_sha256"],
            "source_clause_hash_verified": prov["real_source_clause_hash"],
            "source_clause_content_preview": "Nguoi tham gia bao hiem y te khi kham benh...",
            "payload_content_preview": "Dieu 14. Muc huong bao hiem y te...",
            "mismatch_type": "payload_is_target_text_not_source_derived",
            "verified_at": DOWNGRADE_TS,
            "verified_by": "builder:sonnet-4.6",
        }
        op["blocked_at"] = DOWNGRADE_TS
        changes.append(f"BLOCKED: {op_id} - payload provenance mismatch")

    elif verb == "applicability" and notes == "Stubbed to satisfy completeness check":
        # Downgrade all stubs from verified to pending
        op["review_status"] = "pending"
        op["downgrade_reason"] = (
            "Downgraded from verified: stub created to satisfy gate completeness check. "
            "source_hash and target_hash are unknown (no real provenance). "
            "Requires legal review with actual source clause and hash verification."
        )
        op["downgraded_at"] = DOWNGRADE_TS
        op["downgraded_by"] = "builder:sonnet-4.6"
        changes.append(f"PENDING: {op_id} (stub downgraded)")

    updated_ops.append(op)

# Write back
OPS_PATH.write_text(json.dumps(updated_ops, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"operations.json updated: {len(changes)} changes")
for c in changes:
    print(f"  {c}")

# Verify: no operations should have review_status=verified AND source_hash=unknown
violations = [
    op.get("operation_id") for op in updated_ops
    if op.get("review_status") == "verified"
    and (op.get("source_hash") == "unknown" or op.get("target_hash") == "unknown")
]
if violations:
    print(f"ERROR: Still have verified+unknown ops: {violations}")
else:
    print("VERIFICATION PASS: No verified operations with unknown hashes")

# Summary
status_counts = {}
for op in updated_ops:
    s = op.get("review_status", "unknown")
    status_counts[s] = status_counts.get(s, 0) + 1
print(f"Status summary: {status_counts}")
