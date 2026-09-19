"""Extract legal blocks from archived government full-text HTML."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag


def extract_government_html(path: Path) -> list[dict[str, Any]]:
    soup = BeautifulSoup(path.read_bytes(), "html.parser")
    body = soup.select_one(".detail-content.afcbc-body")
    if body is None:
        raise ValueError(f"No government article body in {path}")
    blocks = []
    for index, child in enumerate(body.children):
        if not isinstance(child, Tag):
            continue
        if child.name == "table":
            rows = [[cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"], recursive=False)]
                    for row in child.find_all("tr")]
            blocks.append({"kind": "table", "rows": rows, "locator": f"html/table:{index}"})
        elif child.name in {"p", "h1", "h2", "h3", "h4", "h5"}:
            text = child.get_text(" ", strip=True)
            if text:
                blocks.append({"kind": "paragraph", "text": text, "locator": f"html/{child.name}:{index}"})
    if not any(block["text"].startswith("Điều 1.") for block in blocks if block["kind"] == "paragraph"):
        raise ValueError(f"Government HTML lacks Điều 1: {path}")
    return blocks
