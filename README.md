# AI Agent Tra cứu, Soạn thảo & Tính toán Luật Lao động Việt Nam

Dự án xây dựng một AI Agent dựa trên kiến trúc RAG có khả năng: **tra cứu có trích dẫn**, **tính toán chính xác** (tách biệt khỏi LLM), và **soạn thảo văn bản** trong lĩnh vực luật lao động Việt Nam, phục vụ cả Người lao động (NLĐ) và Người sử dụng lao động/HR (NSDLĐ).

## Tính năng chính (Core Features)

1. **Tra cứu Q&A có trích dẫn**: Truy xuất và trả lời các câu hỏi dựa trên BLLĐ 2019, Luật BHXH, BHYT, BHTN và các văn bản hướng dẫn thi hành.
2. **Tính toán chính xác tuyệt đối (Rule-based)**:
   - Trợ cấp thôi việc / mất việc
   - Lương thử việc
   - Bảo hiểm thất nghiệp
   - Phép năm
   *(Các công thức tính toán được thiết kế bằng hàm deterministic, không giao cho LLM tính toán số liệu để tránh hallucination).*
3. **Soạn thảo văn bản (Drafting)**: Cung cấp các mẫu đơn (Khiếu nại, HĐLĐ cơ bản, Quyết định chấm dứt HĐLĐ,...) và tự động điền các trường thông tin do người dùng cung cấp.

## Kiến trúc hệ thống

Dự án được chia làm 3 modules cốt lõi:
- **Retrieval Pipeline**: Xử lý chunking theo điều luật, nhúng (embedding với BGE-M3), và lưu trữ (Qdrant). Tìm kiếm Hybrid kết hợp Sparse (BM25) và Dense.
- **Calculation & Drafting Module**: Trích xuất tham số từ ngôn ngữ tự nhiên và áp dụng vào các hàm tính toán Python thuần hoặc template Jinja2.
- **Orchestration & Web Frontend**: Hệ thống phân loại intent và tổng hợp response để giao tiếp với người dùng qua Web app (Next.js/Vite).

## Trạng thái dự án (Project Status)

Dự án đang trong quá trình phát triển (Timeline dự kiến 10 tuần).
- [x] **Phase 1: Data Foundation** - Thu thập, làm sạch và chunking >100 văn bản pháp luật, xây dựng đồ thị quan hệ tài liệu.
- [ ] **Phase 2: Retrieval Pipeline** - Đang tiến hành (Setup Qdrant & Embedding).
- [ ] **Phase 3: Calculation & Drafting** - Lên kế hoạch.
- [ ] **Phase 4: Orchestration & API** - Lên kế hoạch.
- [ ] **Phase 5: Frontend** - Lên kế hoạch.
- [ ] **Phase 6: Evaluation & Optimization** - Lên kế hoạch.

## Nguyên tắc làm việc

1. **Hiểu luật trước, implement sau**: Mọi logic tính toán phải dựa trên văn bản pháp luật gốc (có trích dẫn).
2. **Không dùng LLM để tính toán**: Mọi phép tính số phải dùng code Python. LLM chỉ lấy tham số (Parameter Extraction).
3. **Có disclaimer pháp lý rõ ràng**: Hệ thống cung cấp thông tin tham khảo, không phải tư vấn pháp lý chính thức.
