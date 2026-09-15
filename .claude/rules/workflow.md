# Workflow — AI Agent Luật Lao Động

## Đầu phiên làm việc

1. Đọc `session_state.md` để nắm context hiện tại
2. Xác nhận task hôm nay thuộc WP nào (WP1/WP2/WP3)
3. Kiểm tra `open_issues.md` xem có blocker nào liên quan không

## Trong phiên làm việc

### Khi viết code mới
1. Xác định module (retrieval / calculation / drafting / orchestration / frontend)
2. Kiểm tra API contract đã thống nhất chưa (input/output format giữa các module)
3. Viết code → viết test → chạy test → commit

### Khi thay đổi calculation module
- PHẢI chạy toàn bộ unit test sau khi thay đổi
- PHẢI nêu rõ căn cứ pháp lý cho mọi công thức
- KHÔNG merge nếu có test fail

### Khi thay đổi retrieval pipeline
- Chạy eval set retrieval (precision/recall) trước và sau thay đổi
- Ghi nhận metric vào `session_state.md`

### Khi gặp vấn đề kiến trúc / design decision
- Log vào `open_issues.md` với format `[OPEN]`
- Phân loại: `[RETRIEVAL]`, `[CALCULATION]`, `[DRAFTING]`, `[INTEGRATION]`, `[EVAL]`

## Cuối phiên làm việc

1. Cập nhật `session_state.md`:
   - Đánh dấu task hoàn thành `[x]`
   - Cập nhật "Đang làm" cho phiên tiếp theo
   - Ghi nhận quyết định quan trọng (append-only)
2. Commit code với message rõ ràng
3. Nếu có vấn đề chưa giải quyết → log vào `open_issues.md`

## Quy trình tích hợp (tuần 5-6)

- WP1 output: API endpoint `/api/retrieve` → trả JSON chunks có metadata
- WP2 output: API endpoint `/api/calculate/{type}` và `/api/draft/{template}`
- WP3 input: nhận output từ WP1+WP2, orchestrate thành response hoàn chỉnh
- Đồng bộ API contract TRƯỚC khi code — thống nhất schema request/response

## Git workflow

- Branch naming: `wp1/feature-name`, `wp2/feature-name`, `wp3/feature-name`
- PR review: cross-WP review khi thay đổi ảnh hưởng API contract
- Main branch: chỉ merge khi tests pass
