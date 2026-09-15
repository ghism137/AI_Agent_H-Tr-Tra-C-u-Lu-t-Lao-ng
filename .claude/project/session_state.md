# Session State — AI Agent Luật Lao Động

> **Cập nhật lần cuối:** 2026-09-16 — Bắt đầu Phase 2
>
> **Phase hiện tại:** Phase 2 (Retrieval Pipeline - In progress)

---

## Phase 1: Data Foundation (✅ Hoàn tất)

### Tasks

- [x] [2026-09-10] Lập `data/crawl_plan.md` — danh sách ≥30 VB cần crawl
- [x] [2026-09-12] Crawl BLLĐ 2019 (45/2019/QH14)
- [x] [2026-09-15] Tải thủ công NĐ 145/2020/NĐ-CP
- [x] [2026-09-15] Tải thủ công NĐ 12/2022/NĐ-CP
- [x] [2026-09-15] Tải thủ công NĐ 74/2024/NĐ-CP (lương tối thiểu vùng)
- [x] [2026-09-15] Tải thủ công Luật BHXH 2014 (58/2014/QH13)
- [x] [2026-09-15] Tải thủ công NĐ 115/2015/NĐ-CP
- [x] [2026-09-12] Crawl Luật BHYT (25/2008/QH12, 46/2014/QH13)
- [x] [2026-09-15] Tải thủ công Luật Việc làm 2013 (38/2013/QH13)
- [x] [2026-09-15] Tải thủ công NĐ 28/2015/NĐ-CP
- [x] [2026-09-15] Tải thủ công các TT hướng dẫn liên quan
- [x] [2026-09-16] Parse + clean toàn bộ raw -> `data/cleaned/`
- [x] [2026-09-16] Chunking theo Điều -> `data/chunks.jsonl`
- [x] [2026-09-16] Tạo `data/document_relations.json` (Graph Expansion bằng Regex)
- [x] [2026-09-16] **Quality Gate 1:** Reviewer Agent sign-off

### Agent phụ trách: Ingestion Agent → Reviewer Agent

---

## Phase 2: Retrieval Pipeline

### Tasks

- [ ] Setup BGE-M3 embedding (chọn: GPU local / HF API / CPU)
- [ ] Embed toàn bộ chunks → Qdrant local
- [ ] Tạo payload indexes (status, effective_date, doc_type, topic_tags)
- [ ] Build BM25 index
- [ ] Implement hybrid search (BM25 + Dense + RRF)
- [ ] Implement metadata pre-filter (status != "het_hieu_luc")
- [ ] Implement rule-based reranker
- [ ] Implement query processor (entity extraction + expansion)
- [ ] Xây eval set retrieval (≥50 cases)
- [ ] Đo baseline: BM25-only vs Dense-only vs Hybrid
- [ ] **Quality Gate 2:** Precision@5 ≥ 0.70, Recall@5 ≥ 0.80

### Agent phụ trách: RAG Engineer Agent + Eval/QA Agent → Reviewer Agent

---

## Phase 3: Calculation & Drafting *(có thể song song với Phase 2)*

### Calculation Tasks

- [ ] Phân tích Đ.46 BLLĐ 2019 → edge cases trợ cấp thôi việc
- [ ] Implement `tro_cap_thoi_viec.py` + ≥5 unit tests
- [ ] Implement `tro_cap_mat_viec.py` + ≥5 unit tests
- [ ] Implement `luong_thu_viec.py` + ≥5 unit tests
- [ ] Implement `bhtn.py` + ≥5 unit tests
- [ ] Implement `phep_nam.py` + ≥5 unit tests
- [ ] Tạo `config/legal_constants.json` (lương TT vùng, tỷ lệ BHXH)
- [ ] Implement `param_extractor.py` (LLM → Pydantic)

### Drafting Tasks

- [ ] Thiết kế template fields cho 3 mẫu
- [ ] Implement `don_khieu_nai.j2`
- [ ] Implement `hdld_co_ban.j2`
- [ ] Implement `quyet_dinh_cham_dut.j2`
- [ ] Implement `renderer.py` (Jinja2)
- [ ] Implement `exporter.py` (.md → .docx)

### Quality Gate 3: Calc accuracy = 100%, Reviewer sign-off

### Agent phụ trách: Calculation Agent + Drafting Agent → Reviewer Agent

---

## Phase 4: Orchestration & API

### Tasks

- [ ] Thiết kế Pydantic request/response models
- [ ] Setup FastAPI + routers
- [ ] Implement intent_classifier.py (heuristic + LLM fallback)
- [ ] Implement response_assembler.py (citations + disclaimer)
- [ ] Implement llm_client.py (Gemini primary + Groq fallback)
- [ ] Ghép nối: /api/chat end-to-end
- [ ] Integration tests
- [ ] **Quality Gate 4:** 4 intent types OK, latency < 10s

### Agent phụ trách: Orchestration Agent + Eval/QA Agent → Reviewer Agent

---

## Phase 5: Frontend

### Tasks

- [ ] Setup Next.js/Vite project
- [ ] Chat UI + markdown rendering
- [ ] Inline citations + CitationPanel
- [ ] CalcForm (5 loại tính toán)
- [ ] DraftPreview + export .docx
- [ ] Responsive (mobile ≥ 375px)
- [ ] Loading states, error messages, empty states
- [ ] Gợi ý câu hỏi mẫu (welcome screen)
- [ ] API integration
- [ ] **Quality Gate 5:** Full flow hoạt động, responsive OK

