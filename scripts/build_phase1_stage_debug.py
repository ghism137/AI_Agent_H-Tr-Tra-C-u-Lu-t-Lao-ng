"""Build a deterministic, unpublished Phase 1 candidate snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from backend.ingestion.chunker_v2 import chunk_articles
from backend.ingestion.docx_extractor import extract_docx
from backend.ingestion.html_extractor import extract_government_html
from backend.ingestion.pdf_text_extractor import extract_pdf_text
from backend.ingestion.parser import parse_legal_document
from backend.ingestion.parser import parse_legal_document
from backend.ingestion.version_builder import base_versions, materialize_versions
ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "registry"
STAGE = ROOT / "data" / "staging" / "phase1-candidate"


def candidate_fingerprint() -> tuple[str, str]:
    parser_files = [ROOT / path for path in (
        "backend/ingestion/parser.py", "backend/ingestion/chunker_v2.py",
        "backend/ingestion/docx_extractor.py", "backend/ingestion/html_extractor.py",
        "backend/ingestion/pdf_text_extractor.py", "scripts/build_phase1_stage.py",
        "backend/ingestion/version_builder.py",
    )]
    code_sha256 = hashlib.sha256(b"".join(path.read_bytes() for path in parser_files)).hexdigest()
    fingerprint = hashlib.sha256((REGISTRY / "sources.json").read_bytes() + (REGISTRY / "documents.json").read_bytes()
                                 + (REGISTRY / "coverage.json").read_bytes() +
                                 (REGISTRY / "source_selection.json").read_bytes() +
                                 (REGISTRY / "relations_verified.json").read_bytes() + code_sha256.encode()).hexdigest()[:16]
    return f"candidate-{fingerprint}", code_sha256


def main() -> None:
    sources = {item["source_id"]: item for item in json.loads((REGISTRY / "sources.json").read_text(encoding="utf-8"))}
    documents = json.loads((REGISTRY / "documents.json").read_text(encoding="utf-8"))
    coverage = json.loads((REGISTRY / "coverage.json").read_text(encoding="utf-8"))
    source_selection = json.loads((REGISTRY / "source_selection.json").read_text(encoding="utf-8"))
    sources_by_path = {item["path"]: item for item in sources.values()}
    release_id, code_sha256 = candidate_fingerprint()
    relation_sha256 = hashlib.sha256((REGISTRY / "relations_verified.json").read_bytes()).hexdigest()
    parsed: dict[str, dict] = {}
    chunks: list[dict] = []
    quarantine = []
    for document in sorted(documents, key=lambda item: item["doc_id"]):
        selection = source_selection.get(document["doc_id"])
        official_html = [sources[source_id] for source_id in document["source_ids"]
                         if sources[source_id]["format"] == "html" and sources[source_id]["source_url"]]
        text_pdf = [sources[source_id] for source_id in document["source_ids"]
                    if "-congbao" in sources[source_id]["path"] and sources[source_id]["format"] == "pdf"]
        supplemental_pdf = []
        if document["doc_number"] == "188/2025/NĐ-CP":
            supplemental_pdf = [item for item in text_pdf if item["path"].endswith("-part2.pdf")]
            text_pdf = [item for item in text_pdf if item["path"].endswith("-part1.pdf")]
        variants = [sources[source_id] for source_id in document["source_ids"] if sources[source_id]["format"] == "docx"]
        body = text_pdf or official_html or [source for source in variants if source["path"].rsplit("/", 1)[-1].lower().startswith(("luật", "bộ-luật", "nghị-định", "thông-tư", "quyết-định"))]
        if selection:
            body = [sources_by_path[selection["body"]]]
            if body[0]["source_id"] not in document["source_ids"]:
                raise ValueError(f"Selected body is not registered for {document['doc_id']}")
        body = sorted(body, key=lambda item: item["path"])
        equivalent_sources = []
        if len(body) > 1 and all(source["format"] == "docx" for source in body):
            extracted = [(source, extract_docx(ROOT / source["path"])) for source in body]
            texts = [[block.get("text", block.get("rows")) for block in blocks] for _, blocks in extracted]
            if all(text == texts[0] for text in texts[1:]):
                equivalent_sources = [item[0] for item in extracted[1:]]
                body = [extracted[0][0]]
        if len(body) != 1:
            quarantine.append({"doc_id": document["doc_id"], "reason": "body_source_missing_or_ambiguous", "candidates": [item["path"] for item in body]})
            continue
        source = body[0]
        try:
            if source["format"] == "html":
                blocks = extract_government_html(ROOT / source["path"])
            elif source["format"] == "pdf":
                page_intervals = {
                    "45/2019/QH14": (3, 95), "41/2024/QH15": (3, 90),
                    "71/2025/QH15": (39, 69),
                    "113/2025/QH15": (93, 107),
                    "124/2025/QH15": (84, 108),
                    "73/2025/QH15": (57, 75), "84/2025/QH15": (4, 44),
                    "142/2025/QH15": (41, 100), "162/2026/NĐ-CP": (10, 14),
                    "61/2020/NĐ-CP": (1, 21), "75/2024/NĐ-CP": (1, 6),
                    "42/2023/NĐ-CP": (1, 6),
                    "108/2021/NĐ-CP": (1, 7),
                    "44/2019/NĐ-CP": (1, 4),
                    "146/2018/NĐ-CP": (1, 57),
                    "104/2022/NĐ-CP": (1, 13),
                    "75/2023/NĐ-CP": (1, 19),
                    "74/2025/NĐ-CP": (1, 18),
                    "46/2014/QH13": (1, 14),
                    "02/2025/NĐ-CP": (1, 9),
                    "70/2015/NĐ-CP": (1, 16),
                    "32/2013/QH13": (1, 11),
                    "97/2015/QH13": (1, 30),
                    "35/2018/QH14": (1, 77),
                    "68/2020/QH14": (1, 27),
                    "30/2023/QH15": (1, 17),
                    "74/2025/QH15": (29, 55), "293/2025/NĐ-CP": (1, 17),
                    "374/2025/NĐ-CP": (2, 98),
                    "188/2025/NĐ-CP": (1, 97),
                    "219/2025/NĐ-CP": (2, 37),
                }
                first_page, last_page = page_intervals[document["doc_number"]]
                blocks = extract_pdf_text(ROOT / source["path"], first_page=first_page, last_page=last_page)
            else:
                blocks = extract_docx(ROOT / source["path"])
            metadata = {
                "doc_id": document["doc_id"], "doc_number": document["doc_number"],
                "doc_title": document["title"], "doc_type": document["doc_type"],
                "content_kind": "normative", "issued_date": document.get("issued_date"),
                "valid_from": document.get("valid_from"), "verification_status": document.get("verification_status", "pending"),
            }
            result = parse_legal_document("", metadata, blocks)
            article_numbers = [int(article["article_number"]) for article in result["articles"]
                               if article["content_kind"] == "normative" and article["article_number"].isdigit()]
            if (not article_numbers or len(article_numbers) != len(set(article_numbers))
                    or article_numbers != list(range(1, max(article_numbers) + 1))):
                raise ValueError("normative article sequence is incomplete or missing")
            new_chunks = chunk_articles(result, release_id=release_id, source_id=source["source_id"], source_url=source["source_url"])
            for chunk in new_chunks:
                original_refs = list(chunk["source_refs"])
                for equivalent in equivalent_sources:
                    chunk["source_refs"].extend({"source_id": equivalent["source_id"],
                                                 "source_url": equivalent["source_url"], "locator": ref["locator"]}
                                                for ref in original_refs)
            supplemental = [item for item in variants if item["source_id"] not in {source["source_id"], *(entry["source_id"] for entry in equivalent_sources)}
                            and item["path"].rsplit("/", 1)[-1].lower().startswith(("mau ", "phu "))]
            for artifact in sorted(supplemental, key=lambda item: item["path"]):
                artifact_kind = "form" if artifact["path"].rsplit("/", 1)[-1].lower().startswith("mau ") else "annex"
                artifact_meta = {**metadata, "content_kind": artifact_kind}
                artifact_parsed = parse_legal_document("", artifact_meta, extract_docx(ROOT / artifact["path"]))
                for part_number, article in enumerate(artifact_parsed["articles"], 1):
                    article["structural_path"] = [artifact_kind, artifact["source_id"], f"item:{part_number}"]
                result["articles"].extend(artifact_parsed["articles"])
                new_chunks.extend(chunk_articles(artifact_parsed, release_id=release_id,
                                                source_id=artifact["source_id"], source_url=artifact["source_url"]))
            continuation = [sources_by_path[path] for path in selection.get("continuation", [])] if selection else supplemental_pdf
            for artifact in continuation:
                artifact_meta = {**metadata, "content_kind": "form"}
                if artifact["source_id"] not in document["source_ids"]:
                    raise ValueError(f"Selected continuation is not registered for {document['doc_id']}")
                artifact_blocks = (extract_docx(ROOT / artifact["path"]) if artifact["format"] == "docx" else
                                   extract_pdf_text(ROOT / artifact["path"], first_page=3, last_page=20))
                artifact_parsed = parse_legal_document("", artifact_meta, artifact_blocks)
                for part_number, article in enumerate(artifact_parsed["articles"], 1):
                    article["structural_path"] = ["form", artifact["source_id"], f"item:{part_number}"]
                result["articles"].extend(artifact_parsed["articles"])
                new_chunks.extend(chunk_articles(artifact_parsed, release_id=release_id,
                                                source_id=artifact["source_id"], source_url=artifact["source_url"]))
            parsed[document["doc_id"]] = result
            chunks.extend(new_chunks)
        except (ValueError, KeyError, OSError) as error:
            quarantine.append({"doc_id": document["doc_id"], "source": source["path"], "reason": str(error)})
    ids = [item["chunk_id"] for item in chunks]
    if len(ids) != len(set(ids)):
        raise ValueError("Corpus chunk ID collision")
    versions = base_versions(parsed, chunks)
    print('Total versions:', len(versions))
    doc146_versions = [v for v in versions if v['doc_id'] == 'doc:146/2018/NĐ-CP']
    print('doc146_versions count:', len(doc146_versions))
    if doc146_versions:
        paths = ['/'.join(v['structural_path']) for v in doc146_versions if 'article:14' in v['structural_path']]
        print('Paths for article 14:', paths)
        print('valid_from:', doc146_versions[0].get('valid_from'))
        print('valid_to:', doc146_versions[0].get('valid_to'))
    else:
        print('NO VERSIONS FOUND FOR doc:146/2018/NĐ-CP!')
    sys.exit(0)
    
    operations_path = REGISTRY / "operations.json"
    operations = []
    gate3 = "PASS"
    if operations_path.exists():
        operations = json.loads(operations_path.read_text(encoding="utf-8"))
        for op in operations:
            if op.get("review_status") != "verified":
                gate3 = "FAIL"
                break
                
    try:
        versions = materialize_versions(versions, operations)
    except Exception as e:
        print(f"Materialization failed: {e}")
        gate3 = "FAIL"
        raise
    
    missing = [item["doc_number"] for item in coverage if f"doc:{item['doc_number']}" not in parsed]
    gate1 = "PASS" if len(quarantine) == 0 and len(missing) == 0 else "FAIL"
    gate2 = "FAIL"
    legal_verification_path = REGISTRY / "legal_verification.json"
    if legal_verification_path.exists():
        try:
            legal_data = json.loads(legal_verification_path.read_text(encoding="utf-8"))
            if legal_data.get("status") == "PASS":
                gate2 = "PASS"
        except Exception:
            pass

    
    manifest = {"release_id": release_id, "status": "candidate", "published": False,
                "sources_sha256": hashlib.sha256((REGISTRY / "sources.json").read_bytes()).hexdigest(),
                "parser_code_sha256": code_sha256, "verified_relations_sha256": relation_sha256,
                "schema_version": 2, "documents_parsed": len(parsed), "chunks": len(chunks),
                "provision_versions": len(versions),
                "quarantined_documents": len(quarantine), "missing_required_parsed_documents": missing,
                "verified_as_of": None, "gate1": gate1, "gate2": gate2, "gate3": gate3}
    STAGE.mkdir(parents=True, exist_ok=True)
    (STAGE / "parsed.json").write_text(json.dumps(parsed, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    (STAGE / "chunks.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in chunks), encoding="utf-8")
    (STAGE / "provision_versions.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in versions), encoding="utf-8")
    (STAGE / "quarantine.json").write_text(json.dumps(quarantine, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (STAGE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
