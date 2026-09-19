"""Archive government HTML full text for review."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import requests


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data/raw/official"
PAGES = {
    "41-2024-QH15": "https://xaydungchinhsach.chinhphu.vn/toan-van-luat-so-41-2024-qh15-bao-hiem-xa-hoi-119240723163650489.htm",
    "74-2025-QH15": "https://xaydungchinhsach.chinhphu.vn/toan-van-luat-viec-lam-119250711173403835.htm",
    "293-2025-ND-CP": "https://xaydungchinhsach.chinhphu.vn/nghi-dinh-so-293-2025-nd-cp-quy-dinh-muc-luong-toi-thieu-doi-voi-nguoi-lao-dong-lam-viec-theo-hop-dong-lao-dong-119251110172808433.htm",
    "158-2025-ND-CP": "https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-158-2025-nd-cp-quy-dinh-ve-bao-hiem-xa-hoi-bat-buoc-119250629171336803.htm",
    "51-2024-QH15": "https://xaydungchinhsach.chinhphu.vn/toan-van-luat-sua-doi-bo-sung-mot-so-dieu-cua-luat-bao-hiem-y-te-11924122017211787.htm",
    "219-2025-ND-CP": "https://xaydungchinhsach.chinhphu.vn/nghi-dinh-so-219-2025-nd-cp-quy-dinh-ve-nguoi-lao-dong-nuoc-ngoai-lam-viec-tai-viet-nam-11925080910491801.htm",
}
def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    records = []
    for number, url in PAGES.items():
        response = requests.get(url, timeout=45)
        response.raise_for_status()
        target = DEST / f"{number}.html"
        target.write_bytes(response.content)
        records.append({"document": number, "path": target.relative_to(ROOT).as_posix(), "url": url,
                        "sha256": hashlib.sha256(response.content).hexdigest(), "bytes": len(response.content)})
    (DEST / "text_download_manifest.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{"document": entry["document"], "bytes": entry["bytes"]} for entry in records]))


if __name__ == "__main__":
    main()
