"""Download named government attachments, preserving original bytes and URL."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "raw" / "official"
PAGES = {
    "41-2024-QH15": "https://vanban.chinhphu.vn/?classid=1&docid=211199&orggroupid=1&pageid=27160",
    "74-2025-QH15": "https://vanban.chinhphu.vn/?docid=214560&pageid=27160",
    "374-2025-ND-CP": "https://vanban.chinhphu.vn/?classid=1&docid=216493&pageid=27160",
    "293-2025-ND-CP": "https://vanban.chinhphu.vn/?classid=1&docid=215832&pageid=27160",
}


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    records = []
    for number, page_url in PAGES.items():
        page = requests.get(page_url, timeout=30)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, "html.parser")
        links = []
        for anchor in soup.find_all("a", href=True):
            href = urljoin(page_url, anchor["href"])
            if "datafiles.chinhphu.vn" in href and href.lower().split("?")[0].endswith(".pdf"):
                links.append((anchor.get_text(" ", strip=True), href))
        for index, (name, url) in enumerate(dict.fromkeys(links), 1):
            response = requests.get(url, timeout=90)
            response.raise_for_status()
            target = DEST / f"{number}-{index}.pdf"
            target.write_bytes(response.content)
            records.append({"doc_number_slug": number, "path": target.relative_to(ROOT).as_posix(),
                            "url": url, "landing_page": page_url, "attachment_name": name,
                            "sha256": hashlib.sha256(response.content).hexdigest(), "bytes": len(response.content)})
    (DEST / "download_manifest.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{"document": number, "count": sum(record["doc_number_slug"] == number for record in records)} for number in PAGES], ensure_ascii=False))


if __name__ == "__main__":
    main()
