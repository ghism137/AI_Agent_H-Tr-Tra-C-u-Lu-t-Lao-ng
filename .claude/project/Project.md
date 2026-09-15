 # Project.md — AI Agent Tra cứu, Soạn thảo & Tính toán Luật Lao động Việt Nam

## 0. Thông tin chung

- **Team size:** 3 người
- **Timeline:** 10 tuần
- **Budget API:** $0 (ưu tiên mô hình mã nguồn mở / free-tier)
- **Định hướng:** đồ án có tính ứng dụng — hướng tới khả năng vận hành thực tế (không chỉ là proof-of-concept)

---

## 1. Project Proposal

### 1.1. Bối cảnh & vấn đề

Người lao động (NLĐ) và người sử dụng lao động/HR (NSDLĐ) tại Việt Nam thường xuyên gặp khó khăn khi tra cứu quyền lợi/nghĩa vụ theo pháp luật lao động vì: (1) văn bản pháp luật phân tán ở nhiều cấp (Bộ luật, Nghị định, Thông tư), (2) việc tính toán quyền lợi (trợ cấp thôi việc, BHTN, phép năm...) đòi hỏi áp dụng đúng công thức pháp lý, dễ tính sai nếu tự làm thủ công, (3) việc soạn thảo văn bản (đơn khiếu nại, hợp đồng, quyết định) đòi hỏi đúng cấu trúc và căn cứ pháp lý.

### 1.2. Mục tiêu tổng thể

Xây dựng một AI Agent dựa trên kiến trúc RAG có khả năng: **tra cứu có trích dẫn**, **tính toán chính xác** (tách biệt khỏi LLM), và **soạn thảo văn bản** trong lĩnh vực luật lao động Việt Nam, phục vụ cả NLĐ và NSDLĐ.

### 1.3. Đối tượng & phạm vi

- **Người dùng:** NLĐ và NSDLĐ/HR
- **Phạm vi luật:** Bộ luật Lao động 2019 + Nghị định hướng dẫn (cốt lõi); BHXH/BHYT/BHTN (cốt lõi); ATVSLĐ, Công đoàn (mở rộng — xem 1.5)
- **Nền tảng:** Web application (responsive, dùng tốt trên di động qua trình duyệt); không build app native riêng trong phạm vi đồ án — xem lý do ở mục 5

### 1.4. Điểm mới / giá trị kỹ thuật

1. Tách biệt rõ 3 module: **Retrieval** (RAG có metadata/temporal filter), **Calculation** (rule-based, không giao phép tính cho LLM), **Drafting** (LLM có kiểm soát template)
2. Xử lý **document versioning theo thời gian** (lương tối thiểu vùng, mức đóng BHXH thay đổi theo từng giai đoạn)
3. Tự xây **bộ eval set riêng cho domain luật lao động** (vì chưa có benchmark public chuyên biệt) — đóng góp có thể tái sử dụng cho nghiên cứu sau này

### 1.5. Phân chia mức độ ưu tiên (với team 3 người, có buffer để mở rộng)

| Mức | Nội dung |
|---|---|
| **Bắt buộc (Core)** | Tra cứu Q&A có trích dẫn (BLLĐ + BHXH/BHYT/BHTN); 4 module tính toán (trợ cấp thôi việc/mất việc, lương thử việc, BHTN, phép năm); 3 mẫu soạn thảo (đơn khiếu nại, HĐLĐ cơ bản, quyết định chấm dứt HĐLĐ); web app hoàn chỉnh; bộ eval tự xây |
| **Mở rộng (nếu tiến độ tốt)** | Thêm ATVSLĐ, Công đoàn vào phạm vi tra cứu; thêm 2-3 mẫu soạn thảo (nội quy lao động, thỏa ước lao động tập thể); tính BHXH một lần |
| **Stretch (nếu rất dư thời gian)** | Multi-turn conversation có nhớ ngữ cảnh; so sánh trước/sau khi luật thay đổi; dashboard thống kê cho HR (nhiều nhân viên) |

---

## 2. Kiến trúc hệ thống

```
                    ┌─────────────────────┐
                    │   User Query (NLĐ/   │
                    │      NSDLĐ)          │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │   Intent Classifier   │  → phân loại: tra cứu / tính toán / soạn thảo / multi-intent
                    └──────────┬───────────┘
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
      ┌───────────────┐ ┌─────────────┐ ┌──────────────┐
      │  RAG Retrieval │ │ Calculation │ │   Drafting    │
      │  (metadata     │ │  Module     │ │   Module      │
      │  filter + rank)│ │ (rule-based,│ │ (LLM + template│
      │                │ │  KHÔNG dùng │ │  có slot điền  │
      │                │ │  LLM tính   │ │  từ dữ liệu    │
      │                │ │  toán số)   │ │  người dùng)   │
      └───────┬────────┘ └──────┬──────┘ └───────┬───────┘
              │                 │                │
              └─────────────────┼────────────────┘
                                 ▼
                    ┌──────────────────────┐
                    │  Response Generator   │  → kèm trích dẫn điều khoản + disclaimer
                    │  (LLM tổng hợp)       │
                    └──────────────────────┘
```

