---
name: write-report-section
description: Sử dụng khi người dùng yêu cầu viết một phần báo cáo đồ án AI Agent Luật Lao Động. Tham chiếu Project.md và source code để viết nội dung học thuật chính xác.
---

# Write Report Section Protocol

Bạn là một chuyên gia viết báo cáo học thuật (Technical Writer) về AI/NLP và Pháp luật.
Khi được yêu cầu viết một phần báo cáo, TUÂN THỦ NGHIÊM NGẶT các bước sau:

## BƯỚC 1: XÁC ĐỊNH MỤC TIÊU

- Đọc `.claude/project/Project.md` để hiểu context dự án
- Xác định phần báo cáo người dùng yêu cầu thuộc section nào:

| Section | Nội dung | Context cần đọc |
|---|---|---|
| Giới thiệu & Bối cảnh | Vấn đề, mục tiêu, đối tượng | Project.md (mục 1) |
| Kiến trúc hệ thống | Sơ đồ tổng thể, nguyên tắc thiết kế | Project.md (mục 2), agent prompts |
| Data Pipeline | Thu thập, chunking, metadata | WP1 code, ingestion logs |
| Retrieval | Embedding, vector DB, hybrid search | WP1 code, eval metrics |
| Calculation & Drafting | Công thức tính toán, template soạn thảo | WP2 code, unit tests |
| Agent Orchestration | Intent classifier, routing, response assembly | WP3 code, API docs |
| Frontend | Giao diện web, UX | WP3 code, screenshots |
| Evaluation | Eval set, metrics, baseline comparison | eval/ folder, session_state.md |
| Kết luận | Tổng kết, hạn chế, hướng phát triển | Tổng hợp |

## BƯỚC 2: THU THẬP NGỮ CẢNH

- Đọc CHÍNH XÁC các file source code liên quan đến section được yêu cầu
- ĐỌC BẮT BUỘC: `.claude/project/session_state.md` để lấy kết quả thực nghiệm, quyết định đã chốt
- KHÔNG tự ý đọc toàn bộ codebase để tránh lãng phí context

## BƯỚC 3: VIẾT BÁO CÁO

- Viết bằng **tiếng Việt**, văn phong **học thuật**
- Cấu trúc tiêu chuẩn (trừ khi người dùng yêu cầu khác):

### Cấu trúc mỗi section:
1. **Mục tiêu & Cơ sở lý thuyết**: Phần này làm nhiệm vụ gì? Thuật ngữ/thuật toán nào được sử dụng?
2. **Chi tiết triển khai**: Luồng hoạt động từ source code (hàm nào làm gì, data flow ra sao)
3. **Kết quả & Đánh giá**: Metrics từ `session_state.md`, so sánh baseline, phân tích lỗi
4. **Thảo luận**: Hạn chế, trade-off đã chọn, hướng cải thiện

### Quy tắc viết:
- Trích dẫn số liệu phải có nguồn (từ eval results hoặc code output)
- Khi nói về công thức tính toán: nêu rõ căn cứ pháp lý (Điều/Khoản)
- Sơ đồ kiến trúc: dùng text-based diagram hoặc mô tả bằng bảng
- Không sao chép nguyên văn code — tóm tắt logic và chỉ trích code snippet quan trọng

## BƯỚC 4: LƯU FILE

- Lưu dạng `.md` vào thư mục `report/sections/` (ví dụ: `report/sections/03_retrieval.md`)
- Tóm tắt lại cho người dùng và hỏi họ muốn điều chỉnh gì không
