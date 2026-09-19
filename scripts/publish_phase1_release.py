"""Publish an immutable internal Phase 1 snapshot only after Gate 1 passes."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

from scripts.audit_gate1 import REGISTRY, ROOT, STAGE, audit


RELEASES = ROOT / "data/releases"
POINTER = ROOT / "data/active_release.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    os.replace(temporary, path)


def publish() -> dict:
    gate = audit()
    if gate["gate1"] != "PASS":
        raise RuntimeError(f"Gate 1 is {gate['gate1']}: {gate['blockers']}")
    candidate = json.loads((STAGE / "manifest.json").read_text(encoding="utf-8"))
    coverage = json.loads((REGISTRY / "coverage.json").read_text(encoding="utf-8"))
    dates = {row["target_as_of"] for row in coverage}
    if len(dates) != 1 or any(row["verification_status"] != "verified" for row in coverage):
        raise RuntimeError("Coverage has no single verified target date")
    release_id = candidate["release_id"].replace("candidate-", "phase1-")
    target = RELEASES / release_id
    if target.exists():
        raise FileExistsError(f"Immutable release already exists: {target}")
    RELEASES.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{release_id}.", dir=RELEASES))
    try:
        files = [STAGE / name for name in ("parsed.json", "chunks.jsonl", "provision_versions.jsonl", "quarantine.json")]
        files += [REGISTRY / name for name in ("sources.json", "documents.json", "coverage.json",
                                               "relations_verified.json", "source_selection.json")]
        files += [ROOT / "reports/phase1-closeout/source_reconciliation.json",
                  ROOT / "reports/phase1-implementation/review_queue.json"]
        file_hashes = {}
        for path in files:
            dest = temporary / path.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            if sha256(path) != sha256(dest):
                raise RuntimeError(f"Snapshot copy mismatch: {path}")
            file_hashes[path.relative_to(ROOT).as_posix()] = sha256(dest)
        reviews = REGISTRY / "reviews"
        if reviews.exists():
            for path in sorted(reviews.glob("*.json")):
                dest = temporary / path.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
                file_hashes[path.relative_to(ROOT).as_posix()] = sha256(dest)
        manifest = {**candidate, "release_id": release_id, "status": "verified", "published": True,
                    "verified_as_of": dates.pop(), "gate1": "PASS", "snapshot_file_sha256": file_hashes}
        atomic_json(temporary / "manifest.json", manifest)
        temporary.rename(target)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    pointer = {"release_id": release_id, "path": target.relative_to(ROOT).as_posix(),
               "manifest_sha256": sha256(target / "manifest.json")}
    atomic_json(POINTER, pointer)
    return pointer


if __name__ == "__main__":
    print(json.dumps(publish(), ensure_ascii=False))