**Nguyên tắc thiết kế cốt lõi:** Module tính toán không giao cho LLM tự tính — LLM chỉ trích xuất tham số đầu vào (số năm làm việc, mức lương...), sau đó gọi hàm rule-based để đảm bảo độ chính xác tuyệt đối về số liệu.

### 2.1. Công thức mẫu cần hard-code (ví dụ)

Trợ cấp thôi việc (Điều 46 BLLĐ 2019):

$$TC_{thoiviec} = \frac{1}{2} \times L_{bq} \times N$$

trong đó $L_{bq}$ là tiền lương bình quân 6 tháng liền kề theo hợp đồng lao động trước khi thôi việc, và $N$ là tổng thời gian làm việc tính trợ cấp (đã trừ thời gian tham gia BHTN và thời gian đã được chi trả trợ cấp trước đó).

---

## 3. Work Packages (WP) — phân chia cho 3 thành viên

Mỗi WP có thể giao cho 1 người phụ trách chính, nhưng có điểm tích hợp chung ở giữa timeline (tuần 5-6) nên cần đồng bộ sớm về format dữ liệu/API contract giữa các module.

### WP1 — Data & Retrieval Pipeline (RAG core)
**Mục tiêu:** Có một hệ thống retrieval hoạt động, trả về đúng điều luật liên quan có xét đến thời gian hiệu lực.
- Thu thập, làm sạch văn bản luật lao động (BLLĐ, Nghị định, BHXH/BHYT/BHTN)
- Thiết kế schema metadata (cấp văn bản, thời gian hiệu lực, phạm vi)
- Chunking theo cấu trúc Điều/Khoản/Điểm (không chunk theo độ dài ký tự)
- Xây embedding + metadata filter + rerank
- *Người phụ trách sẽ cần đào sâu: chọn embedding model tiếng Việt, chiến lược chunking, cách filter theo effective date*

### WP2 — Calculation & Drafting Modules
**Mục tiêu:** Có các hàm tính toán chính xác 100% và các template soạn thảo có thể điền tự động.
- Cài đặt công thức tính (trợ cấp thôi việc, BHTN, lương thử việc, phép năm) dưới dạng hàm kiểm thử được (unit test)
- Thiết kế template văn bản (đơn khiếu nại, HĐLĐ, quyết định chấm dứt) với các slot cần điền
- Xây cơ chế trích xuất tham số từ câu hỏi tự nhiên (NLĐ nói "tôi làm 5 năm, lương 10 triệu" → parse ra `so_nam=5, luong=10000000`)
- *Người phụ trách sẽ cần đào sâu: cách kiểm thử độ chính xác tuyệt đối, cách LLM trích xuất tham số có kiểm soát (structured output/function calling)*

### WP3 — Agent Orchestration, Evaluation & Product (Web)
**Mục tiêu:** Ghép nối các module thành agent hoàn chỉnh, có giao diện dùng được, có số liệu đánh giá thuyết phục.
- Intent classifier (phân loại tra cứu/tính toán/soạn thảo/multi-intent)
- Response generator (tổng hợp kết quả từ các module + trích dẫn + disclaimer)
- Xây bộ eval set riêng cho luật lao động (câu hỏi thực tế + ground truth điều luật/kết quả tính toán)
- Web app (frontend + API layer nối các module)
- *Người phụ trách sẽ cần đào sâu: thiết kế eval set (nguồn câu hỏi, cách gán nhãn), kiến trúc API tách biệt để tái dùng cho web/app sau này*

> **Lưu ý phối hợp:** WP1 và WP2 có thể chạy song song ngay từ tuần 1. WP3 phụ thuộc vào output ban đầu của WP1/WP2 nên tuần 1-2 nên tập trung vào thiết kế API contract (định dạng input/output giữa các module) trước, để không bị nghẽn ở tuần tích hợp.

---

## 4. Timeline dự kiến (10 tuần)

