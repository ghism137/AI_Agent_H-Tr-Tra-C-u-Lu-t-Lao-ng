# AI Agent Luật Lao Động — Project Bootstrap

> **⚡ BẮT ĐẦU TỪ ĐÂY** — Mọi conversation mới PHẢI đọc file này trước.

---

## 🔴 ĐỌC NGAY — Trạng thái dự án

### Phase hiện tại: **Phase 1 — Data Foundation** 🟡 Đang làm *(cập nhật trường này mỗi khi chuyển phase)*

### Tóm tắt tiến độ:

| Phase | Tên | Status | Quality Gate |
|---|---|---|---|
| 1 | Data Foundation | ✅ Hoàn tất | ✅ Đã pass |
| 2 | Retrieval Pipeline | 🟡 Đang làm | ⬜ |
| 3 | Calculation & Drafting | ⬜ Chưa bắt đầu | ⬜ |
| 4 | Orchestration & API | ⬜ Chưa bắt đầu | ⬜ |
| 5 | Frontend | ⬜ Chưa bắt đầu | ⬜ |
| 6 | Evaluation & Optimization | ⬜ Chưa bắt đầu | ⬜ |
| 7 | Documentation & Packaging | ⬜ Chưa bắt đầu | ⬜ |

*Ký hiệu: ⬜ Chưa bắt đầu | 🟡 Đang làm | ✅ Hoàn tất | 🔴 Blocked*

---

## 📋 Quy trình Bootstrap cho Conversation mới

```
BẮT ĐẦU CONVERSATION MỚI:
│
├── BƯỚC 1: Đọc file NÀY (.claude/CLAUDE.local.md)
│   → Biết phase hiện tại + tiến độ tổng quan
│
├── BƯỚC 2: Đọc session_state.md
│   → Biết chi tiết: task nào done, task nào đang làm, blockers
│   → File: .claude/project/session_state.md
│
├── BƯỚC 3: Xác định bạn cần làm gì
│   │
│   ├── Nếu TIẾP TỤC công việc dở:
│   │   → Đọc session_state.md mục "Đang làm" → tiếp tục
│   │
│   ├── Nếu BẮT ĐẦU phase mới:
│   │   → Đọc Operations Guide → tìm Phase tương ứng
│   │   → Đọc agent prompt tương ứng
│   │
│   └── Nếu CẦN HIỂU kiến trúc:
│       → Đọc Technical Design (phần liên quan)
│
└── BƯỚC 4: Khi KẾT THÚC conversation
    → CẬP NHẬT session_state.md (việc đã làm, việc đang dở)
    → CẬP NHẬT file NÀY nếu chuyển phase
```

---

## 🏗️ Mô tả dự án (tóm tắt)

AI Agent hỗ trợ tra cứu, tính toán và soạn thảo liên quan đến **luật lao động Việt Nam**, sử dụng kiến trúc RAG.

### 3 chức năng lõi

| # | Chức năng | Mô tả | Nguyên tắc |
|---|---|---|---|
| 1 | **Tra cứu Q&A** | RAG có trích dẫn nguồn, xử lý temporal validity | Citation phải chính xác tuyệt đối |
| 2 | **Tính toán** | Trợ cấp, BHTN, lương thử việc, phép năm | **Rule-based deterministic, KHÔNG LLM** |
| 3 | **Soạn thảo** | Đơn khiếu nại, HĐLĐ, QĐ chấm dứt | Template + LLM naturalization |

### Ràng buộc

- **Budget: $0** — chỉ dùng free-tier/open-source
- **Tập trung chất lượng** — không giới hạn thời gian hay nhân sự
- **Tính toán KHÔNG giao cho LLM** — dùng hàm Python thuần
- **Trích dẫn phải chính xác** — số hiệu VB, điều/khoản, ngày hiệu lực

---

## 📚 Bản đồ Tài liệu — Tìm ở đâu?

### Tài liệu Thiết kế (Design Documents)

