# Open Issues — AI Agent Luật Lao Động

> **Format**: `[STATUS] [YYYY-MM-DD] [CATEGORY] Tên vấn đề ngắn gọn`
>
> **Categories**: `RETRIEVAL`, `CALCULATION`, `DRAFTING`, `INTEGRATION`, `EVAL`, `FRONTEND`, `ARCHITECTURE`
>
> **Rules**: KHÔNG xóa issue đã log. Khi giải quyết → đổi `[OPEN]` thành `[SOLVED]`, gạch ngang nội dung cũ, thêm Resolution.

---

<!-- Thêm issue mới ở dưới dòng này -->

### [OPEN] [2026-09-16] [ARCHITECTURE] P1 — Registry, coverage và danh tính nguồn (F01/F02/F07/F08)

**Vấn đề:** BLLĐ 2019 có cleaned nhưng 0 chunk trong output; file mang tên BHXH chứa BHYT; 1.225 chunks bị sai số hiệu NĐ/TT/QĐ. 107 DOCX có 5 nhóm basename trùng nhưng khác hash, chỉ còn 102 Markdown. Thiếu cập nhật luật 2025–2026 và provenance.
**Impact:** Q&A/citation/temporal retrieval chưa đủ căn cứ; Gate 1 FAIL.
**Đề xuất:** Registry source/document/version với hash/nguồn đối chiếu; coverage theo thời điểm; khôi phục nguồn và xử lý alias/duplicates trước reparse.
**Evidence:** [Review](../../reports/phase1-review-2026-09-16/review.md), audit JSON cùng thư mục; acceptance theo Gate 1 technical_design v1.2 §8.

**Cập nhật 17/09/2026:** Candidate mới có 258 nguồn, 61 văn bản đã parse, 0 source quarantine và 0 dependency thiếu nguồn; 15 coverage items vẫn pending vì chuỗi sửa đổi/áp dụng theo thời gian chưa duyệt. Năm luật sửa chéo BHYT đã nhập nhưng quan hệ/phiên bản chưa được ký duyệt. Xem `reports/phase1-implementation/gate1_preflight.json` và `reports/phase1-closeout/acquisition_gaps.json`.

### [OPEN] [2026-09-16] [RETRIEVAL] P1 — DOCX numbering và annex/form (F03/F04/F09/F10)

**Vấn đề:** Mất số Điều khi chuyển Word; Luật ATVSLĐ bị gộp ALL; Điều trong mẫu thành Điều luật, 36 nhóm trùng ID; chunk lớn nhất 267.523 ký tự. Watermark filter có reproduction xóa câu hợp lệ; hierarchy không reset đúng.
**Impact:** Citation sai, upsert có thể ghi đè, embedding có nguy cơ truncate.
**Đề xuất:** DOCX extractor có numbering/styles/tables; structural parser, parent/child chunks, token budget và unique IDs; reparse/kiểm chứng raw spans.

### [OPEN] [2026-09-16] [RETRIEVAL] P1 — Cách ly quan hệ suy sai trước khi nối canonical IDs (F05/F06)

**Vấn đề:** 90/95 relations thiếu effective_date, 29 records cần review; regex suy thay toàn NĐ 152 và bãi bỏ toàn NĐ 35 từ NĐ 70; graph bỏ qua review status, sai scope/date. Seed NĐ 35 dùng ngày ban hành thay ngày hiệu lực.
**Impact:** Sửa riêng normalization rồi rebuild có thể khiến graph sai match và vô hiệu hóa cả văn bản.
**Đề xuất:** Candidate/verified lifecycle; evidence/date/locator bắt buộc; dedup theo scope; resolver theo version/interval và golden cases trước publish. Chưa sửa production relations trong phiên review.

### [OPEN] [2026-09-16] [INTEGRATION] P1 — Schema, provenance và publish release (F08/F11)

**Vấn đề:** 2.041 URL rỗng, clause_range không serialize; build ghi đè trước thành công và chỉ log lỗi; relations có hai writer.
**Impact:** Citation không kiểm chứng, partial/stale corpus, BM25/Qdrant có thể không cùng dữ liệu.
**Đề xuất:** Contract v2, staging/release manifest, atomic publish, deterministic ordering, rollback; một entry point ghi verified relations.

### [OPEN] [2026-09-16] [EVAL] P2 — Tests và quality gate theo dữ liệu thực (F12)

