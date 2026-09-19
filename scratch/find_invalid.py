import json
import hashlib
import uuid
import datetime
import traceback

from pydantic_core import ValidationError
from backend.ingestion import version_builder
from backend.ingestion.schema import Chunk

with open("data/staging/phase1-candidate/parsed.json", "r", encoding="utf-8") as f:
    parsed = json.load(f)

chunks = []
with open("data/staging/phase1-candidate/chunks.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        chunks.append(json.loads(line))

bv = version_builder.base_versions(parsed, chunks)

with open("data/registry/operations.json", "r", encoding="utf-8") as f:
    ops = json.load(f)

versions = version_builder.materialize_versions(bv, ops)

for v in versions:
    if v.get("valid_from") and v.get("valid_to"):
        vf = datetime.date.fromisoformat(v["valid_from"]) if isinstance(v["valid_from"], str) else v["valid_from"]
        vt = datetime.date.fromisoformat(v["valid_to"]) if isinstance(v["valid_to"], str) else v["valid_to"]
        if vt <= vf:
            print("INVALID INTERVAL IN VERSION: " + v["provision_id"] + ", from " + str(vf) + " to " + str(vt))

try:
    from backend.ingestion.chunker_v2 import chunk_versions
    chunks = chunk_versions(versions, parsed, "candidate-1")
    print(f"Successfully built {len(chunks)} chunks")
except Exception as e:
    traceback.print_exc()
