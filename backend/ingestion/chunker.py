import json
import re
from typing import Dict, Any, List

def split_article_by_clauses(article_text: str) -> List[Dict[str, Any]]:
    """Chia một Điều thành nhiều đoạn dựa theo số thứ tự Khoản (1., 2., 3.,...)."""
    clause_pattern = re.compile(r'^(\d+)\.\s', re.MULTILINE)
    
    lines = article_text.split('\n')
    chunks = []
    current_chunk = []
    current_clause_numbers = []
    
    title = lines[0] if lines else ""
    current_chunk.append(title)
    
    for line in lines[1:]:
        match = clause_pattern.match(line)
        if match:
            content_len = sum(len(c) for c in current_chunk)
            if content_len > 1000 and len(current_chunk) > 1:
                chunks.append({
                    "text": "\n".join(current_chunk),
                    "clauses": current_clause_numbers.copy()
                })
                current_chunk = [title]
                current_clause_numbers = []
            
            clause_num = match.group(1)
            current_clause_numbers.append(clause_num)
        
        current_chunk.append(line)
        
    if len(current_chunk) > 1 or not chunks:
        chunks.append({
            "text": "\n".join(current_chunk),
            "clauses": current_clause_numbers
        })
        
    return chunks

def split_text_by_length(text: str, title: str, max_len: int = 1500) -> List[Dict[str, Any]]:
    """Cắt text theo giới hạn ký tự (dành cho biểu mẫu không có Khoản)."""
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    
    for line in lines:
        current_chunk.append(line)
        content_len = sum(len(c) for c in current_chunk)
        if content_len >= max_len:
            chunks.append({
                "text": "\n".join(current_chunk),
                "clauses": []
            })
            current_chunk = [title] if title else []
            
    if current_chunk and (len(current_chunk) > 1 or not title or current_chunk[0] != title):
        chunks.append({
            "text": "\n".join(current_chunk),
            "clauses": []
        })
        
    if not chunks:
        chunks.append({"text": text, "clauses": []})
        
    return chunks

def extract_cross_references(text: str) -> List[str]:
    """Tìm các cụm từ tham chiếu chéo"""
    refs = re.findall(r'(Điều\s+\d+[a-zA-Z]*)', text, re.IGNORECASE)
    return list(set(refs))

def extract_related_documents(text: str) -> List[str]:
    """Tìm số hiệu các văn bản pháp luật được nhắc đến trong chunk"""
    docs = re.findall(r'\b\d+/\d+/[A-ZĐa-z0-9-]+\b', text)
    return list(set(docs))

def chunk_document(cleaned_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Chuyển đổi dữ liệu JSON của 1 văn bản thành danh sách các chunks."""
    meta = cleaned_json.get("metadata", {})
    articles = cleaned_json.get("articles", [])
    
    doc_number = meta.get("doc_number", "UNKNOWN")
    doc_type = meta.get("doc_type", "luat")
    
    output_chunks = []
    
    for article in articles:
        article_num = str(article.get("article_number", ""))
        hierarchy = article.get("hierarchy_path", "")
        content = article.get("content", "")
        title = article.get("title", "")
        
        # Xử lý riêng cho biểu mẫu/phụ lục không có "Điều" (article_num == "ALL")
        if article_num == "ALL":
            if len(content) > 2000:
                sub_chunks = split_text_by_length(content, title)
                for i, sub in enumerate(sub_chunks):
                    chunk = build_chunk(meta, doc_number, f"ALL_P{i+1}", hierarchy, sub["text"], None, title)
                    output_chunks.append(chunk)
            else:
                chunk = build_chunk(meta, doc_number, "ALL", hierarchy, content, None, title)
                output_chunks.append(chunk)
            continue
            
        # Xử lý cho Điều bình thường
        if len(content) > 2000:
            sub_chunks = split_article_by_clauses(content)
            for i, sub in enumerate(sub_chunks):
                clauses = sub["clauses"]
                clause_range = f"K{clauses[0]}-K{clauses[-1]}" if len(clauses) > 1 else (f"K{clauses[0]}" if clauses else f"P{i+1}")
                chunk = build_chunk(meta, doc_number, article_num, hierarchy, sub["text"], clause_range, title)
                output_chunks.append(chunk)
        else:
            chunk = build_chunk(meta, doc_number, article_num, hierarchy, content, None, title)
            output_chunks.append(chunk)
            
    return output_chunks

def build_chunk(meta: dict, doc_number: str, article_num: str, hierarchy: str, content: str, clause_range: str, title: str) -> dict:
    """Tạo dict chunk với đầy đủ các trường (bao gồm schema mới)."""
    chunk_id = f"{doc_number.replace('/','-')}_D{article_num}"
    if clause_range:
        chunk_id += f"_{clause_range}"
        
    tags = set(meta.get("topic_tags", []))
    if hierarchy:
        for p in hierarchy.split('>'):
            if p.strip():
                tags.add(p.strip())
    if title:
        tags.add(title)
        
    related_docs = extract_related_documents(content)
    related_docs = [d for d in related_docs if d != doc_number]
    
    existing_related = meta.get("related_documents", [])
    combined_related = list(set(existing_related + related_docs))
        
    return {
        "chunk_id": chunk_id,
        "doc_type": meta.get("doc_type", ""),
        "doc_number": doc_number,
        "doc_title": meta.get("doc_title", ""),
        "article_number": article_num,
        "hierarchy_path": hierarchy,
        "content": content,
        "chunk_length": len(content),
        "cross_references": extract_cross_references(content),
        "embedding": None, 
        "keywords": meta.get("keywords", []),
        "topic_tags": list(tags),
        "issuing_body": meta.get("issuing_body", ""),
        "issue_date": meta.get("issue_date", ""),
        "effective_date": meta.get("effective_date", ""),
        "status": meta.get("status", "con_hieu_luc"),
        "replaces": meta.get("replaces", []),
        "replaced_by": meta.get("replaced_by", []),
        "signer": meta.get("signer", ""),
        "related_documents": combined_related,
        "domain": meta.get("domain", "luat_lao_dong"),
        "url": meta.get("url", "")
    }
