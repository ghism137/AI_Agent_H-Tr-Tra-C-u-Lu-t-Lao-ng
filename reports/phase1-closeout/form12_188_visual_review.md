# NĐ 188/2025 — Mẫu số 12, đối chiếu trực quan

Ngày review: 2026-09-17. Reviewer: Codex /root. Phạm vi: chỉ Mẫu số 12, không phải toàn bộ NĐ 188 hoặc các mẫu khác.

- PDF Công báo phần tiếp theo: `data/raw/official/188-2025-ND-CP-congbao-part2.pdf`, trang PDF 20. Trang 21 bắt đầu NĐ 190/2025, vì vậy không thuộc Mẫu số 12.
- DOCX người dùng cung cấp: `data/raw/word/2025_979 + 980_188-2025-NĐ-CP.docx`; tiêu đề tại `body/p:367`, đầu mẫu `body/table:368`, bảng danh sách `body/table:374`, chữ ký `body/table:376`, ghi chú `body/p:380`.
- Đối chiếu bản render PDF trang 20 với cấu trúc DOCX: tiêu đề, hai ô đầu trang, dòng tên danh sách, bốn cột `STT / Nhóm đối tượng theo Điều 12 Luật Bảo hiểm y tế / Số lượng / Ghi chú`, các dòng 1–6 và `...`, khối ký, cùng ghi chú cuối trang đều hiện diện. Hàng thứ hai của bảng DOCX là phần tiếp tục của ô gộp dọc; extractor cũ lặp tiêu đề cột. Extractor hiện ghi ô `vMerge=continue` và để hàng này rỗng trong text, giữ metadata ô vật lý để truy ngược.
- Không thấy thiếu nội dung pháp lý của Mẫu 12 sau khi bỏ phần PDF trang 21 trở đi. Đây là sign-off fidelity của mẫu này; hiệu lực và chuỗi sửa đổi BHYT vẫn pending.
