# Hướng dẫn Vận hành — Operations Guide

> **Mục đích**: Bạn có bản thiết kế trong tay. Bây giờ bạn cần biết **làm gì**, **ai (agent nào) làm**, **theo thứ tự nào**, và **khi nào xong**.
>
> **Tham chiếu**: [Technical Design](file:///C:/Users/Admin/.gemini/antigravity-ide/brain/40338306-b56f-47a0-9d3a-35995e61a424/technical_design.md)

---

## 1. Tổng quan Agent System

### 1.1. Danh sách Agents & Vai trò

| Agent | File prompt | Vai trò chính | Khi nào dùng |
|---|---|---|---|
| **Ingestion Agent** | [ingestion-agent.md](file:///c:/Users/Admin/Project/AI_Agent_Luật_Lao_Động/.claude/agents/ingestion-agent.md) | Thu thập, parse, chunk văn bản pháp luật | Phase 1 |
| **RAG Engineer Agent** | [rag-engineer-agent.md](file:///c:/Users/Admin/Project/AI_Agent_Luật_Lao_Động/.claude/agents/rag-engineer-agent.md) | Embedding, indexing, retrieval pipeline | Phase 2, 6 |
| **Orchestration Agent** | [orchestration-agent.md](file:///c:/Users/Admin/Project/AI_Agent_Luật_Lao_Động/.claude/agents/orchestration-agent.md) | API backend, intent routing, response assembly | Phase 4 |
| **Frontend Agent** | [frontend-agent.md](file:///c:/Users/Admin/Project/AI_Agent_Luật_Lao_Động/.claude/agents/frontend-agent.md) | Web UI, chat interface, citation display | Phase 5, 6 |
| **Eval/QA Agent** | [eval-qa-agent.md](file:///c:/Users/Admin/Project/AI_Agent_Luật_Lao_Động/.claude/agents/eval-qa-agent.md) | Viết test cases, chạy eval suite, đo metrics | Phase 2, 3, 4, 6 |
| **Reviewer Agent** | [reviewer-agent.md](file:///c:/Users/Admin/Project/AI_Agent_Luật_Lao_Động/.claude/agents/reviewer-agent.md) | Review code, verify legal accuracy, sign-off | Cuối mỗi Phase |
| **Calculation Agent** | *(chưa tách, dùng Orchestration Agent)* | Implement công thức tính toán rule-based | Phase 3 |
| **Drafting Agent** | *(chưa tách, dùng Orchestration Agent)* | Implement templates soạn thảo | Phase 3 |
| **RAG Design Agent** | [rag-design-agent-prompt.md](file:///c:/Users/Admin/Project/AI_Agent_Luật_Lao_Động/.claude/agents/rag-design-agent-prompt.md) | Thiết kế kiến trúc RAG, ra quyết định kỹ thuật | Khi cần quyết định architecture |

### 1.2. Ma trận Agent × Phase

```
         Phase 1   Phase 2   Phase 3   Phase 4   Phase 5   Phase 6   Phase 7
         Data      Retrieval Calc/     Orchest.  Frontend  Eval &    Docs
         Found.    Pipeline  Draft     & API              Optimize

Ingestion  ██████    ·         ·         ·         ·         ·         ·
RAG Eng.   ·         ██████    ·         ·         ·         ████      ·
Calc       ·         ·         ██████    ·         ·         ██        ·
Draft      ·         ·         ██████    ·         ·         ·         ·
Orchest.   ·         ·         ·         ██████    ·         ·         ██
Frontend   ·         ·         ·         ·         ██████    ██        ·
Eval/QA    ·         ████      ████      ████      ·         ██████    ·
Reviewer   ██        ██        ██        ██        ██        ██        ·

██████ = Primary (agent chính)
████   = Secondary (hỗ trợ)
██     = Review/Sign-off
·      = Không tham gia
```

---

## 2. Dependency Graph — Thứ tự Bắt buộc

```
Phase 1: Data Foundation
    │
    │  ← PHẢI có chunks.jsonl trước khi làm gì khác
    │
    ├──────────────────────┐
    ▼                      ▼
Phase 2: Retrieval    Phase 3: Calc & Draft
Pipeline                   │
    │                      │
    │  ← CẦN retrieval     │  ← KHÔNG phụ thuộc retrieval
    │    để test end-to-end │    nhưng CẦN legal_constants
    │                      │
    └──────────┬───────────┘
               │
               ▼
        Phase 4: Orchestration & API
               │
               │  ← CẦN tất cả 3 modules hoạt động
               │
               ▼
        Phase 5: Frontend
               │
               │  ← CẦN API endpoints đã sẵn sàng
               │
               ▼
        Phase 6: Eval & Optimization
               │
               │  ← CẦN full pipeline chạy end-to-end
               │
               ▼
        Phase 7: Docs & Packaging
```

> [!IMPORTANT]
> **Phase 2 và Phase 3 có thể chạy SONG SONG** vì chúng không phụ thuộc nhau. Đây là cơ hội để tiết kiệm thời gian nếu có nhiều người làm.

> [!WARNING]
> **Phase 4 PHẢI đợi** cả Phase 2 và Phase 3 hoàn tất, vì Orchestration cần ghép nối tất cả modules.

---

## 3. Hướng dẫn Chi tiết Từng Phase

### 📦 Phase 1: Data Foundation

#### Bắt đầu bằng cách nào?

```
1. Mở project workspace
2. Kích hoạt Ingestion Agent (đọc .claude/agents/ingestion-agent.md)
3. Giao nhiệm vụ đầu tiên
```

#### Prompt gợi ý cho Ingestion Agent

```
Prompt 1 — Lập crawl plan:
"Đọc Technical Design mục 2.1. Dựa trên danh sách 10 văn bản Core,
lập file data/crawl_plan.md với: tên VB, số hiệu, URL nguồn, status crawl.
Bổ sung thêm các TT hướng dẫn liên quan nếu tìm thấy."

Prompt 2 — Crawl:
"Crawl văn bản [số hiệu] từ [URL]. Lưu raw HTML vào data/raw/.
Parse cấu trúc pháp lý (Phần/Chương/Mục/Điều/Khoản/Điểm).
Lưu cleaned JSON vào data/cleaned/."

Prompt 3 — Chunking:
"Đọc Technical Design mục 2.2 (chunking rules). Áp dụng chunking
cho tất cả VB đã cleaned. Output: data/chunks.jsonl với metadata
schema theo mục 2.3. Report: tổng chunks, phân bổ theo doc_type."

Prompt 4 — Document Relations:
"Đọc Technical Design mục 2.4. Tạo data/document_relations.json
chứa quan hệ sửa đổi/thay thế giữa các VB trong corpus.
Đặc biệt chú ý: BLLĐ 2019 thay thế BLLĐ 2012; các NĐ sửa đổi."
```

#### Khi nào gọi Reviewer Agent?

```
Sau khi Ingestion Agent hoàn tất → gọi Reviewer Agent:
"Review chunks.jsonl: sampling 10 random chunks, verify metadata
đúng vs source gốc. Kiểm tra document_relations.json đầy đủ.
Report findings theo Critical/Major/Minor."
```

#### ✅ Checklist Quality Gate 1

```
□ data/crawl_plan.md tồn tại, liệt kê ≥ 30 VB
□ data/raw/ có ≥ 30 files
□ data/cleaned/ có ≥ 30 JSON files
□ data/chunks.jsonl có ≥ 2000 dòng (chunks)
□ Mỗi chunk có đủ 19 metadata fields
□ Sampling 10 random chunks: 10/10 đúng vs source
□ data/document_relations.json tồn tại
□ Reviewer Agent: 0 Critical findings
```

---

### 🔍 Phase 2: Retrieval Pipeline

#### Prerequisite: Phase 1 Quality Gate PASSED

#### Prompt gợi ý cho RAG Engineer Agent

```
Prompt 1 — Setup embedding:
"Đọc Technical Design mục 3.1. Setup BGE-M3 embedding model.
Chọn deployment option phù hợp (GPU local hoặc HF Inference API).
Embed thử 10 chunks đầu tiên, verify vector dimensions = 1024."

Prompt 2 — Index:
"Embed toàn bộ chunks.jsonl và lưu vào Qdrant local.
Theo Technical Design mục 3.2: tạo payload indexes cho
status, effective_date, doc_type, topic_tags.
Song song: build BM25 index từ content text."

Prompt 3 — Hybrid search:
"Đọc Technical Design mục 3.3. Implement hybrid search pipeline
4 bước: Query Processing → Metadata Pre-filter → Hybrid Search
(BM25 + Dense + RRF) → Rule-based Reranking.
Test với 5 queries mẫu, in top 5 results."

Prompt 4 — Query expansion:
"Implement query_processor.py: entity extraction (số hiệu VB,
tên điều khoản) + query expansion (synonym dictionary cho
legal terms). Test: 'Điều 46' → phải match exact."
```

#### Song song: Eval/QA Agent xây eval set

```
Prompt cho Eval/QA Agent:
"Đọc Technical Design mục 5.1. Xây eval_set_v1.json:
- 30 câu tra cứu thông thường
- 15 câu temporal (phải trả VB mới nhất)
- 5 câu negative (ngoài scope)
Format: {query, expected_articles[], expected_doc_numbers[]}"
```

#### ✅ Checklist Quality Gate 2

```
□ Qdrant DB populated với tất cả chunks
□ BM25 index built
□ Hybrid search trả results cho mọi test query
□ Precision@5 ≥ 0.70 trên eval set
□ Recall@5 ≥ 0.80 trên eval set
□ Temporal Recall@5 ≥ 0.80
□ 0 chunks hết hiệu lực trong top 5
□ Latency < 3 giây
□ Hybrid > BM25-only AND > Dense-only
□ Reviewer Agent: 0 Critical findings
```

---

### 🧮 Phase 3: Calculation & Drafting (Song song với Phase 2)

#### Prompt gợi ý cho Calculation Agent

```
Prompt 1 — Phân tích luật:
"Đọc Điều 46 BLLĐ 2019 (trợ cấp thôi việc) + NĐ 145/2020 hướng dẫn.
Liệt kê: công thức, tham số đầu vào, edge cases, ví dụ tính.
Tham khảo Technical Design mục 4.5."

Prompt 2 — Implement:
"Implement hàm tinh_tro_cap_thoi_viec() trong
backend/calculation/tro_cap_thoi_viec.py:
- Input: Pydantic model với validation
- Output: result + formula + breakdown + legal_basis
- Đọc legal_constants.json cho mức lương
- Viết ≥ 5 unit tests (happy, edge, boundary)"

(Lặp lại cho 4 công thức còn lại)

Prompt 3 — Param extractor:
"Implement param_extractor.py: nhận câu hỏi tự nhiên,
gọi LLM (Gemini) để extract structured params → Pydantic model.
Nếu thiếu field bắt buộc → trả danh sách missing_fields."
```

#### Prompt gợi ý cho Drafting Agent

```
Prompt 1 — Templates:
"Đọc Technical Design mục 4.6. Thiết kế 3 Jinja2 templates:
1. Đơn khiếu nại (don_khieu_nai.j2)
2. HĐLĐ cơ bản (hdld_co_ban.j2)
3. Quyết định chấm dứt HĐLĐ (quyet_dinh_cham_dut.j2)
Mỗi template: required fields, optional fields, format VN chuẩn."

Prompt 2 — Renderer + Export:
"Implement renderer.py (Jinja2 render) + exporter.py (.md → .docx).
Test: render template 1 với sample data, export .docx, verify format."
```

#### ✅ Checklist Quality Gate 3

```
□ 5/5 hàm tính toán implemented
□ ≥ 25 unit tests passing (5 per function)
□ Calculation accuracy = 100%
□ legal_constants.json có version + effective_date
□ 3/3 Jinja2 templates created
□ Templates render đúng format VN
□ Param extractor hoạt động ≥ 90%
□ Reviewer Agent: 0 Critical findings
```

---

### 🔌 Phase 4: Orchestration & API

#### Prerequisite: Phase 2 AND Phase 3 Quality Gates PASSED

#### Prompt gợi ý cho Orchestration Agent

```
Prompt 1 — API skeleton:
"Đọc Technical Design mục 1.1 (architecture) + mục 7 (folder structure).
Setup FastAPI app với routers: /api/chat, /api/retrieve,
/api/calculate/{type}, /api/draft/{template}, /api/health.
Định nghĩa Pydantic request/response models."

Prompt 2 — Intent classifier:
"Đọc Technical Design mục 4.1. Implement intent_classifier.py:
- Bước 1: Keyword heuristic (tinh_toan/soan_thao keywords)
- Bước 2: LLM fallback nếu heuristic không chắc
Test: 10 queries mẫu, verify intent đúng."

Prompt 3 — Response assembler:
"Đọc Technical Design mục 4.2 (routing) + 4.4 (citation).
Implement response_assembler.py:
- Tổng hợp output từ retrieval/calc/draft modules
- Parse [N] references → map to chunk_id
- Build citations[] array
- Thêm disclaimer
Test: mock retrieval + mock calc → verify response format."

Prompt 4 — LLM client:
"Implement llm_client.py: Gemini Flash primary, Groq fallback.
Retry logic, rate limit handling, response parsing.
Prompt template theo Technical Design mục 4.3."

Prompt 5 — Integration:
"Ghép nối tất cả: /api/chat nhận query →
intent_classifier → routing → modules → response_assembler.
Test end-to-end: 1 query tra_cuu, 1 tinh_toan, 1 soan_thao."
```

#### ✅ Checklist Quality Gate 4

```
□ GET /api/health → 200
□ POST /api/chat xử lý 4 intent types
□ POST /api/retrieve → chunks + citations
□ POST /api/calculate/tro_cap_thoi_viec → result + breakdown
□ POST /api/draft/don_khieu_nai → rendered document
□ Mọi response có citations[] và disclaimer
□ 400 cho validation errors, 500 cho internal errors
□ Latency < 10 giây full pipeline
□ Intent classifier ≥ 90% accuracy
□ Reviewer Agent: 0 Critical findings
```

---

### 🎨 Phase 5: Frontend

#### Prerequisite: Phase 4 Quality Gate PASSED

#### Prompt gợi ý cho Frontend Agent

```
Prompt 1 — Setup:
"Setup Next.js/Vite project trong frontend/.
Thiết kế layout: sidebar (navigation) + main (chat/calc/draft).
Welcome screen với gợi ý câu hỏi mẫu."

Prompt 2 — Chat UI:
"Implement ChatMessage.tsx: render markdown, inline citations [1]
với tooltip, streaming response (nếu API hỗ trợ).
CitationPanel.tsx: expandable panel, hiển thị doc_number,
article, status badge (✅/⚠️)."

Prompt 3 — Calc UI:
"Implement CalcForm.tsx: dropdown chọn loại tính toán (5 loại),
dynamic form fields per type, submit → hiển thị result +
breakdown table + legal_basis."

Prompt 4 — Draft UI:
"Implement DraftPreview.tsx: chọn template → form fields →
live preview (split view) → export .docx button."

Prompt 5 — Polish:
"Loading states, error messages, empty states, mobile responsive.
Disclaimer component hiện ở mọi response.
Dark mode (nếu có thời gian)."
```

#### ✅ Checklist Quality Gate 5

```
□ Chat: hỏi → loading → trả lời + citations
□ Calc: chọn → điền → kết quả + breakdown
□ Draft: chọn → điền → preview → export
□ Citation: inline [1] + tooltip + panel expandable
□ Responsive: mobile (375px) OK
□ Disclaimer hiển thị
□ 0 console errors, 0 broken layouts
```

---

### 📊 Phase 6: Evaluation & Optimization

#### Prerequisite: Phase 5 Quality Gate PASSED

#### Prompt gợi ý cho Eval/QA Agent

```
Prompt 1 — Final eval set:
"Hoàn thiện eval set: ≥ 90 cases theo Technical Design mục 5.1.
Categories: 30 tra cứu + 15 temporal + 20 tính toán + 10 multi
+ 10 edge cases + 5 negative."

Prompt 2 — Run eval:
"Chạy eval suite trên full pipeline. Đo:
- Retrieval: Precision@5, Recall@5, MRR, Temporal Recall@5
- Calculation: Accuracy
- Citation: Precision, Recall
Lưu results vào eval/eval_report.md."

Prompt 3 — Baselines:
"Chạy 4 baselines theo Technical Design mục 5.3:
B1: BM25 thuần, B2: Dense-only, B3: LLM không RAG, B4: Full pipeline.
So sánh metrics, tạo comparison table."

Prompt 4 — Failure analysis:
"Từ eval results, identify top 10 failure cases.
Phân tích root cause: retrieval miss? wrong intent? hallucination?
Đề xuất fixes → giao cho agent phù hợp."
```

#### Iteration loop

```
┌─► Eval/QA chạy eval
│       │
│       ▼
│   Metrics đạt target? ──── YES → Quality Gate 6 PASS
│       │
│       NO
│       │
│       ▼
│   Phân tích failure cases
│       │
│       ├── Retrieval issue → RAG Engineer fix → ─┐
│       ├── Calc issue → Calculation Agent fix → ──┤
│       └── UI issue → Frontend Agent fix → ───────┤
│                                                   │
└───────────────────────────────────────────────────┘
```

#### ✅ Checklist Quality Gate 6 (FINAL)

```
□ Precision@5 ≥ 0.70
□ Recall@5 ≥ 0.80
□ MRR ≥ 0.70
□ Temporal Recall@5 ≥ 0.80
□ Citation Precision ≥ 0.90
□ Citation Recall ≥ 0.80
□ Calculation Accuracy = 100%
□ Full pipeline > BM25 > LLM-no-RAG
□ Reviewer Agent final sign-off
□ README.md hoàn chỉnh
```

---

### 📝 Phase 7: Documentation & Packaging

#### Prompt gợi ý

```
"Viết báo cáo phần [X] dựa trên:
- Technical Design (kiến trúc + quyết định)
- Eval Report (metrics + baselines)
- Codebase hiện tại
Sử dụng write-report-section skill."
```

---

## 4. Quy trình Xử lý Khi Agent Gặp Vấn Đề

### 4.1. Agent không hiểu nhiệm vụ

```
→ Kiểm tra: Agent đã đọc file prompt (.claude/agents/xxx.md) chưa?
→ Kiểm tra: Agent đã đọc phần Technical Design liên quan chưa?
→ Thử: Chia nhỏ prompt thành steps cụ thể hơn
```

### 4.2. Retrieval quality kém

```
→ Kiểm tra: chunks.jsonl có đúng format không? (Phase 1 issue)
→ Kiểm tra: Qdrant có đủ payload indexes không?
→ Thử: Tăng top_k từ 5 → 10 rồi rerank xuống 5
→ Thử: Kiểm tra BM25 hoạt động riêng → vấn đề ở dense hay sparse?
→ Escalate: Gọi RAG Design Agent để quyết định architecture change
```

### 4.3. Calculation trả sai kết quả

```
→ Kiểm tra: legal_constants.json có đúng version không?
→ Kiểm tra: Edge case nào bị miss? (N < 0.5 năm? Lương = 0?)
→ Đọc lại luật gốc: Điều khoản có thay đổi không?
→ KHÔNG BAO GIỜ fix bằng cách cho LLM tính → luôn fix Python function
```

### 4.4. LLM rate limit (Gemini free tier hết quota)

```
→ Chuyển sang Groq fallback (cấu hình trong llm_client.py)
→ Nếu eval: chia eval set thành batches, chạy qua nhiều ngày
→ Nếu dev: dùng cached responses cho test đã chạy trước
```

---

## 5. Quick Start — Bắt đầu Ngay

### Bước 1: Setup môi trường

```bash
# Clone repo
git clone <repo_url>
cd AI_Agent_Luật_Lao_Động

# Setup Python
python -m venv venv
source venv/bin/activate  # hoặc venv\Scripts\activate trên Windows
pip install -r requirements.txt

# Copy env
cp .env.example .env
# Điền GEMINI_API_KEY, GROQ_API_KEY (nếu có)
```

### Bước 2: Đọc tài liệu

```
1. Đọc Technical Design    → hiểu WHAT (cần build gì)
2. Đọc Operations Guide    → hiểu HOW (làm thế nào)
3. Đọc agent prompts       → hiểu WHO (agent nào làm gì)
```

### Bước 3: Bắt đầu Phase 1

```
1. Mở conversation mới với Ingestion Agent
2. Giao nhiệm vụ: "Lập crawl_plan.md" (xem prompt gợi ý ở mục 3)
3. Khi xong → giao nhiệm vụ tiếp: "Crawl văn bản Core"
4. Khi xong → "Chunking"
5. Khi xong → gọi Reviewer Agent review
6. Check Quality Gate 1
7. Nếu PASS → sang Phase 2
```

### Bước 4: Theo dõi tiến độ

```
Cập nhật session_state.md sau mỗi buổi làm việc:
- Phase hiện tại
- Quality Gate items đã check
- Issues gặp phải
- Quyết định đã lấy
```

---

## 6. Reference Map — Tìm nhanh

| Cần tìm | Xem ở đâu |
|---|---|
| Kiến trúc tổng thể | Technical Design § 1 |
| Metadata schema | Technical Design § 2.3 |
| Chunking rules | Technical Design § 2.2 |
| Embedding model | Technical Design § 3.1 |
| Retrieval pipeline | Technical Design § 3.3 |
| Công thức tính toán | Technical Design § 4.5 |
| Prompt templates | Technical Design § 4.3 |
| Eval metrics & targets | Technical Design § 5.2 |
| Folder structure | Technical Design § 7 |
| Quality Gates | Technical Design § 8 |
| Agent prompts | .claude/agents/*.md |
| Skills | .claude/skills/*.md |
| Rules | .claude/rules/*.md |
| Session tracking | .claude/project/session_state.md |
| Issues | .claude/project/open_issues.md |
