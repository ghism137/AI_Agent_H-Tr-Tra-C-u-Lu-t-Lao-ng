import json
import os
from datetime import date

# ── Module-level cache — tránh đọc file mỗi lần gọi (Issue 6) ────────────────
_relations_cache: list | None = None
_relations_cached_path: str | None = None


def load_relations(filepath: str = 'data/document_relations.json') -> list:
    """Load relations từ file, cache kết quả vào bộ nhớ."""
    global _relations_cache, _relations_cached_path
    if _relations_cache is None or _relations_cached_path != filepath:
        if not os.path.exists(filepath):
            _relations_cache = []
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                _relations_cache = json.load(f)
        _relations_cached_path = filepath
    return _relations_cache


def invalidate_cache():
    """Gọi sau khi re-generate document_relations.json để clear cache."""
    global _relations_cache, _relations_cached_path
    _relations_cache = None
    _relations_cached_path = None


def is_valid(doc_id: str, article: str, relations: list,
             reference_date: str | None = None) -> bool:
    """
    Kiểm tra xem một Điều khoản của một văn bản còn hiệu lực hay không.
    Trả về False nếu bị sửa đổi, thay thế, hoặc bãi bỏ tính đến reference_date.

    Args:
        doc_id:         Số hiệu văn bản (vd: "45/2019/QH14")
        article:        Số điều (vd: "Điều 36"), hoặc None để kiểm tra toàn bộ VB
        relations:      Danh sách relations (từ load_relations())
        reference_date: ISO date string "YYYY-MM-DD"; mặc định là ngày hôm nay
    """
    if reference_date is None:
        reference_date = date.today().isoformat()

    for rel in relations:
        if rel.get('review_status') != 'verified':
            continue
        target_doc = rel.get('target_doc') or rel.get('target_doc_id', '').removeprefix('doc:')
        if target_doc != doc_id:
            continue
        if rel.get('relation_type') not in ('thay_the', 'bai_bo', 'replaces', 'repeals'):
            continue

        # Issue 7: Bỏ qua nếu quan hệ chưa có hiệu lực ───────────────────────
        eff_date = rel.get('effective_date') or rel.get('effective_from')
        if not eff_date or eff_date > reference_date:
            continue

        scope = rel.get('scope', 'toan_bo')
        if scope in ('toan_bo', 'document'):
            return False
        if scope == 'dieu_khoan_cu_the' and rel.get('target_article') == article:
            return False

    return True


def get_supplementary_docs(doc_id: str, relations: list) -> list:
    """
    Lấy danh sách các văn bản bổ sung / hướng dẫn cho văn bản hiện tại (1-hop expansion).

    Args:
        doc_id:    Số hiệu văn bản gốc cần tìm văn bản phụ trợ
        relations: Danh sách relations (từ load_relations())
    Returns:
        List[str] — số hiệu các văn bản hướng dẫn / bổ sung
    """
    supp_docs = set()
    for rel in relations:
        target_doc = rel.get('target_doc') or rel.get('target_doc_id', '').removeprefix('doc:')
        if rel.get('review_status') == 'verified' and target_doc == doc_id and rel.get('relation_type') in ('huong_dan', 'bo_sung', 'guides', 'supplements'):
            supp_docs.add(rel.get('source_doc') or rel.get('source_doc_id', '').removeprefix('doc:'))
    return sorted(supp_docs)
