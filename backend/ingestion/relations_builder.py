import json
import os

# ─── Seed relations: Quan hệ hardcoded thủ công, KHÔNG auto-extract được ─────
# Dùng đúng key "relation_type" để khớp schema của extract_relations.py và graph_utils.py.
# Import constant này từ extract_relations.py để merge vào output.
SEED_RELATIONS = [
    {
        "source_doc": "45/2019/QH14",
        "target_doc": "10/2012/QH13",
        "relation_type": "thay_the",
        "scope": "toan_bo",
        "target_article": None,
        "effective_date": "2021-01-01",
        "status": "active",
        "note": "BLLĐ 2019 thay thế toàn bộ BLLĐ 2012"
    },
    {
        "source_doc": "145/2020/NĐ-CP",
        "target_doc": "45/2019/QH14",
        "relation_type": "huong_dan",
        "scope": "toan_bo",
        "target_article": None,
        "effective_date": "2021-02-01",
        "status": "active",
        "note": "Hướng dẫn chi tiết BLLĐ 2019"
    },
    {
        "source_doc": "12/2022/NĐ-CP",
        "target_doc": "45/2019/QH14",
        "relation_type": "huong_dan",
        "scope": "toan_bo",
        "target_article": None,
        "effective_date": "2022-01-17",
        "status": "active",
        "note": "Xử phạt VPHC trong lĩnh vực lao động"
    },
    {
        "source_doc": "35/2022/NĐ-CP",
        "target_doc": "145/2020/NĐ-CP",
        "relation_type": "sua_doi",
        "scope": "mot_so_dieu",
        "target_article": None,
        "effective_date": "2022-05-28",
        "status": "active",
        "note": "Sửa đổi, bổ sung một số điều NĐ 145/2020"
    },
    {
        "source_doc": "74/2024/NĐ-CP",
        "target_doc": "38/2022/NĐ-CP",
        "relation_type": "thay_the",
        "scope": "toan_bo",
        "target_article": None,
        "effective_date": "2024-07-01",
        "status": "active",
        "note": "Lương tối thiểu vùng 2024 thay thế NĐ 38/2022"
    },
]


def build_relations():
    """Legacy entry point is disabled; seeds are review candidates only."""
    raise RuntimeError("Seed relations require evidence and review; use extract_relations for candidate output")
