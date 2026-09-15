# Core Principles — AI Agent Luật Lao Động

## Triết lý làm việc

1. **Hiểu luật trước, implement sau**
   Với mọi điều khoản pháp lý (công thức trợ cấp, điều kiện áp dụng, quy trình khiếu nại),
   đọc và hiểu CĂN CỨ PHÁP LÝ gốc TRƯỚC khi viết code.
   Không implement công thức mà không trích dẫn được nguồn điều/khoản cụ thể.

2. **Simple > Clever**
   Code đơn giản, dễ đọc luôn được ưu tiên hơn code "xịn" khó hiểu.
   Đây là đồ án học thuật — clarity quan trọng hơn performance micro-optimization.

3. **Working > Perfect**
   Ưu tiên pipeline chạy được end-to-end trước khi tối ưu từng bước.
   Milestone: mỗi module (retrieval, calculation, drafting) phải demo được RIÊNG LẺ
   trước khi tích hợp.

4. **Tính toán KHÔNG giao cho LLM**
   Mọi phép tính số (trợ cấp thôi việc, BHTN, lương thử việc, phép năm)
   PHẢI dùng hàm rule-based deterministic.
   LLM chỉ trích xuất tham số đầu vào → gọi hàm → trả kết quả.
   Đây là nguyên tắc thiết kế cốt lõi, KHÔNG được vi phạm.

5. **Trích dẫn phải chính xác tuyệt đối**
   Không hallucinate số điều/khoản/điểm.
   Nếu không chắc chắn điều khoản nào áp dụng → nói rõ "cần xác nhận" thay vì đoán.
   Mỗi câu trả lời phải kèm: số hiệu văn bản, điều/khoản, ngày hiệu lực.

6. **Luôn kèm disclaimer pháp lý**
   Hệ thống cung cấp thông tin tham khảo, KHÔNG phải tư vấn pháp lý chính thức.
   Người dùng cần tham vấn luật sư cho tình huống cụ thể/phức tạp.

7. **Nếu tôi sai, hãy phản biện lại một cách lịch sự và đưa ra lý do**
   Đừng chỉ làm theo yêu cầu một cách máy móc.
   Đặc biệt quan trọng khi: hiểu sai điều luật, logic tính toán có lỗ hổng,
   thiết kế kiến trúc có rủi ro.

8. **Nêu rõ giả định**
   Khi thiếu thông tin (ví dụ: quy mô corpus, version LLM cụ thể),
   nêu rõ giả định đang dùng thay vì bỏ qua.
