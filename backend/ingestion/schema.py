"""Phase 1 source, provision and release contracts."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


Status = Literal["pending", "verified", "rejected"]
Kind = Literal["normative", "annex", "form", "commentary"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Source(StrictModel):
    source_id: str
    path: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    format: Literal["md", "docx", "html", "pdf"]
    source_url: HttpUrl | None = None
    collected_at: date | None = None
    verification_status: Status = "pending"
    extraction_method: str | None = None
    source_role: Literal["body", "annex", "form", "continuation", "alternate", "body_and_forms"] | None = None


class Document(StrictModel):
    doc_id: str
    doc_number: str
    title: str
    doc_type: str
    issued_date: date | None = None
    valid_from: date | None = None
    source_refs: list[SourceRef]
    is_quarantined: bool = False

class Operation(StrictModel):
    operation_id: str
    relation_id: str | None = None
    source_clause: str
    source_hash: str | None = None
    target_locator: str | None = None
    target_hash: str | None = None
    verb: Literal["replace", "add", "delete", "renumber", "repeal", "scoped_amendment", "applicability"]
    payload: str | None = None
    payload_source: str | None = None
    ordering: int | None = None
    preconditions: list[str] = Field(default_factory=list)
    effective_from: date | None = None
    effective_to: date | None = None
    population_predicate: str | None = None
    transition_rule: str | None = None
    review_refs: list[str] = Field(default_factory=list)
    review_status: Status = "pending"

    @model_validator(mode="after")
    def validate_operation(self) -> "Operation":
        if self.verb != "applicability" and not self.relation_id:
            raise ValueError("operation requires relation_id unless verb is applicability")
        if self.verb == "applicability":
            if not (self.source_clause and self.source_hash and self.effective_from and self.review_status == "verified"):
                raise ValueError("applicability event missing mandatory fields")
            if self.target_locator and not self.target_hash:
                raise ValueError("applicability event with target requires target_hash")
        return self

class ParsedDocument(StrictModel):
    doc_id: str
    doc_number: str
    title: str
    doc_type: str
    issued_date: date | None = None
    valid_from: date | None = None
    source_ids: list[str]
    aliases: list[str] = Field(default_factory=list)
    verification_status: Status = "pending"


class SourceRef(StrictModel):
    source_id: str
    locator: str
    source_url: HttpUrl | None = None


class ProvisionVersion(StrictModel):
    schema_version: Literal[2] = 2
    provision_id: str
    provision_version_id: str
    doc_id: str
    structural_path: list[str]
    content_kind: Kind
    content: str
    valid_from: date | None = None
    valid_to: date | None = None
    proposed_valid_from: date | None = None
    proposed_valid_to: date | None = None
    verification_status: Status = "pending"
    source_refs: list[SourceRef]
    applied_relation_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_interval(self) -> "ProvisionVersion":
        if self.valid_from and self.valid_to and self.valid_to <= self.valid_from:
            raise ValueError("valid_to must be later than valid_from")
        if self.verification_status == "verified" and self.content_kind == "normative":
            if not self.valid_from or not self.source_refs:
                raise ValueError("verified normative provision requires valid_from and source_refs")
        return self


class Chunk(StrictModel):
    schema_version: Literal[2] = 2
    release_id: str
    chunk_id: str
    provision_id: str
    provision_version_id: str
    doc_id: str
    doc_number: str
    doc_title: str
    doc_type: str
    content_kind: Kind
    structural_path: list[str]
    article_number: str | None = None
    clause_numbers: list[str] = Field(default_factory=list)
    point_letters: list[str] = Field(default_factory=list)
    parent_id: str | None = None
    hierarchy_path: str = ""
    issued_date: date | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    proposed_valid_from: date | None = None
    proposed_valid_to: date | None = None
    verification_status: Status
    content: str
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    content_length: int = Field(ge=0)
    token_count: int | None = Field(default=None, ge=0)
    is_fragment: bool = False
    topic_tags: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef]
    applied_relation_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_chunk(self) -> "Chunk":
        if len(self.content) != self.content_length:
            raise ValueError("content_length mismatch")
        if self.valid_from and self.valid_to and self.valid_to <= self.valid_from:
            raise ValueError("invalid validity interval")
        if self.verification_status == "verified" and self.content_kind == "normative":
            if not self.valid_from or not self.source_refs:
                raise ValueError("verified normative chunk requires validity and source")
        return self


class Relation(StrictModel):
    relation_id: str
    relation_type: Literal["references", "guides", "amends", "supplements", "replaces", "repeals"]
    source_doc_id: str
    source_provision_id: str | None = None
    target_doc_id: str
    target_locators: list[list[str]]
    scope: Literal["document", "provision", "fragment", "unknown"]
    operation: str
    effective_from: date | None = None
    effective_to: date | None = None
    evidence_source_id: str | None = None
    evidence_locator: str | None = None
    review_status: Status = "pending"
    reviewed_by: str | None = None
    reviewed_at: date | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def verified_requires_evidence(self) -> "Relation":
        if self.review_status == "verified":
            if not all([self.effective_from, self.evidence_source_id, self.evidence_locator, self.reviewed_by, self.reviewed_at]):
                raise ValueError("verified relation requires date, evidence and reviewer")
            if self.scope == "unknown":
                raise ValueError("verified relation requires resolved scope")
        return self
