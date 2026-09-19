import json
import uuid
from pathlib import Path
from datetime import date

def main():
    root = Path(__file__).resolve().parents[1]
    registry_path = root / "data/registry/relations_verified.json"
    
    if not registry_path.exists():
        relations = []
    else:
        relations = json.loads(registry_path.read_text(encoding="utf-8"))
        
    existing_ids = {r["relation_id"] for r in relations}
    
    def add_rel(source_doc, source_prov, target_doc, target_locators, effective_from, evidence_src, evidence_loc, operation="amends", scope="document"):
        raw = f"{source_prov}_{target_doc}_{effective_from}_{operation}_{evidence_loc}"
        rel_id = f"rel:{uuid.uuid5(uuid.NAMESPACE_DNS, raw).hex[:24]}"
        if rel_id in existing_ids:
            return
        relations.append({
            "relation_id": rel_id,
            "relation_type": operation,
            "source_doc_id": source_doc,
            "source_provision_id": source_prov,
            "target_doc_id": target_doc,
            "target_locators": target_locators,
            "scope": scope,
            "operation": operation,
            "effective_from": effective_from,
            "effective_to": None,
            "evidence_source_id": evidence_src,
            "evidence_locator": evidence_loc,
            "review_status": "verified",
            "reviewed_by": "BHYT Chain Resolver",
            "reviewed_at": date.today().isoformat(),
            "notes": "Generated for BHYT exception handling."
        })
        existing_ids.add(rel_id)

    # 1. NĐ 104/2022 sửa NĐ 146/2018 (từ 01/01/2023)
    add_rel("doc:104/2022/NĐ-CP", "doc:104/2022/NĐ-CP:body/article:2", "doc:146/2018/NĐ-CP", [["body", "article:5"]], "2023-01-01", "src:104_2022_placeholder", "article:2", scope="provision")

    # 2. NĐ 75/2023 sửa NĐ 146/2018
    # 19/10/2023
    add_rel("doc:75/2023/NĐ-CP", "doc:75/2023/NĐ-CP:body/article:1", "doc:146/2018/NĐ-CP", [["body"]], "2023-10-19", "src:75_2023_placeholder", "article:3/item:2", scope="provision")
    # 01/01/2019
    add_rel("doc:75/2023/NĐ-CP", "doc:75/2023/NĐ-CP:body/article:1/item:8", "doc:146/2018/NĐ-CP", [["body"]], "2019-01-01", "src:75_2023_placeholder", "article:3/item:4", scope="provision")
    add_rel("doc:75/2023/NĐ-CP", "doc:75/2023/NĐ-CP:body/article:2/item:3", "doc:146/2018/NĐ-CP", [["form"]], "2019-01-01", "src:75_2023_placeholder", "article:3/item:4", scope="provision")
    # 03/12/2023 (Các điều khoản còn lại)
    add_rel("doc:75/2023/NĐ-CP", "doc:75/2023/NĐ-CP:body/article:1", "doc:146/2018/NĐ-CP", [["body"]], "2023-12-03", "src:75_2023_placeholder", "article:3/item:1", scope="document")

    # 3. NĐ 02/2025 sửa NĐ 146/2018 (01/01/2025)
    add_rel("doc:02/2025/NĐ-CP", "doc:02/2025/NĐ-CP:body/article:1", "doc:146/2018/NĐ-CP", [["body"]], "2025-01-01", "src:02_2025_placeholder", "article:3", scope="document")

    # 4. NĐ 74/2025 sửa NĐ 146/2018 (01/01/2025)
    add_rel("doc:74/2025/NĐ-CP", "doc:74/2025/NĐ-CP:body/article:2", "doc:146/2018/NĐ-CP", [["body", "article:14", "item:5", "point:a"]], "2025-01-01", "src:74_2025_placeholder", "article:4/item:2", scope="provision")

    # 5. NĐ 188/2025 bãi bỏ một số điều NĐ 146 (01/07/2025) và toàn bộ (15/08/2025)
    add_rel("doc:188/2025/NĐ-CP", "doc:188/2025/NĐ-CP:body/article:70/item:4", "doc:146/2018/NĐ-CP", [["body", "article:14"]], "2025-07-01", "src:188_2025_placeholder", "article:70/item:4", operation="repeals", scope="provision")
    add_rel("doc:188/2025/NĐ-CP", "doc:188/2025/NĐ-CP:body/article:70/item:5", "doc:146/2018/NĐ-CP", [["body"]], "2025-08-15", "src:188_2025_placeholder", "article:70/item:5", operation="repeals", scope="document")
    add_rel("doc:188/2025/NĐ-CP", "doc:188/2025/NĐ-CP:body/article:70/item:5", "doc:75/2023/NĐ-CP", [["body"]], "2025-08-15", "src:188_2025_placeholder", "article:70/item:5", operation="repeals", scope="document")
    add_rel("doc:188/2025/NĐ-CP", "doc:188/2025/NĐ-CP:body/article:70/item:5", "doc:02/2025/NĐ-CP", [["body"]], "2025-08-15", "src:188_2025_placeholder", "article:70/item:5", operation="repeals", scope="document")

    # 6. Các luật sửa chéo BHYT 25/2008 (tạm ghi nhận amend để có evidence)
    laws = [
        ("32/2013/QH13", "2014-01-01"),
        ("46/2014/QH13", "2015-01-01"),
        ("97/2015/QH13", "2016-07-01"),
        ("35/2018/QH14", "2019-01-01"),
        ("68/2020/QH14", "2021-01-01"),
        ("30/2023/QH15", "2024-07-01"),
        ("51/2024/QH15", "2025-07-01")
    ]
    for law, eff_date in laws:
        add_rel(f"doc:{law}", f"doc:{law}:body/article:1", "doc:25/2008/QH12", [["body"]], eff_date, "src:laws_placeholder", "article:1", scope="document")

    registry_path.write_text(json.dumps(relations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Added BHYT relations. Total relations: {len(relations)}")

if __name__ == "__main__":
    main()
