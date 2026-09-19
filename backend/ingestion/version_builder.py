"""Build traceable base provision candidates without inferring legal currency."""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from typing import Any

from backend.ingestion.schema import ProvisionVersion


def base_versions(parsed: dict[str, dict[str, Any]], chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_version: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for chunk in chunks:
        by_version[chunk["provision_version_id"]].append(chunk)

    versions = []
    seen_version_ids = set()
    for doc_id, document in sorted(parsed.items()):
        for article in document["articles"]:
            path = article["structural_path"]
            provision_id = f"{doc_id}:{'/'.join(path)}"
            content = article["content"]
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            version_id = f"{provision_id}@{digest[:16]}"
            
            if version_id in seen_version_ids:
                continue
            seen_version_ids.add(version_id)
            
            members = by_version.pop(version_id, None)
            if not members or any(row["provision_id"] != provision_id for row in members):
                raise ValueError(f"Missing or mismatched chunks for {version_id}")
            refs = list({(ref["source_id"], ref["locator"], ref.get("source_url")): ref
                         for row in members for ref in row["source_refs"]}.values())
            if not refs:
                raise ValueError(f"No source provenance for {version_id}")
            versions.append(ProvisionVersion.model_validate({
                "provision_id": provision_id,
                "provision_version_id": version_id,
                "doc_id": doc_id,
                "structural_path": path,
                "content_kind": article["content_kind"],
                "content": content,
                "valid_from": members[0].get("valid_from"),
                "valid_to": members[0].get("valid_to"),
                "proposed_valid_from": members[0].get("proposed_valid_from"),
                "proposed_valid_to": members[0].get("proposed_valid_to"),
                "verification_status": "pending",
                "source_refs": refs,
                "applied_relation_ids": [],
            }).model_dump(mode="json"))
    if by_version:
        raise ValueError(f"Orphan chunks without a base provision: {len(by_version)}")
    return versions

def extract_payload(text: str) -> str:
    match = re.search(r'như sau:\s*[\n]*\s*[“\x22](.*?)[”\x22]?\s*$', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text

def split_payload(content: str, base_path: list[str]) -> list[tuple[list[str], str]]:
    CLAUSE = re.compile(r"^(\d+)\.\s")
    POINT = re.compile(r"^([a-zđ])\)\s", re.I)
    
    lines = content.splitlines()
    sub_provisions = []
    
    current_path = list(base_path)
    current_content = []
    
    for line in lines:
        clause_match = CLAUSE.match(line)
        point_match = POINT.match(line)
        
        if clause_match:
            if current_content:
                sub_provisions.append((current_path, "\n".join(current_content)))
            current_path = list(base_path) + [f"item:{clause_match.group(1)}"]
            current_content = [line]
        elif point_match and len(current_path) >= len(base_path):
            if current_content:
                sub_provisions.append((current_path, "\n".join(current_content)))
            if current_path[-1].startswith("item:"):
                current_path = current_path + [f"point:{point_match.group(1).lower()}"]
            else:
                current_path = current_path[:-1] + [f"point:{point_match.group(1).lower()}"]
            current_content = [line]
        else:
            current_content.append(line)
            
    if current_content:
        sub_provisions.append((current_path, "\n".join(current_content)))
        
    return sub_provisions

def materialize_versions(
    input_versions: list[dict[str, Any]], operations: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Apply verified operations to base versions, producing a materialized timeline.

    Guards:
    - Only applies ops with review_status == "verified".
    - Rejects ops with review_status "verified" but source_hash or target_hash == "unknown"
      (unverifiable provenance must not enter the production corpus).
    - Uses op.get("operation_id", "<no id>") throughout to avoid KeyError on mock ops.
    """
    # Guard: reject verified ops with unknown provenance hashes
    provenance_violations = [
        op.get("operation_id", "<no id>") for op in operations
        if op.get("review_status") == "verified"
        and (op.get("source_hash") == "unknown" or op.get("target_hash") == "unknown")
    ]
    if provenance_violations:
        raise ValueError(
            f"Cannot materialize: operations marked verified but have unknown source/target hash "
            f"(provenance not established): {provenance_violations}"
        )

    materialized = list(input_versions)

    ops = [op for op in operations if op.get("review_status") == "verified"]
    ops.sort(key=lambda x: (x.get("effective_from") or "", x.get("operation_id", "")))

    for op in ops:
        op_id = op.get("operation_id", "<no id>")
        target_locator = op.get("target_locator")
        verb = op.get("verb")
        effective_from = op.get("effective_from")
        effective_to = op.get("effective_to")
        relation_id = op.get("relation_id")

        if not effective_from:
            raise ValueError(f"Conflict: Missing effective_from in operation {op_id}")

        target_parts = target_locator.split(":", 2)
        target_doc = target_parts[1] if len(target_parts) > 1 else target_locator
        target_path_parts = target_parts[2].split("/") if len(target_parts) > 2 else []

        is_document_scope = len(target_path_parts) == 0 or (
            len(target_path_parts) == 1 and target_path_parts[0] == "body"
        )

        found = False
        new_versions = []
        payload_inserted = False

        for v in materialized:
            if v["doc_id"] != f"doc:{target_doc}":
                continue

            v_to = v.get("valid_to")
            if v_to and v_to <= effective_from:
                continue

            match = False
            if is_document_scope:
                match = True
            else:
                v_path = v.get("structural_path", [])
                if len(target_path_parts) <= len(v_path) and v_path[:len(target_path_parts)] == target_path_parts:
                    match = True

            if match:
                found = True

                if verb == "applicability":
                    # applicability sets a proposed effective date but does NOT
                    # change the content timeline. Record on proposed_valid_from only;
                    # do not overwrite valid_from which is determined by legal chain review.
                    v["proposed_valid_from"] = effective_from
                else:
                    v["valid_to"] = effective_from

                    if verb in ["replace", "scoped_amendment", "add"] and not payload_inserted:
                        payload = op.get("payload")
                        if payload is None and verb == "replace":
                            source_clause = op.get("source_clause")
                            if source_clause:
                                src_parts = source_clause.split(":", 2)
                                src_doc = f"doc:{src_parts[1]}" if len(src_parts) > 1 else source_clause
                                src_path = src_parts[2].split("/") if len(src_parts) > 2 else []
                                payloads = []
                                for src_v in input_versions:
                                    if (src_v["doc_id"] == src_doc
                                            and src_v.get("structural_path", [])[:len(src_path)] == src_path):
                                        payloads.append(extract_payload(src_v["content"]))
                                if payloads:
                                    payload = "\n".join(payloads)

                        if payload is None:
                            payload = v["content"]

                        # If replacing a broad target (article level), split the payload
                        if len(target_path_parts) <= 2:
                            sub_provs = split_payload(payload, target_path_parts)
                        else:
                            # Direct replacement of a specific point/item
                            sub_provs = [(target_path_parts, payload)]

                        for sub_path, sub_content in sub_provs:
                            new_v = dict(v)
                            new_v["structural_path"] = sub_path
                            new_v["provision_id"] = f"{new_v['doc_id']}:{'/'.join(sub_path)}"
                            new_v["valid_from"] = effective_from
                            new_v["valid_to"] = effective_to
                            if relation_id:
                                new_v["applied_relation_ids"] = list(new_v.get("applied_relation_ids", [])) + [relation_id]

                            new_v["content"] = sub_content
                            digest = hashlib.sha256(sub_content.encode("utf-8")).hexdigest()
                            new_v["provision_version_id"] = f"{new_v['provision_id']}@{digest[:16]}"
                            new_versions.append(new_v)

                        payload_inserted = True

        if not found:
            raise ValueError(
                f"Conflict: Target {target_locator} not found or not active at {effective_from} "
                f"for op {op_id}"
            )

        materialized.extend(new_versions)

    # Filter out zero-length intermediate versions created when multiple ops apply on the same day
    materialized = [
        v for v in materialized
        if not (v.get("valid_from") and v.get("valid_to") and v["valid_from"] == v["valid_to"])
    ]

    return materialized
