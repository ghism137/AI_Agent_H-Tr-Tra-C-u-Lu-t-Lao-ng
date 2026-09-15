import json
import os
import glob
import re
from typing import List, Dict, Any, Tuple

def extract_relations(text: str, source_doc: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Trích xuất các mối quan hệ pháp lý từ nội dung văn bản.

    Args:
        text: Nội dung văn bản pháp luật cần phân tích.
        source_doc: Số hiệu văn bản gốc (ví dụ: "45/2019/QH14").

    Returns:
        Một tuple gồm hai danh sách:
        - relations: Danh sách tất cả các quan hệ trích xuất được.
        - needs_review: Danh sách các quan hệ có rủi ro cao (sua_doi, thay_the, bai_bo) cần con người kiểm duyệt.
    """
    relations = []
    needs_review = []
    
    action_patterns = {
        "can_cu": (r'căn cứ\s+.*?(?:luật|nghị định|thông tư|bộ luật)\s+.*?(?:số\s+)?([a-z0-9/đ-]+)', "low"),
        "sua_doi": (r'sửa đổi(?:,\s*bổ sung)?\s+', "high"),
        "bo_sung": (r'bổ sung\s+', "low"),
        "thay_the": (r'thay thế\s+', "high"),
        "bai_bo": (r'bãi bỏ\s+', "high"),
        "huong_dan": (r'hướng dẫn\s+(?:thi hành\s+)?', "low")
    }
    
    # Matches formats like 45/2019/QH14, 145/2020/NĐ-CP
    doc_pattern = re.compile(r'\b([0-9a-zA-Z]+/[0-9]{4}/[a-zA-Z0-9Đ-]+)\b', re.IGNORECASE)
    # Cải thiện regex để bắt "các Điều 1, 2 và 3"
    article_pattern = re.compile(r'(?:các\s+)?(điều\s+\d+[a-z]*(?:(?:\s*,\s*|\s+và\s+)\d+[a-z]*)*)', re.IGNORECASE)
    
    for rel_type, (pattern, risk) in action_patterns.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start_idx = match.start()
            # Cửa sổ tối đa 300 ký tự hoặc dừng khi gặp . ; \n
            max_end = min(len(text), start_idx + 300)
            
            dot_idx = text.find('.', match.end(), max_end)
            semi_idx = text.find(';', match.end(), max_end)
            nl_idx = text.find('\n', match.end(), max_end)
            
            cut_idx = max_end
            valid_cuts = [i for i in (dot_idx, semi_idx, nl_idx) if i != -1]
            if valid_cuts:
                cut_idx = min(valid_cuts)
                
            scope_span = text[start_idx:cut_idx]
            
            target_docs = list(set(doc_pattern.findall(scope_span)))
            if not target_docs:
                continue
                
            target_articles = list(set(article_pattern.findall(scope_span)))
            
            for t_doc in target_docs:
                t_doc_upper = t_doc.upper()
                # Bỏ qua self-reference (kể cả khi format khác nhau chút)
                if t_doc_upper == source_doc or t_doc_upper.replace('/', '-') == source_doc.replace('/', '-'):
                    continue
                    
                if target_articles:
                    for t_art in target_articles:
                        rel = {
                            "source_doc": source_doc,
                            "target_doc": t_doc_upper,
                            "relation_type": rel_type,
                            "scope": "dieu_khoan_cu_the",
                            "target_article": t_art.capitalize(),
                            "status": "active"
                        }
                        if rel not in relations:
                            relations.append(rel)
                            if risk == "high": needs_review.append(rel)
                else:
                    rel = {
                        "source_doc": source_doc,
                        "target_doc": t_doc_upper,
                        "relation_type": rel_type,
                        "scope": "mot_so_dieu" if rel_type in ["sua_doi", "bo_sung"] else "toan_bo",
                        "target_article": None,
                        "status": "active"
                    }
                    if rel not in relations:
                        relations.append(rel)
                        if risk == "high": needs_review.append(rel)
                    
    return relations, needs_review

def _normalize_doc_number(raw: str) -> str:
    """
    Chuyển đổi tên file sang số hiệu văn bản chuẩn.
    Chỉ replace đúng 2 dấu '-' đầu (ngăn cách số/năm/loại).

    Ví dụ:
      "145-2020-NĐ-CP"   → "145/2020/NĐ-CP"   ✓
      "45-2019-QH14"     → "45/2019/QH14"      ✓
      "06-2021-TT-BLĐTBXH" → "06/2021/TT-BLĐTBXH" ✓
    """
    parts = raw.split('-', 2)          # tách tối đa 3 phần: [số, năm, loại-suffix]
    if len(parts) == 3:
        return f"{parts[0]}/{parts[1]}/{parts[2]}".upper()
    # fallback an toàn nếu format không khớp
    return raw.replace('-', '/').upper()

def build_relations_corpus(
    raw_dir: str = None,
    relations_file: str = None,
    review_file: str = None
) -> None:
    """
    Xây dựng kho dữ liệu quan hệ pháp lý từ các file Markdown.

    Args:
        raw_dir: Thư mục chứa các file markdown thô. Mặc định từ RAW_MD_DIR hoặc 'data/raw/manual_md'.
        relations_file: File output lưu tất cả quan hệ. Mặc định từ RELATIONS_FILE hoặc 'data/document_relations.json'.
        review_file: File output lưu các quan hệ cần review. Mặc định từ REVIEW_FILE hoặc 'data/relations_needs_review.json'.
    """
    from backend.ingestion.relations_builder import SEED_RELATIONS

    raw_dir = raw_dir or os.getenv("RAW_MD_DIR", "data/raw/manual_md")
    relations_file = relations_file or os.getenv("RELATIONS_FILE", "data/document_relations.json")
    review_file = review_file or os.getenv("REVIEW_FILE", "data/relations_needs_review.json")

    md_files = glob.glob(os.path.join(raw_dir, '*.md'))
    
    all_relations = []
    all_needs_review = []

    # ── Seed trước — đảm bảo các quan hệ quan trọng không bị bỏ sót ─────────
    # Dùng set of (source, target, type) để dedup
    seen = set()
    for rel in SEED_RELATIONS:
        key = (rel['source_doc'], rel['target_doc'], rel['relation_type'])
        if key not in seen:
            all_relations.append(rel)
            seen.add(key)
    
    # ── Auto-extract từ corpus ─────────────────────────────────────────────────
    for file_path in md_files:
        file_name = os.path.basename(file_path)

        # FIX Bug 2: chỉ replace 2 dấu '-' đầu tiên để giữ nguyên suffix (NĐ-CP, TT-BLĐTBXH...)
        match = re.search(r'-(\d+-\d+-[A-ZĐa-z0-9-]+)\.md', file_name)
        if match:
            doc_number = _normalize_doc_number(match.group(1))
        else:
            doc_number = file_name.replace('.md', '')
            
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        rels, reviews = extract_relations(text, doc_number)

        for rel in rels:
            key = (rel['source_doc'], rel['target_doc'], rel['relation_type'])
            if key not in seen:
                all_relations.append(rel)
                seen.add(key)

        all_needs_review.extend(reviews)
        
    os.makedirs(os.path.dirname(relations_file) or '.', exist_ok=True)
    with open(relations_file, 'w', encoding='utf-8') as f:
        json.dump(all_relations, f, ensure_ascii=False, indent=2)
        
    os.makedirs(os.path.dirname(review_file) or '.', exist_ok=True)
    with open(review_file, 'w', encoding='utf-8') as f:
        json.dump(all_needs_review, f, ensure_ascii=False, indent=2)
        
    print(f"Total relations extracted: {len(all_relations)}")
    print(f"  - Seed relations: {len(SEED_RELATIONS)}")
    print(f"  - Auto-extracted: {len(all_relations) - len(SEED_RELATIONS)}")
    print(f"Relations needing manual review: {len(all_needs_review)}")

if __name__ == "__main__":
    build_relations_corpus()