**Vấn đề:** 10 tests pass nhưng bỏ qua coverage/identity/temporal truth. P@5 ≥0.70 không khả thi nếu query chỉ có 1 gold; sign-off cũ thiếu evidence.
**Đề xuất:** Regression corpus có nguồn; dev/test độc lập; Recall@5/nDCG@5/MRR@5, temporal leakage, abstention; báo P@5 đúng công thức. Baselines cùng filter, ablation bỏ filter riêng. Design đã sửa; tests/eval/sign-off còn mở.

### [OPEN] [2026-09-16] [RETRIEVAL] P2 — Kiểm chứng BGE-M3 và Qdrant mode

**Vấn đề:** v1.1 nhầm embedded path mode với server payload indexes và hứa hiệu năng/quota chưa đo.
**Đề xuất:** Giữ BGE-M3 1.024 chiều, benchmark token/batch/CPU/GPU; Qdrant server local cho integration, embedded cho smoke. Pin dependencies/model revision. Design v1.2 đã sửa; chưa cài/chạy các dịch vụ.

### [OPEN] [2026-09-16] [CALCULATION] P1 — Rule specs/constants theo phiên bản

**Vấn đề:** Công thức v1.1 có off-by-one phép năm, thiếu eligibility/cap/version BHTN; constants cũ trong ví dụ 2026; mặc định BHTN=0 khi thiếu dữ kiện.
**Đề xuất:** V1.2 §4.5 yêu cầu specs có căn cứ, interval, applicability, rounding và golden cases; missing facts → needs_input. Design đã sửa, legal-rule verification/code Phase 3 chưa triển khai.

### Ghi chú ưu tiên sau yêu cầu người dùng 2026-09-16

Các findings trên vẫn mở. Chi tiết v1.2 là lịch sử review; triển khai theo `phase1_design.md` và `phase2_design.md`, giữ kiến trúc tổng thể trong `technical_design.md`. Ưu tiên nguồn/schema/parser và baseline đơn giản; chưa bắt buộc Qdrant server hoặc toàn bộ cơ chế release nâng cao trước lần đo đầu. Issue về embedded/server chỉ yêu cầu phân biệt đúng khả năng và báo đúng chế độ thử nghiệm.

### [OPEN] [2026-09-17] [ARCHITECTURE] Gate 1 — Xác minh pháp lý và metadata toàn corpus

**Tiến độ:** Staging schema v2 hiện parse 37/37 documents, 2.442 chunks; 15/15 mục coverage tối thiểu có nguồn và parse được. Hash 231 sources khớp file, 0 document quarantine, 14 tests pass. Ba quan hệ hết hiệu lực toàn văn có evidence từ Công báo; 95 legacy relations được cách ly.
**Còn mở:** 37 documents/chunks vẫn ở `verification_status=pending`, title/issued_date/valid_from của nhiều documents chưa được xác minh, 74 sources (chủ yếu Markdown biểu mẫu) chưa map identity, chưa duyệt chuỗi sửa đổi/chuyển tiếp đầy đủ đến thời điểm as-of, chưa đối chiếu thủ công 10 chunk/5 boundary với nguồn chính thức. Không phát hành hoặc dùng staging làm căn cứ tư vấn pháp lý cho đến khi hoàn tất Gate 1.
**Evidence:** `data/staging/phase1-candidate/manifest.json`, `data/registry/coverage.json`, `data/registry/quarantine.json`.

### [OPEN] [2026-09-17] [ARCHITECTURE] P1 — Thiếu chuỗi sửa đổi BHXH trong scope 2026

**Bằng chứng:** VBPL liệt kê Luật 73/2025/QH15 sửa Điều 66 Luật 41/2024/QH15; hồ sơ hợp nhất 58/VBHN-VPQH có Luật 73 và 84/2025. Văn bản Luật 142/2025/QH15 tiếp tục sửa điểm a khoản 1 Điều 37 và nhắc các Luật 73, 84, 113/2025. Xem URL/locator trong `reports/phase1-implementation/gate1_review_2026-09-17.md`.
**Ảnh hưởng:** Coverage BHXH đến tháng 09/2026 chưa thể xác minh. Đây là amendment candidates cần đối chiếu bản gốc, ngày hiệu lực và nhóm đối tượng trước khi ghi verified relations hoặc provision versions.
**Trạng thái:** Gate 1 FAIL; chưa publish.