### Agent phụ trách: Frontend Agent → Reviewer Agent

---

## Phase 6: Evaluation & Optimization

### Tasks

- [ ] Hoàn thiện eval set (≥90 cases)
- [ ] Chạy full eval suite
- [ ] So sánh 4 baselines (BM25, dense, no-RAG, full)
- [ ] Validate citation accuracy
- [ ] Phân tích failure cases → fix
- [ ] Re-run eval → confirm improvement
- [ ] **Quality Gate 6 (FINAL):** Metrics meet targets, Reviewer sign-off

### Agent phụ trách: Eval/QA Agent + (RAG/Calc/Frontend fix) → Reviewer Agent

---

## Phase 7: Documentation & Packaging

### Tasks

- [ ] Viết báo cáo từng phần
- [ ] Tổng hợp báo cáo cuối
- [ ] README.md hoàn chỉnh
- [ ] Record demo
- [ ] Deploy (nếu cần)

---

## Đang làm

- [x] Đã hoàn thành 100% Phase 1 (Data Foundation).
- Đã trích xuất thành công 2041 chunks từ 107 files.
- Đã chạy `extract_relations.py` tạo `document_relations.json` (104 quan hệ).
- Đang bắt đầu Phase 2 (Retrieval Pipeline): Cần setup BGE-M3 embedding và Qdrant local.

## File đang làm việc

Sắp tới: `backend/retrieval/qdrant_setup.py`, `backend/retrieval/embedding.py`

## Quyết định đã chốt (append-only log)

| Ngày | Quyết định | Lý do |
|---|---|---|
| 2026-09-06 | Embedding model: BGE-M3 | Hybrid dense+sparse native, top VN benchmarks, MIT |
| 2026-09-06 | Vector DB: Qdrant local | Pre-filtering mạnh, Rust performance, payload indexing |
| 2026-09-06 | Chunking: theo Điều (Article-level) | Đơn vị pháp lý tự nhiên, metadata rõ, dễ trích dẫn |
| 2026-09-06 | Retrieval: Hybrid BM25+Dense+RRF | BM25 bắt exact keyword, Dense bắt semantic |
| 2026-09-06 | Reranking: Rule-based (doc_type × recency) | Miễn phí, deterministic, đủ cho giai đoạn đầu |
| 2026-09-06 | Intent classification: Heuristic + LLM fallback | Tiết kiệm 70-80% LLM calls |
| 2026-09-06 | LLM: Gemini Flash primary, Groq fallback | $0 budget |
| 2026-09-06 | Calculation: Python thuần, KHÔNG LLM | Nguyên tắc bất di bất dịch |
| 2026-09-15 | Data Ingestion: Chuyển sang tải thủ công file `.docx` | Dataset HF bị private, web SPA khó crawl, PDF bị lỗi scan không dùng OCR được |
| 2026-09-15 | Tuyệt đối không dùng OCR cho Legal RAG | OCR có rủi ro nhận diện sai số liệu, dấu câu, làm sai lệch cấu trúc Luật |
| 2026-09-16 | Lọc watermark trong Parser | Lọc bỏ từ khóa (thuvienphapluat, luatvietnam) bằng Regex để làm sạch dữ liệu |
| 2026-09-16 | Chunking biểu mẫu / phụ lục | Gom toàn bộ nội dung thành article_number="ALL" (cắt theo độ dài) để giữ nguyên vẹn form template |
| 2026-09-16 | Graph Expansion & Rule-based extraction | Tách context bằng `re.split` (giới hạn scope span tại dấu chấm/chấm phẩy) để chống rò rỉ ngữ cảnh, xuất ra document_relations.json |
| 2026-09-16 | `SEED_RELATIONS` tách riêng trong `relations_builder.py` | Tránh hardcode quan hệ lõi bị overwrite bởi auto-extract; giữ được khi re-run |
| 2026-09-16 | `extract_relations` làm điểm tích hợp duy nhất | Chỉ 1 nơi ghi `document_relations.json`, dễ debug |
| 2026-09-16 | `invalidate_cache()` explicit trong `graph_utils.py` | Caller control rõ ràng hơn TTL tự động |

## Kết quả thực nghiệm

| Metric | Baseline (BM25) | Dense-only | Hybrid | Full Pipeline |
|---|---|---|---|---|
| Precision@5 | — | — | — | — |
| Recall@5 | — | — | — | — |
| MRR | — | — | — | — |
| Temporal Recall@5 | — | — | — | — |
| Citation Precision | — | — | — | — |
| Citation Recall | — | — | — | — |
| Calc Accuracy | — | — | — | — |

## Bugs / Blockers

- 🔴 **Hugging Face Dataset (tmquan/vbpl-vn)**: Bị private (HTTP 401), phải chuyển hoàn toàn sang tải thủ công 19/20 văn bản còn lại.
- ~~🔴 **Chờ dữ liệu thủ công**: Cần user hoàn thành việc tải `.docx` từ `thuvienphapluat.vn` vào `data/raw/manual/`.~~ (Đã fix: 2026-09-15, đã tải và convert 107 file)
