---
name: review-legal-chunking
description: Review chất lượng chunking văn bản pháp luật — kiểm tra cắt đúng Điều/Khoản, metadata đầy đủ, không mất context. Use after Ingestion Agent creates chunks.
---

# Review Legal Chunking

> Dùng sau khi Ingestion Agent tạo chunks, hoặc khi thay đổi chunking strategy.

## Checklist review

### 1. Cấu trúc chunk
- [ ] Mỗi chunk chứa đúng 1 đơn vị pháp lý (1 Điều hoặc 1 nhóm Khoản liên quan)
- [ ] Chunk KHÔNG cắt giữa một Khoản hoặc Điểm
- [ ] Chunk quá dài (>2000 ký tự) đã được chia hợp lý theo nhóm Khoản
- [ ] Tên Chương/Mục/Phần cha được giữ trong metadata `hierarchy_path`
- [ ] Không có chunk trống hoặc chỉ chứa tiêu đề

### 2. Metadata đầy đủ
- [ ] `chunk_id` unique, có thể trace ngược về source
- [ ] `doc_number` đúng format (vd: "45/2019/QH14", "145/2020/NĐ-CP")
- [ ] `effective_date` là ngày hiệu lực, KHÔNG phải ngày ban hành (2 ngày này khác nhau)
- [ ] `status` phản ánh đúng trạng thái hiện tại (con_hieu_luc / het_hieu_luc / sua_doi_bo_sung)
- [ ] `replaces` / `replaced_by` đầy đủ cho các văn bản có quan hệ thay thế
- [ ] `topic_tags` có ít nhất 1 tag phân loại chủ đề
- [ ] `article_number` và `clause_number` (nếu có) chính xác

### 3. Content quality
- [ ] Text không bị mất ký tự đặc biệt (dấu tiếng Việt: ă, â, ê, ô, ơ, ư, đ)
- [ ] Ký hiệu đặc biệt giữ nguyên (§, %, ‰, ≥, ≤)
- [ ] Bảng biểu/phụ lục: giữ nguyên hoặc có reference rõ ràng tới source
- [ ] Không có HTML tags thừa từ quá trình crawl
- [ ] Encoding đúng UTF-8 NFC

### 4. Dedup & consistency
- [ ] Không có chunk trùng lặp nội dung (cùng Điều xuất hiện 2 lần)
- [ ] Nếu cùng Điều có nhiều version (sửa đổi) → mỗi version là chunk riêng, phân biệt bằng metadata

### 5. Sampling test (manual verification)
- Chọn random **10 chunks** → verify thủ công với văn bản gốc trên vanban.chinhphu.vn
- Chọn **5 chunks ở ranh giới** (đầu/cuối Chương, Mục chuyển tiếp) → kiểm tra boundary
- Chọn **3 chunks có quan hệ thay thế** → verify `replaces`/`replaced_by` đúng

## Output

Báo cáo review:
```
## Chunking Quality Report
- Tổng số chunks reviewed: X
- Pass: Y / X
- Findings:
  - [CRITICAL] Chunk ABC cắt giữa Khoản 2 và Khoản 3 của Điều 46
  - [WARNING] Chunk DEF thiếu trường effective_date
  - [INFO] Chunk GHI có thể gộp với chunk JKL (cùng Điều, quá ngắn)
```