| Tuần | WP1 (Data & Retrieval) | WP2 (Calculation & Drafting) | WP3 (Orchestration & Product) |
|---|---|---|---|
| 1 | Thu thập dữ liệu, thiết kế metadata schema | Liệt kê công thức pháp lý cần cài đặt, thiết kế template văn bản | Thiết kế API contract chung giữa 3 module |
| 2 | Xử lý & chunking theo Điều/Khoản | Cài đặt & unit test các hàm tính toán | Bắt đầu thiết kế bộ eval set (thu thập câu hỏi thực tế) |
| 3 | Xây embedding + vector index | Hoàn thiện template soạn thảo | Khung sườn web app (frontend cơ bản) |
| 4 | Metadata filter + rerank | Cơ chế trích xuất tham số từ câu hỏi tự nhiên | Intent classifier phiên bản đầu |
| 5 | Tinh chỉnh retrieval, đo thử precision/recall | Test end-to-end calculation module | Ghép nối WP1+WP2 vào orchestration |
| 6 | Hỗ trợ tích hợp | Hỗ trợ tích hợp | Response generator, tích hợp toàn bộ pipeline |
| 7 | — | — | Chạy eval toàn hệ thống, ghi nhận lỗi |
| 8 | Sửa lỗi retrieval phát hiện qua eval | Sửa lỗi tính toán/soạn thảo phát hiện qua eval | Tinh chỉnh giao diện, xử lý edge case |
| 9 | Hoàn thiện tài liệu kỹ thuật phần mình | Hoàn thiện tài liệu kỹ thuật phần mình | Hoàn thiện demo, viết báo cáo tổng hợp |
| 10 | Buffer chung + chuẩn bị bảo vệ | Buffer chung + chuẩn bị bảo vệ | Buffer chung + chuẩn bị bảo vệ |

---

## 5. Web / App

Quyết định: **Web app trước, không build app native trong phạm vi đồ án.** Lý do: giá trị kỹ thuật cốt lõi của đồ án nằm ở RAG + calculation + drafting, không nằm ở việc có app native hay không; nếu thiết kế API tách biệt khỏi frontend (như WP3 đề ra), việc mở rộng sang app sau này (ngoài phạm vi đồ án) sẽ không cần viết lại backend.

---

## 6. Nguồn dữ liệu & benchmark tham khảo

- **Văn bản gốc:** Cổng Thông tin điện tử Chính phủ (vanban.chinhphu.vn), Thư viện Pháp luật (thuvienphapluat.vn), Cổng BHXH Việt Nam (baohiemxahoi.gov.vn)
- **Dataset/benchmark tham khảo cho retriever tổng quát** (không chuyên biệt luật lao động, dùng để pretrain/so sánh baseline):
  - Zalo AI Legal Text Retrieval 2021 (`GreenNode/zalo-ai-legal-text-retrieval-vn` trên Hugging Face) — 61.4K văn bản, ~2.4K câu hỏi
  - TVPL dataset — 165.334 câu hỏi train, 10.000 câu hỏi test, 224.006 đoạn văn bản
  - VLQA — 3.129 câu hỏi từ thắc mắc thực tế của người dân, kèm gần 60.000 điều luật
  - VLegal-Bench — benchmark mới thiết kế riêng để đánh giá hệ thống RAG pháp luật Việt Nam
- **Quan trọng:** không có benchmark public nào chuyên biệt cho luật lao động Việt Nam — team **bắt buộc phải tự xây bộ eval set riêng** cho domain này (thuộc WP3)

---

## 7. Phương pháp đánh giá (Evaluation)

- **Retrieval:** Precision/Recall trên bộ eval tự xây (multi-label — một câu hỏi có thể cần nhiều điều luật)
- **Calculation:** So sánh với case tính tay theo văn bản → yêu cầu Accuracy tuyệt đối, không chấp nhận sai số
- **Drafting:** Checklist chuyên gia (đủ điều khoản bắt buộc, điền đúng dữ liệu người dùng)
- **Baseline so sánh bắt buộc:** ít nhất BM25 thuần và LLM không RAG, để chứng minh giá trị của kiến trúc đề xuất

---

## 8. Rủi ro & lưu ý quan trọng

- **Không có benchmark chuyên biệt** → tự xây eval set là công việc chính, không phải phụ, cần bắt đầu sớm (tuần 2) chứ không để cuối
- **Dữ liệu lương/thông tin cá nhân người dùng nhập vào** là dữ liệu nhạy cảm — cần nêu rõ trong báo cáo cách xử lý (không lưu trữ dài hạn, hoặc ẩn danh hóa) theo tinh thần Nghị định 13/2023 về bảo vệ dữ liệu cá nhân
- **Rủi ro pháp lý khi "tư vấn" sai** — cần disclaimer rõ ràng, giới hạn phạm vi trả lời cho các case tổng quát, tránh tư vấn case cụ thể phức tạp
- **RAG là static snapshot** — cần nêu rõ giới hạn "chính xác tới thời điểm crawl X" trong báo cáo, tránh hội đồng tự phát hiện
- **Nếu claim "có tính thương mại"** — nên có ít nhất phân tích sơ bộ chi phí vận hành/query khi scale, vì hội đồng thường hỏi câu này khi thấy claim thương mại hóa
