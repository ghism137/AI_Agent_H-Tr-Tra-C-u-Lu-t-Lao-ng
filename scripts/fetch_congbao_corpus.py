"""Archive original text-layer Công báo issues for core laws."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data/raw/official"
URLS = {
    "41-2024-QH15-congbao.pdf": "https://congbaocdn.chinhphu.vn/CongBaoCP/CongBao/2024/8/42574/51463-1-987-988.pdf",
    "74-2025-QH15-congbao.pdf": "https://congbaocdn.chinhphu.vn/CongBaoCP/CongBao/2025/7/45558/57693-1-967-968.pdf",
    "293-2025-ND-CP-congbao.pdf": "https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2025/11/46568/59713-1-20251591-1592293-2025-nd-cp.pdf",
    "188-2025-ND-CP-congbao-part1.pdf": "https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2025/7/45593/57770-1-2025977-978188-2025-nd-cp.pdf",
    "188-2025-ND-CP-congbao-part2.pdf": "https://congbaocdn.chinhphu.vn/CongBaoCP/CongBao/2025/7/45600/57783-1-979-980.pdf",
    "219-2025-ND-CP-congbao.pdf": "https://congbaocdn.chinhphu.vn/CongBaoCP/CongBao/2025/8/45797/58140-1-1073-1074.pdf",
}


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, url in URLS.items():
        target = DEST / name
        if target.exists() and target.read_bytes().startswith(b"%PDF-"):
            content = target.read_bytes()
        else:
            response = requests.get(url, timeout=180)
            response.raise_for_status()
            content = response.content
        if not content.startswith(b"%PDF-"):
            raise ValueError(f"Not a PDF: {url}")
        target.write_bytes(content)
        manifest.append({"path": target.relative_to(ROOT).as_posix(), "url": url,
                         "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)})
    (DEST / "congbao_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{"path": item["path"], "bytes": item["bytes"]} for item in manifest]))


if __name__ == "__main__":
    main()