| Tài liệu | Đường dẫn | Nội dung |
|---|---|---|
| **Technical Design** | `.claude/project/technical_design.md` | Kiến trúc, data pipeline, retrieval, calculation, eval strategy |
| **Operations Guide** | `.claude/project/operations_guide.md` | Agent nào làm gì, thứ tự, prompt gợi ý, quality gates |
| **Project Spec** | `.claude/project/Project.md` | Đặc tả dự án gốc |

### Tracking & Status

| File | Đường dẫn | Cập nhật khi nào |
|---|---|---|
| **Session State** | `.claude/project/session_state.md` | Cuối MỖI conversation |
| **Open Issues** | `.claude/project/open_issues.md` | Khi phát hiện bug/blocker |
| **Bootstrap** (file này) | `.claude/CLAUDE.local.md` | Khi chuyển phase |

### Agent Prompts

| Agent | File | Dùng khi |
|---|---|---|
| Ingestion | `.claude/agents/ingestion-agent.md` | Phase 1: crawl, parse, chunk |
| RAG Engineer | `.claude/agents/rag-engineer-agent.md` | Phase 2: embedding, index, retrieval |
| Orchestration | `.claude/agents/orchestration-agent.md` | Phase 4: API, intent router |
| Frontend | `.claude/agents/frontend-agent.md` | Phase 5: Web UI |
| Eval/QA | `.claude/agents/eval-qa-agent.md` | Phase 2-6: test, eval |
| Reviewer | `.claude/agents/reviewer-agent.md` | Cuối mỗi Phase |
| Calculation | `.claude/agents/calculation-agent.md` | Phase 3: công thức |
| Drafting | `.claude/agents/drafting-agent.md` | Phase 3: templates |
| RAG Design | `.claude/agents/rag-design-agent-prompt.md` | Quyết định architecture |

### Rules & Skills

| Loại | Đường dẫn | Nội dung |
|---|---|---|
| Tech Defaults | `.claude/rules/tech_defaults.md` | Stack: FastAPI, Qdrant, BGE-M3, Gemini |
| Workflow | `.claude/rules/workflow.md` | Quy tắc session management |
| Code Style | `.claude/rules/code_style.md` | Coding conventions |
| Legal Accuracy | `.claude/rules/legal_accuracy.md` | Quy tắc trích dẫn pháp luật |
| Skills | `.claude/skills/*.md` | 9 skills chuyên biệt |

---

## 📁 Cấu trúc Thư mục Dự án

> Đây là layout **thực tế** của repo. Cập nhật khi thêm folder/file lớn mới.

