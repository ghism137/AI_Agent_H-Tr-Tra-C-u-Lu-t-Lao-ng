from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from backend.ingestion.docx_extractor import _numbering_definitions


def _element(name, **attributes):
    node = OxmlElement(name)
    for key, value in attributes.items():
        node.set(qn(f"w:{key}"), str(value))
    return node


def test_start_override_is_local_to_num_id():
    document = Document()
    root = document.part.numbering_part.element
    abstract = _element("w:abstractNum", abstractNumId="999")
    level = _element("w:lvl", ilvl="0")
    level.append(_element("w:start", val="1"))
    level.append(_element("w:lvlText", val="Điều %1."))
    abstract.append(level)
    root.append(abstract)
    for num_id, start in (("998", "7"), ("999", "1")):
        num = _element("w:num", numId=num_id)
        num.append(_element("w:abstractNumId", val="999"))
        override = _element("w:lvlOverride", ilvl="0")
        override.append(_element("w:startOverride", val=start))
        num.append(override)
        root.append(num)

    levels = _numbering_definitions(document)
    assert levels["998"][0]["start"] == 7
    assert levels["999"][0]["start"] == 1
