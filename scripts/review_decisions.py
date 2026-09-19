"""Materialize signed decisions only while their exact inputs are unchanged.

Decisions live outside generated registry files. A rebuild may refresh facts but it
must not erase a review or silently carry it across changed source bytes.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject_type: str
    subject_id: str
    review_type: str
    input_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    conclusion: str
    evidence_source_id: str
    evidence_locator: str
    evidence_url: str | None = None
    reviewer: str
    reviewed_at: date
    values: dict = Field(default_factory=dict)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_decision(self):
        if self.subject_type not in {"source", "document"}:
            raise ValueError("unsupported subject_type")
        if self.conclusion not in {"verified", "rejected"}:
            raise ValueError("unsupported conclusion")
        if not all([self.evidence_source_id, self.evidence_locator, self.reviewer]):
            raise ValueError("review requires evidence and reviewer")
        if self.subject_type == "document" and self.review_type == "metadata" and self.conclusion == "verified":
            if not all(self.values.get(key) for key in ("title", "issued_date", "valid_from")):
                raise ValueError("verified metadata requires title, issued_date and valid_from")
        return self


def input_hash(subject: dict, sources: dict[str, dict]) -> str:
    if "source_id" in subject:
        raw = {"source_id": subject["source_id"], "sha256": subject["sha256"]}
    else:
        raw = {"doc_id": subject["doc_id"], "source_hashes": sorted(
            (sid, sources[sid]["sha256"]) for sid in subject["source_ids"])}
    return hashlib.sha256(json.dumps(raw, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def load_decisions(directory: Path) -> list[ReviewDecision]:
    if not directory.exists():
        return []
    return [ReviewDecision.model_validate(json.loads(path.read_text(encoding="utf-8")))
            for path in sorted(directory.glob("*.json"))]


def apply_source_decisions(rows: list[dict], directory: Path) -> list[dict]:
    by_id = {row["source_id"]: row for row in rows}
    for decision in load_decisions(directory):
        if decision.subject_type != "source" or decision.review_type != "identity":
            continue
        row = by_id.get(decision.subject_id)
        if row and input_hash(row, by_id) == decision.input_sha256:
            if decision.evidence_source_id not in by_id:
                continue
            row["verification_status"] = decision.conclusion
    return rows


def apply_document_decisions(rows: list[dict], source_rows: list[dict], directory: Path) -> list[dict]:
    sources = {row["source_id"]: row for row in source_rows}
    by_id = {row["doc_id"]: row for row in rows}
    allowed = {"title", "issued_date", "valid_from", "aliases"}
    for decision in load_decisions(directory):
        if decision.subject_type != "document" or decision.review_type != "metadata":
            continue
        row = by_id.get(decision.subject_id)
        if not row or input_hash(row, sources) != decision.input_sha256:
            continue
        if decision.evidence_source_id not in row["source_ids"]:
            continue
        if not set(decision.values) <= allowed:
            raise ValueError("document decision has unsupported fields")
        row.update(decision.values)
        row["verification_status"] = decision.conclusion
    return rows
