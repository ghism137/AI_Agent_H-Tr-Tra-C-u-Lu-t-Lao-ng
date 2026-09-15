import json
import os
import glob
from backend.ingestion.parser import parse_legal_document, save_cleaned
from backend.ingestion.chunker import chunk_document
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline(
    raw_dir: str = None,
    cleaned_dir: str = None,
    chunks_file: str = None
) -> None:
    """
    Chạy pipeline ingestion để parse markdown files, chia chunk, và lưu kết quả.

    Args:
        raw_dir: Thư mục chứa các file markdown thô. Mặc định đọc từ biến môi trường RAW_MD_DIR hoặc 'data/raw/manual_md'.
        cleaned_dir: Thư mục lưu các file JSON đã được clean. Mặc định từ CLEANED_DIR hoặc 'data/cleaned'.
        chunks_file: Đường dẫn file để lưu các chunk dưới dạng JSONL. Mặc định từ CHUNKS_FILE hoặc 'data/chunks.jsonl'.
    """
    raw_dir = raw_dir or os.getenv("RAW_MD_DIR", "data/raw/manual_md")
    cleaned_dir = cleaned_dir or os.getenv("CLEANED_DIR", "data/cleaned")
    chunks_file = chunks_file or os.getenv("CHUNKS_FILE", "data/chunks.jsonl")
    relations_file = os.getenv("RELATIONS_FILE", "data/document_relations.json")
    metadata_file = os.getenv("METADATA_FILE", "data/documents_metadata.json")
    
    os.makedirs(cleaned_dir, exist_ok=True)
    
    # Load document relations
    meta_lookup = {}
    if os.path.exists(relations_file):
        with open(relations_file, 'r', encoding='utf-8') as f:
            doc_relations = json.load(f)
            for rel in doc_relations:
                src = rel.get("source_doc")
                tgt = rel.get("target_doc")
                rtype = rel.get("relation_type")
                scope = rel.get("scope")
                eff_date = rel.get("effective_date")
                
                if src not in meta_lookup:
                    meta_lookup[src] = {"replaces": [], "replaced_by": [], "status": "con_hieu_luc", "effective_date": ""}
                if tgt and tgt not in meta_lookup:
                    meta_lookup[tgt] = {"replaces": [], "replaced_by": [], "status": "con_hieu_luc", "effective_date": ""}
                    
                if eff_date and not meta_lookup[src]["effective_date"]:
                    meta_lookup[src]["effective_date"] = eff_date
                    
                if rtype == "thay_the" and scope == "toan_bo" and tgt:
                    meta_lookup[tgt]["status"] = "het_hieu_luc"
                    if src not in meta_lookup[tgt]["replaced_by"]:
                        meta_lookup[tgt]["replaced_by"].append(src)
                    if tgt not in meta_lookup[src]["replaces"]:
                        meta_lookup[src]["replaces"].append(tgt)
                        
    # Load static document metadata
    static_metadata = {}
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            static_metadata = json.load(f)
            
    md_files = glob.glob(os.path.join(raw_dir, '*.md'))
    logger.info(f"Tìm thấy {len(md_files)} files trong {raw_dir}")
    
    total_chunks = 0
    
    # Mở file chunks dưới dạng write (ghi đè)
    with open(chunks_file, 'w', encoding='utf-8') as f_out:
        for file_path in md_files:
            file_name = os.path.basename(file_path)
            
            # Extract doc_number from file name: Nghị-định-145-2020-NĐ-CP.md -> 145/2020/NĐ-CP
            match = re.search(r'-(\d+-\d+-[A-ZĐa-z0-9-]+)\.md', file_name)
            if match:
                doc_number = match.group(1).replace('-', '/').upper()
            else:
                doc_number = file_name.replace('.md', '')
                
            doc_type = "luat" if "QH" in doc_number else ("nghi_dinh" if "ND" in doc_number or "NĐ" in doc_number else "thong_tu")
            
            doc_meta = {
                "doc_number": doc_number,
                "doc_type": doc_type,
                "doc_title": file_name.replace(".md", "").replace("-", " "),
                "status": "con_hieu_luc",
                "effective_date": "",
                "issue_date": "",
                "signer": "",
                "issuing_body": "",
                "topic_tags": [],
                "replaces": [],
                "replaced_by": []
            }
            
            # Apply static metadata first
            if doc_number in static_metadata:
                sm = static_metadata[doc_number]
                for key in ["effective_date", "issue_date", "signer", "issuing_body", "topic_tags"]:
                    if sm.get(key):
                        doc_meta[key] = sm[key]
            
            # Then apply dynamic relations metadata
            if doc_number in meta_lookup:
                lookup = meta_lookup[doc_number]
                doc_meta["status"] = lookup["status"]
                # Only override effective_date if it wasn't provided statically
                if not doc_meta["effective_date"] and lookup.get("effective_date"):
                    doc_meta["effective_date"] = lookup["effective_date"]
                doc_meta["replaces"] = lookup["replaces"]
                doc_meta["replaced_by"] = lookup["replaced_by"]
            
            try:
                # 1. Parse File
                with open(file_path, 'r', encoding='utf-8') as f_in:
                    md_content = f_in.read()
                cleaned_json = parse_legal_document(md_content, doc_meta)
                
                cleaned_path = os.path.join(cleaned_dir, file_name.replace(".md", ".json"))
                save_cleaned(cleaned_json, cleaned_path)
                
                # 2. Chunking
                chunks = chunk_document(cleaned_json)
                
                # 3. Ghi ra jsonl
                for chunk in chunks:
                    f_out.write(json.dumps(chunk, ensure_ascii=False) + '\n')
                    total_chunks += 1
                
                logger.info(f"Đã xử lý {doc_number}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Lỗi khi xử lý {file_path}: {e}")

    logger.info(f"Hoàn thành. Tổng cộng {total_chunks} chunks được tạo trong {chunks_file}")

if __name__ == "__main__":
    run_pipeline()
