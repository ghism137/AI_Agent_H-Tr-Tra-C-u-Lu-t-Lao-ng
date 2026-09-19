# Response Format — AI Agent Luật Lao Động

## Ngôn ngữ
- Giao tiếp: **tiếng Việt**
- Code comments: tiếng Anh (convention chuẩn)
- Tên biến, hàm, class: tiếng Anh (snake_case cho Python)
- Tên file/folder: tiếng Anh, kebab-case

## Khi trích dẫn pháp luật

Luôn theo format chuẩn:
> **Điều X, Khoản Y, Điểm Z** — Tên văn bản (Số hiệu: XX/YYYY/..., có hiệu lực từ DD/MM/YYYY)

Ví dụ:
> **Điều 46, Khoản 1** — Bộ luật Lao động 2019 (Số: 45/2019/QH14, hiệu lực từ 01/01/2021)

## Khi giải thích công thức pháp lý

Theo thứ tự:
1. **Căn cứ pháp lý** — điều/khoản nào quy định
2. **Công thức** — viết rõ ràng, định nghĩa mọi biến
3. **Ví dụ số** — tính tay với case cụ thể (lương 10 triệu, 5 năm làm việc...)
4. **Code** — implement hàm rule-based
5. **Edge cases** — trường hợp đặc biệt cần lưu ý

## Khi viết code

- Code block với syntax highlighting
- Comment giải thích business logic (WHY, không phải WHAT)
- Nếu thay đổi file có sẵn: chỉ show phần thay đổi + context đủ để hiểu vị trí
- Mọi hàm tính toán phải có docstring nêu rõ căn cứ pháp lý

## Khi đề xuất cách làm và chia task

- Chọn mặc định hợp lý trong scope/contract đã được giao, nêu ngắn lý do và trade-off quan trọng.
- Không hỏi xác nhận lại chỉ vì task hơn 3 bước. Chỉ hỏi khi thiếu dữ kiện ảnh hưởng kết quả hoặc có quyết định ngoài phạm vi được giao.
- Với Phase 2: dùng task card + Project Guide; không viết lại toàn plan ở mỗi phản hồi.
- Handoff gồm kết quả, files, kiểm tra, blocker; log dài lưu file. Không biến báo cáo builder thành independent sign-off.

## Khi gặp điều chưa chắc chắn

Nói rõ "Tôi không chắc về X" thay vì hallucinate.
Đặc biệt với: nội dung điều luật cụ thể, mức lương tối thiểu vùng hiện hành,
tỷ lệ đóng BHXH hiện tại (thay đổi theo năm).

## Độ dài phản hồi

- Câu hỏi đơn giản → ngắn gọn, đi thẳng vào vấn đề
- Giải thích pháp lý → đầy đủ, kèm trích dẫn nguồn
- Review code → structured: [VẤN ĐỀ] → [LÝ DO] → [GỢI Ý SỬA]
- Thiết kế kiến trúc → quyết định, contract và task cards đủ triển khai; chỉ thêm sơ đồ/so sánh khi giúp hiểu.