```
AI_Agent_Luật_Lao_Động/          ← project root
│
├── .claude/                      ← Cấu hình agent (KHÔNG chứa code)
│   ├── CLAUDE.local.md           ← ⚡ Bootstrap file (file này)
│   ├── agents/                   ← System prompts cho từng agent
│   │   ├── ingestion-agent.md
│   │   ├── rag-engineer-agent.md
│   │   ├── calculation-agent.md
│   │   ├── drafting-agent.md
│   │   ├── orchestration-agent.md
│   │   ├── frontend-agent.md
│   │   ├── eval-qa-agent.md
│   │   ├── reviewer-agent.md
│   │   └── rag-design-agent-prompt.md
│   ├── project/                  ← Tài liệu dự án & tracking
│   │   ├── technical_design.md   ← Thiết kế kỹ thuật chi tiết
│   │   ├── operations_guide.md   ← Agent nào làm gì, thứ tự
│   │   ├── session_state.md      ← Task tracker (cập nhật thường xuyên)
│   │   ├── open_issues.md        ← Bug/blocker tracker
│   │   ├── Project.md            ← Đặc tả gốc
│   │   └── handoff_*.md          ← Handoff notes (tạo khi cần)
│   ├── rules/                    ← Quy tắc bất biến
│   │   ├── tech_defaults.md      ← Tech stack cố định
│   │   ├── workflow.md           ← Quy trình làm việc
│   │   ├── core_principles.md    ← Nguyên tắc cốt lõi
│   │   └── response_format.md    ← Format output
│   └── skills/                   ← Skills tái sử dụng
│       ├── summarize-conversation.md
│       ├── crawl-legal-source.md
│       ├── implement-calculation.md
│       ├── run-eval-suite.md
│       ├── validate-legal-citation.md
│       ├── update-session-state.md
│       └── ...9 skills tổng cộng
│
├── backend/                      ← Python backend (FastAPI)
│   └── ingestion/                ← Phase 1: Data pipeline scripts
│       ├── crawler.py            ← Crawl văn bản từ web
│       ├── parser.py             ← Parse HTML/PDF → JSON
│       ├── chunker.py            ← Chunking theo Điều/Khoản
│       ├── pdf_extractor.py      ← Extract text từ PDF
│       ├── hf_downloader.py      ← Download từ HuggingFace
│       ├── relations_builder.py  ← Xây document_relations.json
│       ├── pipeline.py           ← Orchestrate toàn bộ ingestion
│       └── mock_generator.py     ← Tạo mock data cho testing
│       (Phase 2+: thêm retrieval/, api/, calculation/, drafting/)
│
├── data/                         ← Dữ liệu (KHÔNG commit vào git)
│   ├── raw/                      ← Nguồn gốc thu thập
│   │   ├── hf/                   ← Download từ HuggingFace
│   │   ├── pdf_scan/             ← PDF gốc (nhóm theo năm)
│   │   │   ├── Nghị định 2020/
│   │   │   ├── Nghị định 2021/
│   │   │   ├── Nghị định 2022/
│   │   │   ├── Nghị định 2023/
│   │   │   ├── Nghị định 2024/
│   │   │   └── yeu_cau/          ← VB được yêu cầu crawl riêng
│   │   ├── word/                 ← File .docx gốc
│   │   └── manual/               ← Thêm tay
│   ├── cleaned/                  ← JSON sau khi parse (~34 VB hiện có)
│   │   ├── 45-2019-QH14.json     ← BLLĐ 2019
│   │   ├── 145-2020-ND_CP.json   ← NĐ 145/2020
│   │   └── ...33 VB khác
│   ├── chunks.jsonl              ← ⭐ Output chính của Phase 1
│   ├── document_relations.json   ← Quan hệ sửa đổi/thay thế
│   ├── crawl_plan.md             ← Kế hoạch crawl + status
│   └── ingestion_report.md       ← Báo cáo kết quả ingestion
│       (Phase 2+: thêm qdrant_db/, bm25_index/)
│
├── tests/                        ← Unit tests
│   ├── test_chunker.py
│   └── test_parser.py
│       (Phase 2+: thêm test_retrieval/, test_calculations/)
│
├── eval/                         ← Evaluation (tạo ở Phase 2)
│   ├── eval_set_v1.json
│   └── eval_report_*.md
│
├── frontend/                     ← Next.js/Vite app (tạo ở Phase 5)
│
├── venv/                         ← Python virtual environment (gitignore)
├── requirements.txt              ← Python dependencies
├── .env                          ← Secrets (gitignore) — GEMINI_API_KEY, etc.
├── .env.example                  ← Template .env (commit)
└── README.md
```

### Quy ước đặt tên file cleaned/

```
{số_hiệu}-{năm}-{loại}.json

Ví dụ:
  45-2019-QH14.json     → Luật số 45/2019/QH14 (BLLĐ 2019)
  145-2020-ND_CP.json   → NĐ 145/2020/NĐ-CP
  74-2024-ND_CP.json    → NĐ 74/2024/NĐ-CP (lương TT vùng)
```

---

## ⚡ Quick Reference — Lệnh nhanh

```
# Xem trạng thái hiện tại:
→ Đọc .claude/CLAUDE.local.md (file này)
→ Đọc .claude/project/session_state.md

# Biết cần làm gì tiếp:
→ Đọc .claude/project/operations_guide.md → tìm Phase hiện tại

# Hiểu kiến trúc:
→ Đọc .claude/project/technical_design.md

# Biết agent nào dùng:
→ Xem bảng Agent Prompts ở trên
→ Hoặc đọc Operations Guide mục 1 (Ma trận Agent × Phase)
```
