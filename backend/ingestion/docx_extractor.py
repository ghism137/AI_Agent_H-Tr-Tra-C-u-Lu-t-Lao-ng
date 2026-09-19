"""Extract DOCX blocks with Word numbering and source locations."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph


def _numbering_definitions(document: Document) -> dict[str, dict[int, dict[str, Any]]]:
    try:
        root = document.part.numbering_part.element
    except (KeyError, NotImplementedError):
        return {}
    abstract_levels: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    levels_by_num: dict[str, dict[int, dict[str, Any]]] = {}
    for abstract in root.findall(qn("w:abstractNum")):
        abstract_id = abstract.get(qn("w:abstractNumId"))
        for level in abstract.findall(qn("w:lvl")):
            ilvl = int(level.get(qn("w:ilvl"), "0"))
            text = level.find(qn("w:lvlText"))
            start = level.find(qn("w:start"))
            abstract_levels[abstract_id][ilvl] = {
                "template": text.get(qn("w:val"), "") if text is not None else "",
                "start": int(start.get(qn("w:val"), "1")) if start is not None else 1,
            }
    for num in root.findall(qn("w:num")):
        num_id = num.get(qn("w:numId"))
        abstract = num.find(qn("w:abstractNumId"))
        if abstract is None:
            continue
        abstract_id = abstract.get(qn("w:val"))
        # Overrides belong to this concrete numId, never to the shared abstractNum.
        levels_by_num[num_id] = {level: definition.copy()
                                 for level, definition in abstract_levels.get(abstract_id, {}).items()}
        for override in num.findall(qn("w:lvlOverride")):
            ilvl = int(override.get(qn("w:ilvl"), "0"))
            start = override.find(qn("w:startOverride"))
            if start is not None and ilvl in levels_by_num[num_id]:
                levels_by_num[num_id][ilvl]["start"] = int(start.get(qn("w:val"), "1"))
    return levels_by_num


def _num_properties(paragraph: Paragraph) -> tuple[str, int] | None:
    p_pr = paragraph._p.pPr
    num_pr = p_pr.numPr if p_pr is not None else None
    if num_pr is None and paragraph.style is not None and paragraph.style.element.pPr is not None:
        num_pr = paragraph.style.element.pPr.numPr
    if num_pr is None or num_pr.numId is None:
        return None
    return str(num_pr.numId.val), int(num_pr.ilvl.val) if num_pr.ilvl is not None else 0


def extract_docx(path: Path) -> list[dict[str, Any]]:
    document = Document(path)
    levels_by_num = _numbering_definitions(document)
    counters: dict[str, dict[int, int]] = defaultdict(dict)
    blocks: list[dict[str, Any]] = []
    for index, child in enumerate(document.element.body.iterchildren()):
        if child.tag == qn("w:p"):
            paragraph = Paragraph(child, document)
            text = paragraph.text.strip()
            if not text:
                continue
            number = _num_properties(paragraph)
            if number is not None:
                num_id, ilvl = number
                definition = levels_by_num.get(num_id, {}).get(ilvl)
                if definition is None or not definition["template"]:
                    raise ValueError(f"Unresolved Word numbering at paragraph {index} in {path}")
                values = counters[num_id]
                values[ilvl] = values.get(ilvl, definition["start"] - 1) + 1
                for lower in list(values):
                    if lower > ilvl:
                        del values[lower]
                prefix = definition["template"]
                for level_number in range(1, 10):
                    if f"%{level_number}" in prefix:
                        value = values.get(level_number - 1)
                        if value is None:
                            raise ValueError(f"Missing Word numbering parent at paragraph {index} in {path}")
                        prefix = prefix.replace(f"%{level_number}", str(value))
                if re.match(r"^Điều\s+\d+[a-z]?\.", prefix, re.I) and not re.match(r"^Điều\s+\d+[a-z]?\.", text, re.I):
                    text = f"{prefix} {text}"
            blocks.append({"kind": "paragraph", "text": text, "locator": f"body/p:{index}"})
        elif child.tag == qn("w:tbl"):
            table = Table(child, document)
            physical_cells = []
            for row_number, tr in enumerate(table._tbl.tr_lst, 1):
                column_number = 1
                header = tr.find(qn("w:trPr"))
                is_header = header is not None and header.find(qn("w:tblHeader")) is not None
                for tc in tr.tc_lst:
                    properties = tc.find(qn("w:tcPr"))
                    span = properties.find(qn("w:gridSpan")) if properties is not None else None
                    merge = properties.find(qn("w:vMerge")) if properties is not None else None
                    column_span = int(span.get(qn("w:val"), "1")) if span is not None else 1
                    physical_cells.append({
                        "row": row_number, "column": column_number,
                        "column_span": column_span,
                        "vertical_merge": merge.get(qn("w:val"), "continue") if merge is not None else None,
                        "is_header": is_header,
                        "text": _Cell(tc, table).text.strip(),
                        "locator": f"body/table:{index}/row:{row_number}/col:{column_number}",
                    })
                    column_number += column_span
            rows = []
            for row_number in range(1, len(table._tbl.tr_lst) + 1):
                values = []
                for cell in (item for item in physical_cells if item["row"] == row_number):
                    values.append("" if cell["vertical_merge"] == "continue" else cell["text"])
                    values.extend([""] * (cell["column_span"] - 1))
                rows.append(values)
            blocks.append({"kind": "table", "rows": rows, "cells": physical_cells,
                           "locator": f"body/table:{index}"})
    return blocks
