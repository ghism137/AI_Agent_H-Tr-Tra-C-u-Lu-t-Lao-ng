import json
import os
import re
from typing import Dict, Any, List

def normalize_text(text: str) -> str:
    """Xóa khoảng trắng thừa và chuẩn hóa chuỗi."""
    if not text:
        return ""
    # Giữ lại khoảng trắng đơn
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_watermarks(text: str) -> str:
    """Xóa các đoạn văn bản nghi ngờ là watermark của bên thứ 3."""
    watermarks = [
        "thuvienphapluat",
        "thư viện pháp luật",
        "luatvietnam",
        "luật việt nam",
        "luatminhkhue",
        "giaoducphapluat",
        "www."
    ]
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        lower_line = line.lower()
        # Bỏ qua dòng nếu chứa watermark
        if any(wm in lower_line for wm in watermarks):
            continue
        clean_lines.append(line)
    return '\n'.join(clean_lines)

def parse_legal_document(markdown_content: str, doc_meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phân tích file Markdown và trích xuất cấu trúc văn bản pháp luật.
    """
    text = remove_watermarks(markdown_content)
    
    # Regex để nhận diện các cấp bậc
    phan_pattern = re.compile(r'^Phần\s+([A-Z0-9IVX]+)(.*)', re.IGNORECASE)
    chuong_pattern = re.compile(r'^Chương\s+([A-Z0-9IVX]+)(.*)', re.IGNORECASE)
    muc_pattern = re.compile(r'^Mục\s+(\d+)(.*)', re.IGNORECASE)
    dieu_pattern = re.compile(r'^Điều\s+(\d+)\.(.*)', re.IGNORECASE)
    
    lines = [normalize_text(line) for line in text.split('\n') if normalize_text(line)]
    
    articles = []
    current_phan = ""
    current_chuong = ""
    current_muc = ""
    current_dieu = None
    
    has_dieu = False
    
    for line in lines:
        if phan_match := phan_pattern.match(line):
            current_phan = line
            continue
        if chuong_match := chuong_pattern.match(line):
            current_chuong = line
            continue
        if muc_match := muc_pattern.match(line):
            current_muc = line
            continue
        if dieu_match := dieu_pattern.match(line):
            has_dieu = True
            if current_dieu:
                articles.append(current_dieu)
            
            hierarchy = []
            if current_phan: hierarchy.append(current_phan)
            if current_chuong: hierarchy.append(current_chuong)
            if current_muc: hierarchy.append(current_muc)
            
            hierarchy_path = " > ".join(hierarchy) if hierarchy else ""
            
            current_dieu = {
                "article_number": dieu_match.group(1),
                "title": dieu_match.group(2).strip(),
                "hierarchy_path": hierarchy_path,
                "content": [line]
            }
            continue
            
        if current_dieu:
            current_dieu["content"].append(line)
            
    if current_dieu:
        articles.append(current_dieu)
        
    # Trường hợp file biểu mẫu/phụ lục không có "Điều" nào, ta gom tất cả vào một
    if not has_dieu and lines:
        title = lines[0] if len(lines) > 0 else "Nội dung"
        articles.append({
            "article_number": "ALL",
            "title": title,
            "hierarchy_path": "",
            "content": lines
        })
        
    return {
        "metadata": doc_meta,
        "articles": [
            {
                "article_number": a["article_number"],
                "title": a.get("title", ""),
                "hierarchy_path": a["hierarchy_path"],
                "content": "\n".join(a["content"])
            }
            for a in articles
        ]
    }

def save_cleaned(cleaned_data: Dict[str, Any], output_path: str):
    """Lưu dữ liệu đã parse ra file JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
