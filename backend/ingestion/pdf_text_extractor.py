"""Read an existing PDF text layer; never perform OCR."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pymupdf


HEADER = re.compile(
    r"^(?:\d+\s+)?CÔNG BÁO/Số\s+\d+(?:\s*\+\s*\d+)?/Ngày\s+\d{1,2}-\d{1,2}-\d{4}(?:\s+\d+)?$"
)


def extract_pdf_text(path: Path, *, first_page: int, last_page: int) -> list[dict[str, Any]]:
    document = pymupdf.open(path)
    if first_page < 1 or last_page > len(document) or first_page > last_page:
        raise ValueError("invalid PDF page interval")
    blocks = []
    for page_number in range(first_page, last_page + 1):
        lines = document[page_number - 1].get_text(sort=True).splitlines()
        if len("".join(lines)) < 200:
            raise ValueError(f"PDF page {page_number} has no usable text layer")
        for index, raw in enumerate(lines, 1):
            line = raw.strip()
            next_line = lines[index].strip() if index < len(lines) else ""
            if (not line or HEADER.match(line) or line == str(page_number)
                    or (line.isdigit() and HEADER.match(next_line))):
                continue
            blocks.append({"kind": "paragraph", "text": line, "locator": f"pdf/page:{page_number}/line:{index}"})
    return blocks
