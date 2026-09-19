import hashlib

import pytest
from pydantic import ValidationError

import scripts.review_decisions as reviews
from scripts.review_decisions import ReviewDecision, apply_document_decisions, input_hash


def test_review_requires_evidence_and_reviewer():
    with pytest.raises(ValidationError):
        ReviewDecision.model_validate({
            "subject_type": "document", "subject_id": "doc:test", "review_type": "metadata",
            "input_sha256": "a" * 64, "conclusion": "verified", "evidence_source_id": "src:a",
            "evidence_locator": "", "reviewer": "", "reviewed_at": "2026-09-17"})


def test_rebuild_applies_only_hash_bound_metadata_decision(monkeypatch):
    sources = [{"source_id": "src:a", "sha256": "a" * 64}]
    document = {"doc_id": "doc:test", "source_ids": ["src:a"], "title": "test", "verification_status": "pending"}
    decision = {
        "subject_type": "document", "subject_id": "doc:test", "review_type": "metadata",
        "input_sha256": input_hash(document, {"src:a": sources[0]}),
        "conclusion": "verified", "evidence_source_id": "src:a", "evidence_locator": "article:1",
        "reviewer": "reviewer", "reviewed_at": "2026-09-17", "values": {
            "title": "reviewed title", "issued_date": "2020-12-14", "valid_from": "2021-02-01"},
    }
    monkeypatch.setattr(reviews, "load_decisions", lambda _: [ReviewDecision.model_validate(decision)])
    assert apply_document_decisions([document.copy()], sources, None)[0]["title"] == "reviewed title"
    changed = [{**sources[0], "sha256": hashlib.sha256(b"changed").hexdigest()}]
    stale = apply_document_decisions([document.copy()], changed, None)[0]
    assert stale["title"] == "test"
    assert stale["verification_status"] == "pending"
