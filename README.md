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


## Nguyên tắc làm việc

1. **Hiểu luật trước, implement sau**: Mọi logic tính toán phải dựa trên văn bản pháp luật gốc (có trích dẫn).
2. **Không dùng LLM để tính toán**: Mọi phép tính số phải dùng code Python. LLM chỉ lấy tham số (Parameter Extraction).
3. **Có disclaimer pháp lý rõ ràng**: Hệ thống cung cấp thông tin tham khảo, không phải tư vấn pháp lý chính thức.

## Dữ liệu pháp luật hiện có (data/cleaned)

Hiện tại, hệ thống đã làm sạch và lưu trữ các văn bản pháp luật sau:

### 1. Các Bộ luật / Đạo luật chính
- **Bộ luật Lao động 2019** (Số 45/2019/QH14)
- **Bộ luật Lao động 2012** (Số 10/2012/QH13)
- **Luật Việc làm 2013** (Số 38/2013/QH13)
- **Luật Công đoàn 2012** (Số 12/2012/QH13)
- **Luật Bảo hiểm xã hội 2014** (Số 58/2014/QH13)
- **Luật An toàn, vệ sinh lao động 2015** (Số 84/2015/QH13)

### 2. Các Nghị định (NĐ-CP)
- **Nghị định 145/2020/NĐ-CP:** Hướng dẫn thi hành BLLĐ về điều kiện lao động và quan hệ lao động.
- **Nghị định 152/2020/NĐ-CP** & **Nghị định 70/2023/NĐ-CP:** Về người lao động nước ngoài làm việc tại Việt Nam.
- **Nghị định 12/2022/NĐ-CP:** Xử phạt vi phạm hành chính trong lĩnh vực lao động, BHXH.
- **Nghị định 135/2020/NĐ-CP:** Quy định về tuổi nghỉ hưu.
- **Nghị định 74/2024/NĐ-CP:** Quy định mức lương tối thiểu.
- **Nghị định 28/2015/NĐ-CP:** Chi tiết Luật Việc làm về bảo hiểm thất nghiệp.
- **Nghị định 115/2015/NĐ-CP:** Chi tiết Luật BHXH về BHXH bắt buộc.
- **Nghị định 143/2018/NĐ-CP:** Chi tiết Luật BHXH cho người lao động nước ngoài tại VN.
- **Nghị định 88/2020/NĐ-CP** & **Nghị định 39/2016/NĐ-CP:** Hướng dẫn thi hành Luật ATVSLĐ.
- **Nghị định 43/2013/NĐ-CP** & **Nghị định 191/2013/NĐ-CP:** Hướng dẫn Luật Công đoàn và Tài chính công đoàn.
- **Nghị định 35/2022/NĐ-CP:** Quản lý khu công nghiệp, khu kinh tế.

### 3. Thông tư và Quyết định liên quan
- **Quyết định 23/2021/QĐ-TTg:** Quy định việc thực hiện một số chính sách hỗ trợ NLĐ gặp khó khăn.
- **Các Thông tư của Bộ LĐ-TB&XH:** 06/2021, 09/2020, 10/2020, 11/2020, 11/2022, 28/2015, 59/2015.

Ngoài ra còn có các biểu mẫu, phụ lục đi kèm (ví dụ: danh mục nghề nghiệp nặng nhọc, lộ trình nghỉ hưu, mẫu đăng ký, ...).
