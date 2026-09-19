"""Investigate source_refs format in chunks."""
import json
from collections import Counter
from pathlib import Path

STAGE = Path("data/staging/phase1-candidate")
REGISTRY = Path("data/registry")

with open(STAGE / "chunks.jsonl", encoding="utf-8") as f:
    chunks = [json.loads(l) for l in f if l.strip()]

# Check the variety of source_refs source_id formats
sid_formats = Counter()
for c in chunks:
    for ref in c.get("source_refs", []):
        sid = ref.get("source_id", "")
        if sid.startswith("src:"):
            sid_formats["src: prefix"] += 1
        elif sid.startswith("article:") or sid.startswith("doc:") or sid.startswith("body"):
            sid_formats["locator format"] += 1
        elif sid:
            sid_formats["other: " + sid[:20]] += 1
        else:
            sid_formats["empty"] += 1

print("source_refs source_id format counts:")
for k, v in sid_formats.most_common(10):
    print(f"  {k}: {v}")

# Show a chunk with proper src: format
good = next((c for c in chunks if any(r.get("source_id", "").startswith("src:") for r in c.get("source_refs", []))), None)
if good:
    print("Sample chunk with proper source_id:")
    print(f"  doc_id: {good['doc_id']}")
    print(f"  source_refs: {good['source_refs']}")
else:
    print("NO chunks with proper src: prefix source_id")

# Show what locator-format source_ids look like
bad = next((c for c in chunks if any(not r.get("source_id", "").startswith("src:") and r.get("source_id") for r in c.get("source_refs", []))), None)
if bad:
    print("Sample chunk with locator-format source_id:")
    print(f"  doc_id: {bad['doc_id']}")
    print(f"  source_refs: {bad['source_refs']}")
    print(f"  provision_id: {bad['provision_id']}")

# Check if source_refs uses a different field name for registry source_id
# In chunker, source_id passed to chunk_articles was the registry src: ID
# Let's look at what values the locator-style ones are
locator_samples = set()
for c in chunks:
    for ref in c.get("source_refs", []):
        sid = ref.get("source_id", "")
        if sid and not sid.startswith("src:"):
            locator_samples.add(sid)
        if len(locator_samples) >= 10:
            break
    if len(locator_samples) >= 10:
        break
print(f"Sample locator-style source_ids: {list(locator_samples)[:10]}")

# Check if there's a separate field for the file source
print("\nChecking for 'source_url' field:")
sample_with_url = next((c for c in chunks if any(r.get("source_url") for r in c.get("source_refs", []))), None)
if sample_with_url:
    print(f"  Has source_url: {sample_with_url['source_refs']}")
else:
    print("  No chunks have source_url in source_refs")
