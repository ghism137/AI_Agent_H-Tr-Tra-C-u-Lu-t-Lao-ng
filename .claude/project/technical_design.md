# Bản Thiết kế Kỹ thuật — AI Agent Luật Lao Động Việt Nam

> **Version:** 1.1 — 2026-09-06 (updated: bỏ ràng buộc thời gian/người, tập trung chất lượng)
> **Tác giả:** RAG Solutions Architect
> **Input:** [Project.md](file:///c:/Users/Admin/Project/AI_Agent_Luật_Lao_Động/.claude/project/Project.md) + [rag-design-agent-prompt.md](file:///c:/Users/Admin/Project/AI_Agent_Luật_Lao_Động/.claude/agents/rag-design-agent-prompt.md)

---

## 0. Giả định (Assumptions)

Trước khi đọc, cần nắm các giả định quan trọng ảnh hưởng đến thiết kế:

| # | Giả định | Lý do |
|---|---|---|
| A1 | Corpus ≈ 50-80 văn bản pháp luật → ≈ 3.000-5.000 chunks | Phạm vi Core (BLLĐ 2019 + ~30 NĐ/TT hướng dẫn + BHXH/BHYT/BHTN) |
| A2 | Máy dev có GPU tối thiểu 4GB VRAM hoặc dùng CPU inference | Nếu không có GPU → dùng free inference API (HuggingFace/Groq) |
| A3 | Gemini free tier: ~15 RPM, ~1.500 RPD | Đủ cho dev + eval; bottleneck nếu chạy eval set lớn |
| A4 | Mọi văn bản trong scope đều có bản text trên vanban.chinhphu.vn hoặc thuvienphapluat.vn | Chưa verify 100%, cần confirm ở Phase 1 |
| A5 | Không giới hạn thời gian hay nhân sự — tập trung vào chất lượng sản phẩm | Mục tiêu: sản phẩm tốt nhất có thể, không phải MVP |

---

## 1. Kiến trúc Tổng thể (Architecture Overview)

### 1.1. Sơ đồ luồng xử lý

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js / React)                   │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐                 │
│  │ Chat UI  │  │ Calc Forms   │  │ Draft Preview  │                 │
│  │ + Citation│  │ + Breakdown  │  │ + Export .docx │                 │
│  └─────┬────┘  └──────┬───────┘  └───────┬───────┘                 │
└────────┼───────────────┼─────────────────┼──────────────────────────┘
         │               │                 │
         └───────────────┼─────────────────┘
                         │  HTTP (REST JSON)
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python 3.11+)                  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    API Gateway Layer                          │   │
│  │  POST /api/chat │ /api/retrieve │ /api/calculate │ /api/draft│   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                              │                                      │
│  ┌───────────────────────────▼───────────────────────────────────┐  │
│  │                   INTENT CLASSIFIER                           │  │
│  │     query → {intent: tra_cuu|tinh_toan|soan_thao|multi}      │  │
│  │     + extracted entities (số hiệu VB, params tính toán)       │  │
│  └───┬──────────────────┬──────────────────────┬─────────────────┘  │
│      │                  │                      │                    │
│      ▼                  ▼                      ▼                    │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────┐              │
│  │ RETRIEVAL  │  │ CALCULATION  │  │   DRAFTING      │              │
│  │ MODULE     │  │ MODULE       │  │   MODULE        │              │
│  │            │  │              │  │                 │              │
│  │ BM25 ──┐  │  │ Pydantic     │  │ Template engine │              │
│  │ Dense ─┤  │  │ Input Valid.  │  │ (Jinja2)        │              │
│  │ RRF ───┘  │  │ Rule-based   │  │ + LLM natural-  │              │
│  │ Meta      │  │ Functions    │  │   ization       │              │
│  │ Filter    │  │ (Python      │  │                 │              │
│  │ Rerank    │  │  thuần)      │  │ Export .docx    │              │
│  └─────┬─────┘  └──────┬───────┘  └────────┬────────┘              │
│        │               │                   │                        │
│        └───────────────┬┘───────────────────┘                       │
│                        │                                            │
│  ┌─────────────────────▼────────────────────────────────────────┐   │
│  │              RESPONSE ASSEMBLER                              │   │
│  │  • Tổng hợp output từ modules                                │   │
│  │  • Gắn citations[] (từ retrieved chunks)                     │   │
│  │  • Thêm disclaimer pháp lý                                   │   │
│  │  • Format markdown cho frontend                               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    DATA LAYER                                 │   │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────────────────────┐  │   │
│  │  │ Qdrant   │  │ BM25      │  │ legal_constants.json     │  │   │
│  │  │ (vectors │  │ Index     │  │ (lương TT vùng, tỷ lệ    │  │   │
│  │  │ +metadata│  │ (rank_bm25│  │  đóng BHXH, lương cơ sở) │  │   │
│  │  │ +payload)│  │  library) │  │                          │  │   │
│  │  └──────────┘  └───────────┘  └──────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2. Nguyên tắc thiết kế then chốt

| # | Nguyên tắc | Lý do |
|---|---|---|
| P1 | **Separation of Concerns** — 3 module lõi (Retrieval, Calculation, Drafting) tách biệt hoàn toàn, giao tiếp qua Pydantic models | Cho phép develop + test từng module độc lập |
| P2 | **Calculation = deterministic** — LLM chỉ extract params, KHÔNG tính toán | Công thức pháp lý không được phép sai số |
| P3 | **Temporal-first retrieval** — metadata filter `status` TRƯỚC khi rank | Tránh trả kết quả hết hiệu lực (critical bug) |
| P4 | **Citation-grounded generation** — LLM chỉ được trả lời dựa trên retrieved chunks, kèm reference | Tránh hallucination số điều/khoản |
| P5 | **Modular API** — mỗi module expose riêng endpoint | Frontend có thể gọi trực tiếp `/calculate` mà không qua chat |

---

## 2. Data Pipeline

### 2.1. Nguồn dữ liệu & thu thập

| Nguồn | URL | Ưu tiên | Lý do chọn | Lý do hạn chế |
|---|---|---|---|---|
| **vanban.chinhphu.vn** | vanban.chinhphu.vn | 🥇 Primary | Chính thống nhất, miễn phí, text clean | UI phức tạp, pagination khó parse |
| **thuvienphapluat.vn** | thuvienphapluat.vn | 🥈 Secondary | Phong phú, có consolidated version | Anti-scraping, rate limit |
| **baohiemxahoi.gov.vn** | baohiemxahoi.gov.vn | 🥉 Specific | Chuyên biệt BHXH/BHYT/BHTN | Ít văn bản hơn |

**Crawling strategy:**

```python
# Pseudocode
for doc in crawl_plan:
    raw_html = crawl_with_delay(doc.url, delay=2s)  # respect rate limit
    save_raw(raw_html, f"data/raw/{doc.doc_number}.html")
    cleaned = parse_legal_structure(raw_html)         # BeautifulSoup4
    validate(cleaned, required_fields=[...])
    save_cleaned(cleaned, f"data/cleaned/{doc.doc_number}.json")
```

**Danh sách văn bản Core cần crawl (tuần 1):**

| # | Văn bản | Số hiệu | Vai trò |
|---|---|---|---|
| 1 | Bộ luật Lao động 2019 | 45/2019/QH14 | Luật gốc — nền tảng |
| 2 | NĐ hướng dẫn BLLĐ | 145/2020/NĐ-CP | Chi tiết BLLĐ |
| 3 | NĐ về HĐLĐ, đào tạo, kỷ luật | 12/2022/NĐ-CP | Bổ sung BLLĐ |
| 4 | NĐ về lương tối thiểu (mới nhất) | 74/2024/NĐ-CP | Mức lương TT vùng |
| 5 | Luật BHXH 2014 | 58/2014/QH13 | BHXH cốt lõi |
| 6 | NĐ hướng dẫn Luật BHXH | 115/2015/NĐ-CP | Chi tiết BHXH |
| 7 | Luật BHYT 2008 (sửa đổi 2014) | 25/2008/QH12, 46/2014/QH13 | BHYT |
| 8 | Luật Việc làm 2013 (phần BHTN) | 38/2013/QH13 | BHTN |
| 9 | NĐ hướng dẫn BHTN | 28/2015/NĐ-CP | Chi tiết BHTN |
| 10-30+ | Các TT hướng dẫn liên quan | ... | Bổ trợ |

> **Deliverable tuần 1:** File `data/crawl_plan.md` liệt kê đầy đủ + status crawl

### 2.2. Chunking Strategy

> [!IMPORTANT]
> Đây là quyết định thiết kế quan trọng nhất của Data Pipeline. Chunking SAI sẽ ảnh hưởng domino lên toàn bộ retrieval quality.

#### Trade-off table: Chunking approaches

| Approach | Mô tả | Ưu điểm | Nhược điểm | **Verdict** |
|---|---|---|---|---|
| **🏆 Theo Điều (Article-level)** | 1 chunk = 1 Điều. Nếu Điều > 2000 ký tự → chia theo nhóm Khoản liên quan | Đơn vị pháp lý tự nhiên, metadata rõ ràng, dễ trích dẫn | Một số Điều ngắn (< 100 ký tự) → vector embedding kém | **CHỌN** |
| Theo đoạn (Paragraph) | Cắt theo `\n\n` | Đơn giản | Mất cấu trúc Điều/Khoản, khó trích dẫn chính xác | Loại |
| Theo token count (512/1024) | Fixed-size chunks | Phổ biến trong RAG thông thường | Cắt giữa Khoản, mất context pháp lý | Loại |
| Theo Khoản (Clause-level) | 1 chunk = 1 Khoản | Granularity cao | Quá nhiều chunks nhỏ, context hẹp, embedding kém | Backup |

#### Quy tắc chunking chi tiết

```
QUY TẮC CHUNKING:
┌──────────────────────────────────────────────────────┐
│ 1. Chunk cơ bản = 1 Điều (Article)                    │
│                                                       │
│ 2. Nếu len(Điều) > 2000 chars:                        │
│    → Chia theo NHÓM KHOẢN liên quan                   │
│    → Giữ heading Điều trong mỗi sub-chunk             │
│    → KHÔNG BAO GIỜ cắt giữa một Khoản/Điểm           │
│                                                       │
│ 3. Nếu len(Điều) < 100 chars:                         │
│    → Giữ nguyên (không gộp với Điều khác)              │
│    → Thêm context: tên Chương/Mục vào content          │
│                                                       │
│ 4. Mỗi chunk giữ hierarchy_path trong metadata:       │
│    "Phần II > Chương III > Mục 3 > Điều 46"           │
│                                                       │
│ 5. Tham chiếu chéo: nếu Điều A nhắc "theo Điều B"    │
│    → ghi cross_references: ["Điều B"] trong metadata  │
└──────────────────────────────────────────────────────┘
```

### 2.3. Metadata Schema

```json
{
  "chunk_id": "BLLĐ2019_D46_K1-K3",
  "doc_type": "luat",                            // luat | nghi_dinh | thong_tu | cong_van | quyet_dinh
  "doc_number": "45/2019/QH14",
  "doc_title": "Bộ luật Lao động",
  "issued_date": "2019-11-20",                   // ngày ban hành
  "effective_date": "2021-01-01",                 // ngày CÓ HIỆU LỰC (≠ issued_date!)
  "expiry_date": null,                            // null = còn hiệu lực
  "status": "con_hieu_luc",                       // con_hieu_luc | het_hieu_luc | sua_doi_bo_sung
  "replaces": ["10/2012/QH13"],                   // văn bản bị thay thế
  "replaced_by": [],                              // văn bản thay thế (cập nhật khi có NĐ/TT mới)
  "hierarchy_path": "Chương III > Mục 3 > Điều 46",
  "article_number": 46,
  "clause_range": "K1-K3",                        // null nếu chunk = cả Điều
  "topic_tags": ["tro_cap_thoi_viec", "cham_dut_hdld"],
  "cross_references": ["Điều 34", "Điều 47"],
  "content": "Nội dung chunk...",
  "content_length": 450,
  "source_url": "https://vanban.chinhphu.vn/...",
  "crawled_at": "2026-09-10T10:30:00Z"
}
```

> [!TIP]
> Trường `effective_date` và `status` là **hai trường quan trọng nhất** cho temporal filtering. Cần đặc biệt cẩn thận phân biệt `issued_date` (ngày ban hành) vs `effective_date` (ngày có hiệu lực) — hai ngày này thường cách nhau vài tháng.

### 2.4. Xử lý Temporal Validity (Quan hệ sửa đổi/thay thế)

Đây là **core technical challenge** của project (xem mục 3 trong agent prompt).

#### Mô hình quan hệ giữa văn bản

```
┌─────────────────┐     thay_the      ┌─────────────────┐
│ BLLĐ 2012       │ ◄──────────────── │ BLLĐ 2019       │
│ (10/2012/QH13)  │                   │ (45/2019/QH14)  │
│ status:         │                   │ status:         │
│  het_hieu_luc   │                   │  con_hieu_luc   │
└─────────────────┘                   └─────────────────┘

┌─────────────────┐   sua_doi_bo_sung  ┌─────────────────┐
│ NĐ 145/2020     │ ◄──────────────── │ NĐ 35/2022      │
│ (một số điều)   │                   │ (sửa đổi NĐ 145)│
│ status:         │                   │ status:         │
│  sua_doi_bo_sung│                   │  con_hieu_luc   │
└─────────────────┘                   └─────────────────┘
```

#### File quan hệ: `data/document_relations.json`

```json
[
  {
    "source_doc": "45/2019/QH14",
    "relation": "thay_the",
    "target_doc": "10/2012/QH13",
    "effective_date": "2021-01-01",
    "scope": "toan_bo",
    "note": "BLLĐ 2019 thay thế toàn bộ BLLĐ 2012"
  },
  {
    "source_doc": "35/2022/NĐ-CP",
    "relation": "sua_doi_bo_sung",
    "target_doc": "145/2020/NĐ-CP",
    "effective_date": "2022-07-15",
    "scope": "mot_so_dieu",
    "affected_articles": [5, 8, 12],
    "note": "Sửa đổi Điều 5, 8, 12 của NĐ 145/2020"
  }
]
```

#### Quy trình cập nhật khi có văn bản mới

```
1. Ingestion Agent phát hiện văn bản mới (hoặc team thêm thủ công)
2. Parse văn bản mới → tạo chunks mới (status: "con_hieu_luc")
3. Đọc phần "Điều khoản thi hành" → xác định quan hệ sửa đổi/thay thế
4. Cập nhật metadata chunks cũ:
   - Nếu thay thế toàn bộ: status → "het_hieu_luc", replaced_by += [doc mới]
   - Nếu sửa đổi một phần: status → "sua_doi_bo_sung" (chỉ chunks bị ảnh hưởng)
5. Ghi quan hệ vào document_relations.json
6. Embed + index chunks mới vào Qdrant (incremental, KHÔNG rebuild)
7. Cập nhật metadata payload của chunks cũ trong Qdrant
```

> [!IMPORTANT]
> Đây là quy trình manual trong MVP. Không build auto-detection cho quan hệ sửa đổi — quá phức tạp cho 10 tuần. Team verify bằng tay khi thêm văn bản mới.

---

## 3. Indexing & Retrieval

### 3.1. Lựa chọn Embedding Model

#### Trade-off table

| Model | Dim | Vietnamese Support | Hybrid (Dense+Sparse) | Self-host? | License | **Verdict** |
|---|---|---|---|---|---|---|
| **🏆 BAAI/bge-m3** | 1024 | ✅ Excellent (100+ langs) | ✅ Dense + Sparse + ColBERT | ✅ Local / HF Inference | MIT | **CHỌN** |
| intfloat/multilingual-e5-base | 768 | ✅ Good | ❌ Dense only | ✅ | MIT | Backup |
| Jina Embeddings v3 | 1024 (truncatable) | ✅ Good | ❌ Dense only | ✅ | Apache 2.0 | Phức tạp hơn cần |
| PhoBERT | 768 | ✅ Vietnamese-specific | ❌ | ✅ | MIT | Không optimize cho retrieval |

#### Lý do chọn BGE-M3

1. **Hybrid retrieval native**: BGE-M3 tạo được cả dense vector VÀ sparse (lexical) representation từ cùng model → không cần maintain 2 model riêng
2. **Vietnamese benchmarks**: Top-tier trên VN-MTEB (Vietnamese Massive Text Embedding Benchmark)
3. **Matryoshka dimension**: Có thể truncate 1024 → 512 dim nếu cần tiết kiệm storage/speed
4. **MIT license**: Free dùng thương mại

#### Deployment plan

```
Option A (GPU ≥ 4GB VRAM):
  → Self-host qua sentence-transformers / FlagEmbedding library
  → Batch embedding offline, inference latency ~50ms/query

Option B (Không có GPU):
  → HuggingFace Inference API (free tier: 1000 req/ngày)
  → Hoặc chạy CPU inference (chậm hơn ~5-10x nhưng chấp nhận được cho MVP)
```

### 3.2. Lựa chọn Vector Database

#### Trade-off table

| Vector DB | Metadata Filtering | Local Deploy | Rust/Performance | Free? | **Verdict** |
|---|---|---|---|---|---|
| **🏆 Qdrant (local mode)** | ✅ Advanced (indexed payload) | ✅ Single binary/Docker | ✅ Rust | ✅ | **CHỌN** |
| ChromaDB | ⚠️ Basic (key-value) | ✅ pip install | ❌ Python | ✅ | Backup cho prototype |
| Milvus Lite | ✅ Good | ⚠️ Complex | ✅ | ✅ | Overkill cho 5K chunks |

#### Lý do chọn Qdrant

1. **Pre-filtering**: filter theo `status`, `effective_date`, `doc_type` TRƯỚC khi ANN search → đảm bảo không bao giờ trả chunk hết hiệu lực
2. **Payload indexing**: có thể index `status`, `effective_date`, `topic_tags` → filter O(1) thay vì O(n)
3. **Scalar quantization**: giảm memory ~4x khi cần
4. **Snapshot/backup**: dễ backup và restore
5. **Rust performance**: nhanh hơn ChromaDB đáng kể khi dataset > 1000 chunks

#### Qdrant setup

```python
# Pseudocode
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

client = QdrantClient(path="./data/qdrant_db")  # local mode, không cần server

client.create_collection(
    collection_name="legal_chunks",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
)

# Index metadata fields cho filtering
client.create_payload_index("legal_chunks", "status", PayloadSchemaType.KEYWORD)
client.create_payload_index("legal_chunks", "effective_date", PayloadSchemaType.DATETIME)
client.create_payload_index("legal_chunks", "doc_type", PayloadSchemaType.KEYWORD)
client.create_payload_index("legal_chunks", "topic_tags", PayloadSchemaType.KEYWORD)
```

### 3.3. Retrieval Strategy: Hybrid Search + Temporal Filter + Rerank

#### Pipeline 4 bước

```
User Query: "Trợ cấp thôi việc cho NLĐ làm 5 năm được tính thế nào?"
    │
    ▼
┌─────────────────────────────────────────────────┐
│ BƯỚC 1: Query Processing                        │
│                                                  │
│ • Entity extraction: "trợ cấp thôi việc" →       │
│   topic_tag = "tro_cap_thoi_viec"                │
│ • Query expansion: thêm "Điều 46", "chấm dứt    │
│   hợp đồng" (synonym dictionary)                 │
│ • Nếu có số hiệu VB → exact match mode           │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│ BƯỚC 2: Metadata Pre-filter (Qdrant filter)      │
│                                                  │
│ MUST filter:                                     │
│   status != "het_hieu_luc"                       │
│                                                  │
│ SHOULD filter (nếu có):                          │
│   doc_type IN ["luat", "nghi_dinh"] (nếu query   │
│   chung, ưu tiên luật > NĐ > TT)                │
│   topic_tags CONTAINS extracted_tag               │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│ BƯỚC 3: Hybrid Search (BM25 + Dense)             │
│                                                  │
│ Dense search:                                    │
│   → Qdrant vector search (cosine) trên filtered  │
│     subset → top 20 candidates                    │
│                                                  │
│ Sparse search:                                   │
│   → BM25 trên content text (rank_bm25 library)   │
│     → top 20 candidates                           │
│                                                  │
│ Fusion: Reciprocal Rank Fusion (RRF)             │
│   RRF_score(d) = Σ 1/(k + rank_i(d))            │
│   k = 60 (constant)                              │
│   → top 10 fused results                          │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│ BƯỚC 4: Rule-based Reranking                     │
│                                                  │
│ final_score = rrf_score                          │
│   × doc_type_weight                              │
│   × recency_boost                                │
│   × version_penalty                              │
│                                                  │
│ doc_type_weight:                                 │
│   luat=1.0, nghi_dinh=0.9, thong_tu=0.8,        │
│   cong_van=0.6                                   │
│                                                  │
│ recency_boost:                                   │
│   1.0 + 0.1 × (year - 2019) / 7                 │
│   → văn bản mới hơn boost nhẹ                    │
│                                                  │
│ version_penalty:                                 │
│   if status == "sua_doi_bo_sung"                 │
│     AND replaced_by is not empty                 │
│   → score × 0.5 (giảm ưu tiên bản cũ bị sửa)   │
│                                                  │
│ → Return top 5 results                            │
└─────────────────────────────────────────────────┘
```

#### Lý do chọn Hybrid (dense + BM25) thay vì dense-only

| Case | Dense-only | BM25-only | **Hybrid** |
|---|---|---|---|
| "Điều 46 Khoản 1 BLLĐ 2019" | ⚠️ Có thể miss (semantic search không match exact keyword) | ✅ Exact match tốt | ✅ |
| "Tôi bị sa thải oan, có quyền gì?" | ✅ Semantic match tốt | ⚠️ Thiếu keyword chính xác | ✅ |
| "So sánh trợ cấp thôi việc và mất việc" | ✅ Tốt | ❌ Kém | ✅ |

> [!NOTE]
> **BM25 quan trọng đặc biệt cho legal domain** vì user thường hỏi kèm số hiệu cụ thể ("NĐ 145", "Điều 46") — đây là exact keyword match, dense search thường miss.

#### Lựa chọn Reranking approach

| Approach | Ưu điểm | Nhược điểm | **Verdict** |
|---|---|---|---|
| **🏆 Rule-based (doc_type × recency × version)** | Miễn phí, deterministic, giải thích được | Không capture semantic relevance fine-grained | **CHỌN cho MVP** |
| Cross-encoder (bge-reranker-v2-m3) | Accuracy cao hơn | Cần GPU, thêm latency ~200ms | Stretch goal |
| LLM-as-reranker | Flexible nhất | Tốn token, chậm | Không khả thi ($0) |

---

## 4. Generation & Agent Logic

### 4.1. Intent Classification

#### Phương pháp: Keyword heuristic + LLM fallback

```python
# Pseudocode
def classify_intent(query: str) -> Intent:
    # Bước 1: Keyword/pattern matching (nhanh, miễn phí)
    if has_calculation_keywords(query):  # "tính", "bao nhiêu tiền", "trợ cấp"
        params = extract_calc_type(query)
        if params:
            return Intent(type="tinh_toan", calc_type=params.type)

    if has_drafting_keywords(query):     # "soạn", "viết đơn", "mẫu hợp đồng"
        return Intent(type="soan_thao", template=extract_template(query))

    # Bước 2: Nếu keyword không rõ → gọi LLM classify
    # (tiết kiệm LLM calls — chỉ gọi khi heuristic không chắc)
    llm_result = llm_classify(query)
    return llm_result
```

| Approach | Ưu điểm | Nhược điểm | **Verdict** |
|---|---|---|---|
| **🏆 Heuristic + LLM fallback** | Tiết kiệm LLM calls (70-80% cases resolved by keyword), deterministic | Cần maintain keyword list | **CHỌN** |
| LLM-only | Flexible nhất | Tốn token, latency mỗi request | Backup |
| Fine-tuned classifier | Accuracy cao nhất | Cần training data, thời gian | Out of scope |

### 4.2. Module Routing cho từng Intent

```
┌─────────────────────────────────────────────────────────────────┐
│                        ROUTING LOGIC                             │
│                                                                  │
│ intent == "tra_cuu":                                             │
│   → Retrieval(query, top_k=5)                                   │
│   → LLM.synthesize(query, retrieved_chunks)                     │
│   → attach_citations(retrieved_chunks)                           │
│                                                                  │
│ intent == "tinh_toan":                                           │
│   → LLM.extract_params(query) → CalcInput (Pydantic)            │
│   → if missing_required_fields:                                  │
│       → ask_user(missing_fields)                                 │
│   → Calculation.compute(calc_type, params) → CalcOutput          │
│   → Retrieval(legal_basis_query, top_k=2) → citations            │
│   → format_response(CalcOutput, citations)                       │
│                                                                  │
│ intent == "soan_thao":                                           │
│   → Retrieval(relevant_law, top_k=3) → legal context             │
│   → check_required_fields(template, user_data)                   │
│   → if missing_fields:                                           │
│       → ask_user(missing_fields)                                 │
│   → Drafting.generate(template, user_data, legal_context)        │
│   → attach_citations(legal_context)                              │
│                                                                  │
│ intent == "multi":                                               │
│   → Retrieval(query, top_k=5)                                   │
│   → LLM.extract_params(query) → CalcInput                       │
│   → Calculation.compute(...)                                     │
│   → LLM.synthesize(query, chunks, calc_result)                   │
│   → attach_citations(chunks)                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3. LLM Selection & Prompt Design

#### LLM Trade-off table

| LLM | Free Tier | RPM | RPD | Context | Vietnamese | **Verdict** |
|---|---|---|---|---|---|---|
| **🏆 Gemini Flash (3.0/2.5)** | ✅ | ~15 | ~1,500 | 1M tokens | ✅ Good | **Primary** |
| Groq (Llama 3.1 70B) | ✅ | ~30 | Limited | 128K | ⚠️ OK | **Fallback** |
| Ollama (local quantized) | ✅ Unlimited | N/A | N/A | Varies | ⚠️ Depends | Dev/offline |

#### Prompt template cho Response Synthesis

```
System: Bạn là trợ lý pháp lý chuyên về luật lao động Việt Nam.
Trả lời DỰA TRÊN các điều khoản pháp luật được cung cấp bên dưới.
KHÔNG bịa thông tin, KHÔNG tự ý trích dẫn điều khoản không có trong context.

Quy tắc trả lời:
1. Trích dẫn nguồn bằng [1], [2]... tương ứng với thứ tự điều khoản bên dưới
2. Nếu không tìm thấy điều khoản liên quan → nói rõ "Tôi không tìm thấy thông tin"
3. Kết thúc bằng disclaimer: "Thông tin mang tính tham khảo..."

--- ĐIỀU KHOẢN PHÁP LUẬT ---
{retrieved_chunks_with_metadata}

--- CÂU HỎI ---
{user_query}
```

### 4.4. Citation Grounding

Quy trình đảm bảo trích dẫn chính xác:

```
1. LLM nhận retrieved chunks + metadata → sinh response kèm [1], [2]...
2. Post-processing:
   a. Parse [N] references trong response
   b. Map mỗi [N] → chunk_id cụ thể
   c. Từ chunk_id → extract: doc_number, article, clause, effective_date, status
   d. Build citations[] array cho response JSON
3. Validation:
   a. Kiểm tra [N] có vượt quá số chunks retrieved không
   b. Kiểm tra status của cited chunk — nếu "het_hieu_luc" → warning
4. Output: response JSON với citations[] đầy đủ
```

### 4.5. Calculation Module (Rule-based)

> [!CAUTION]
> **Nguyên tắc bất di bất dịch**: LLM KHÔNG ĐƯỢC tự tính toán số. LLM chỉ trích xuất tham số → gọi hàm Python thuần → trả kết quả.

#### Data flow

```
User: "Tôi làm 5 năm, lương 12 triệu, trợ cấp thôi việc bao nhiêu?"
    │
    ▼
LLM Extract Params (structured output):
    {
      "calc_type": "tro_cap_thoi_viec",
      "luong_binh_quan_6_thang": 12000000,
      "tong_thoi_gian_lam_viec": 5.0,
      "thoi_gian_dong_bhtn": 0,      ← LLM hỏi lại nếu thiếu
      "thoi_gian_da_nhan_tro_cap": 0
    }
    │
    ▼
Python Function (deterministic):
    tinh_tro_cap_thoi_viec(params) → CalculationOutput
    │
    ▼
Result:
    {
      "result": 30000000,
      "result_formatted": "30.000.000 VNĐ",
      "formula_used": "TC = 1/2 × L_bq × N",
      "legal_basis": "Điều 46, Khoản 1, BLLĐ 2019",
      "breakdown": [
        "L_bq = 12.000.000 VNĐ",
        "N = 5 - 0 - 0 = 5 năm",
        "TC = 0.5 × 12.000.000 × 5 = 30.000.000 VNĐ"
      ]
    }
```

#### 5 công thức Core

| # | Tên | Căn cứ | Công thức | Edge cases |
|---|---|---|---|---|
| 1 | Trợ cấp thôi việc | Đ.46 K.1 BLLĐ 2019 | `TC = 1/2 × L_bq × N` | N≤0 → 0; N<6 tháng check NĐ 145 |
| 2 | Trợ cấp mất việc | Đ.47 K.1 BLLĐ 2019 | `TC = 1 × L_bq × N` (min = 2×L_bq) | Mức tối thiểu 2 tháng lương |
| 3 | Lương thử việc | Đ.26 K.1 BLLĐ 2019 | `L_tv ≥ 85% × L_ct` | Check tính hợp lệ, tính ngược |
| 4 | BHTN | Đ.50 Luật VL 2013 | `TC = 60% × L_bq × N_tháng` | N_tháng phụ thuộc thời gian đóng; max 12 tháng |
| 5 | Phép năm | Đ.113 BLLĐ 2019 | `P = 12 + ⌊(N-1)/5⌋` | Tính lẻ; điều kiện đặc biệt 14 ngày |

#### Configurable constants

```json
// config/legal_constants.json
{
  "version": "2026-07-01",
  "luong_co_so": 2340000,
  "luong_toi_thieu_vung": {
    "vung_1": 4960000,
    "vung_2": 4410000,
    "vung_3": 3860000,
    "vung_4": 3450000,
    "effective_date": "2024-07-01",
    "legal_basis": "NĐ 74/2024/NĐ-CP"
  },
  "ty_le_dong_bhxh": {
    "nguoi_lao_dong": 0.08,
    "nguoi_su_dung_ld": 0.175,
    "effective_date": "2022-01-01"
  }
}
```

> [!WARNING]
> Các hằng số này THAY ĐỔI THEO THỜI GIAN (lương tối thiểu vùng thay đổi mỗi 1-2 năm, lương cơ sở đã bãi bỏ). Config file phải version hóa và note rõ `effective_date`.

### 4.6. Drafting Module

#### Data flow

```
User chọn template "Đơn khiếu nại" → Frontend hiện form
    │
    ▼
User điền: tên, CCCD, công ty, nội dung khiếu nại...
    │
    ▼
Validation (Pydantic):
    → Kiểm tra required fields đầy đủ
    → Validate format (CCCD 12 số, ngày hợp lệ)
    │
    ▼
Retrieval (auto):
    → Query: "{nội dung khiếu nại}" → tìm điều khoản liên quan
    → Gợi ý can_cu_phap_ly cho user
    │
    ▼
Template render (Jinja2):
    → Điền data vào template
    → LLM naturalize nội dung (làm mượt ngôn ngữ)
    │
    ▼
Preview + Export (.md → .docx)
```

---

## 5. Evaluation Strategy

### 5.1. Eval Set Design

| Category | Số lượng | Nguồn | Ví dụ |
|---|---|---|---|
| **Tra cứu thông thường** | 30 | Tự soạn + diễn đàn | "Thời gian báo trước khi nghỉ việc?" |
| **Tra cứu temporal** | 15 | Tự soạn | "NĐ nào hướng dẫn Điều 46 BLLĐ 2019?" → phải trả NĐ mới nhất |
| **Tính toán** | 20 | Tự soạn | "5 năm, lương 10 triệu, trợ cấp?" → expected: 25.000.000 |
| **Multi-intent** | 10 | Tự soạn | "Trợ cấp thôi việc bao nhiêu và tôi cần soạn đơn gì?" |
| **Edge cases** | 10 | Tự soạn | Thiếu tham số, câu hỏi mơ hồ, ngoài phạm vi |
| **Negative** | 5 | Tự soạn | "Thuế thu nhập doanh nghiệp?" → ngoài scope → từ chối |
| **Tổng** | **90** | | |

### 5.2. Metrics & Targets

| Dimension | Metric | Target | Phương pháp đo |
|---|---|---|---|
| **Retrieval** | Precision@5 | ≥ 0.70 | Auto: so sánh retrieved vs expected_articles |
| | Recall@5 | ≥ 0.80 | Auto |
| | MRR | ≥ 0.70 | Auto |
| | Temporal Recall@5 | ≥ 0.80 | Auto: subset temporal cases |
| **Calculation** | Accuracy | **100%** | Auto: compare output vs expected |
| **Citation** | Citation Precision | ≥ 0.90 | Manual + auto |
| | Citation Recall | ≥ 0.80 | Manual + auto |
| **Generation** | Faithfulness | ≥ 0.85 | LLM-as-judge (Gemini đánh giá output) |
| **Drafting** | Completeness | ≥ 0.90 | Checklist: đủ điều khoản bắt buộc |

### 5.3. Baseline Comparison (bắt buộc cho báo cáo)

| # | Baseline | Mô tả | Kỳ vọng |
|---|---|---|---|
| B1 | **BM25 thuần** | Sparse retrieval, không có dense/rerank/filter | Precision thấp hơn hybrid |
| B2 | **Dense-only** | Vector search, không BM25, không metadata filter | Miss exact keyword queries |
| B3 | **LLM không RAG** | Gemini trả lời trực tiếp, không retrieval | Hallucinate số điều/khoản |
| B4 | **Full pipeline** | Hybrid + filter + rerank | Kỳ vọng tốt nhất |

> [!IMPORTANT]
> Baseline B3 (LLM không RAG) là comparison quan trọng nhất cho báo cáo — chứng minh RAG thêm giá trị gì so với LLM raw.

---

## 6. Ràng buộc Thực thi

### 6.1. Free-tier Analysis & Risk

| Service | Free Tier | Giới hạn | Rủi ro | Mitigation |
|---|---|---|---|---|
| **Gemini Flash** | ✅ | ~15 RPM, ~1,500 RPD | Không đủ cho eval set lớn trong 1 ngày | Chia eval thành 2-3 ngày; cache responses |
| **HuggingFace Inference** | ✅ | ~1,000 req/ngày (rate limited) | Chậm khi batch embedding | Embed offline + save; chỉ dùng API cho incremental |
| **Qdrant local** | ✅ Unlimited | RAM dependent (~50MB cho 5K vectors) | Mất data nếu không backup | Snapshot weekly |
| **Vercel** | ✅ | 100GB bandwidth, serverless | Cold start ~3s | Chấp nhận cho demo |
| **GitHub Actions** | ✅ | 2,000 min/tháng | Đủ cho CI basic | Chỉ chạy fast tests trên PR |

### 6.2. Data Privacy (NĐ 13/2023)

```
Nguyên tắc:
1. KHÔNG lưu trữ dữ liệu cá nhân user (tên, CCCD, lương) ở server
2. Calculation: xử lý in-memory → trả result → discard input
3. Drafting: render server-side → trả file → discard user_data
4. Logging: ẩn danh hóa — log query pattern, KHÔNG log PII
5. Frontend: localStorage chỉ cho UI preferences, KHÔNG cho user data
6. Disclaimer: hiển thị rõ "Dữ liệu không được lưu trữ"
```

---

## 7. Cấu trúc Codebase

```
AI_Agent_Luật_Lao_Động/
│
├── .claude/                        # Agent prompts, rules, skills (đã thiết kế)
│
├── backend/                        # FastAPI application
│   ├── main.py                     # FastAPI app entry point
│   ├── config/
│   │   ├── settings.py             # Environment config (Pydantic BaseSettings)
│   │   └── legal_constants.json    # Mức lương, tỷ lệ BHXH (versioned)
│   │
│   ├── api/                        # API layer
│   │   ├── router.py               # Include all routers
│   │   ├── chat.py                 # POST /api/chat
│   │   ├── retrieve.py             # POST /api/retrieve
│   │   ├── calculate.py            # POST /api/calculate/{type}
│   │   ├── draft.py                # POST /api/draft/{template}
│   │   └── health.py               # GET /api/health
│   │
│   ├── core/                       # Business logic
│   │   ├── intent_classifier.py    # Keyword heuristic + LLM fallback
│   │   ├── response_assembler.py   # Tổng hợp, gắn citations, disclaimer
│   │   └── llm_client.py           # Gemini/Groq client wrapper
│   │
│   ├── retrieval/                  # WP1 — Retrieval pipeline
│   │   ├── embedder.py             # BGE-M3 embedding (batch + single)
│   │   ├── vector_store.py         # Qdrant operations
│   │   ├── bm25_index.py           # BM25 indexing + search
│   │   ├── hybrid_search.py        # RRF fusion
│   │   ├── reranker.py             # Rule-based reranking
│   │   └── query_processor.py      # Query expansion + entity extraction
│   │
│   ├── calculation/                # WP2 — Calculation module
│   │   ├── models.py               # Pydantic Input/Output models
│   │   ├── tro_cap_thoi_viec.py
│   │   ├── tro_cap_mat_viec.py
│   │   ├── luong_thu_viec.py
│   │   ├── bhtn.py
│   │   ├── phep_nam.py
│   │   └── param_extractor.py      # LLM → structured params
│   │
│   ├── drafting/                   # WP2 — Drafting module
│   │   ├── models.py               # Template definitions + required fields
│   │   ├── templates/              # Jinja2 templates (.j2 files)
│   │   │   ├── don_khieu_nai.j2
│   │   │   ├── hdld_co_ban.j2
│   │   │   └── quyet_dinh_cham_dut.j2
│   │   ├── renderer.py             # Template rendering logic
│   │   └── exporter.py             # .md → .docx conversion
│   │
│   ├── models/                     # Shared Pydantic models
│   │   ├── chunk.py                # ChunkMetadata, ChunkResult
│   │   ├── request.py              # ChatRequest, RetrieveRequest, etc.
│   │   └── response.py             # ChatResponse, CalcResponse, etc.
│   │
│   └── tests/                      # Unit tests
│       ├── test_calculations/      # ≥ 5 tests per formula
│       ├── test_retrieval/
│       ├── test_intent/
│       └── test_drafting/
│
├── data/                           # Data layer
│   ├── raw/                        # Raw HTML/PDF (crawled)
│   ├── cleaned/                    # Cleaned JSON per document
│   ├── chunks.jsonl                # Final chunks with metadata
│   ├── document_relations.json     # Quan hệ sửa đổi/thay thế
│   ├── qdrant_db/                  # Qdrant local storage
│   ├── bm25_index/                 # Serialized BM25 index
│   ├── crawl_plan.md               # Danh sách VB cần crawl + status
│   └── crawl_log.json              # Crawl history
│
├── eval/                           # Evaluation
│   ├── eval_set_v1.json            # Test cases (versioned)
│   ├── run_eval.py                 # Script chạy eval suite
│   ├── eval_report_YYYY-MM-DD.md   # Reports
│   └── baselines/                  # Baseline results for comparison
│
├── frontend/                       # Next.js / React app
│   ├── src/
│   │   ├── app/                    # Pages
│   │   ├── components/             # Reusable UI components
│   │   │   ├── ChatMessage.tsx     # Message bubble + inline citations
│   │   │   ├── CitationPanel.tsx   # Expandable citation list
│   │   │   ├── CalcForm.tsx        # Calculation input forms
│   │   │   ├── DraftPreview.tsx    # Side-by-side draft view
│   │   │   └── Disclaimer.tsx      # Legal disclaimer
│   │   ├── hooks/                  # Custom hooks
│   │   └── lib/                    # API client, utilities
│   └── ...
│
├── scripts/                        # Utility scripts
│   ├── crawl.py                    # Run crawler
│   ├── chunk.py                    # Run chunking pipeline
│   ├── embed.py                    # Run embedding + indexing
│   └── seed_bm25.py               # Build BM25 index
│
├── report/                         # Báo cáo đồ án
│   └── sections/                   # Markdown sections
│
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore
└── README.md
```

---

## 8. Lộ trình theo Phase — Quality Gates

> Không giới hạn thời gian hay nhân sự. Mỗi Phase kết thúc bằng một **Quality Gate** — chỉ chuyển sang Phase tiếp theo khi Gate đã PASS.

### Phase 1: Data Foundation

**Mục tiêu**: Có corpus văn bản pháp luật sạch, chunked, metadata đầy đủ.

| Task | Agent phụ trách | Skill sử dụng | Deliverable |
|---|---|---|---|
| Lập danh sách văn bản cần crawl | Ingestion Agent | `crawl-legal-source` | `data/crawl_plan.md` |
| Crawl toàn bộ văn bản Core | Ingestion Agent | `crawl-legal-source` | `data/raw/` (HTML/PDF) |
| Parse + clean + validate | Ingestion Agent | — | `data/cleaned/` (JSON) |
| Chunking theo Điều/Khoản | Ingestion Agent | — | `data/chunks.jsonl` |
| Xây document_relations | Ingestion Agent | — | `data/document_relations.json` |
| Review chunking quality | Reviewer Agent | `review-legal-chunking` | Chunking Report |

**🚪 Quality Gate 1**:
```
□ chunks.jsonl có ≥ 2000 chunks
□ Mỗi chunk có đủ metadata schema (19 fields)
□ Sampling test: 10 random chunks verify đúng với source gốc
□ document_relations.json phủ mọi quan hệ sửa đổi/thay thế đã biết
□ Reviewer Agent sign-off: 0 Critical findings
```

---

### Phase 2: Retrieval Pipeline

**Mục tiêu**: Retrieval trả đúng điều luật, ưu tiên còn hiệu lực, hybrid search hoạt động.

| Task | Agent phụ trách | Skill sử dụng | Deliverable |
|---|---|---|---|
| Setup BGE-M3 embedding | RAG Engineer Agent | — | Embedding pipeline |
| Embed toàn bộ chunks | RAG Engineer Agent | — | Qdrant DB populated |
| Xây BM25 index | RAG Engineer Agent | — | BM25 serialized index |
| Implement hybrid search (RRF) | RAG Engineer Agent | — | `retrieval/hybrid_search.py` |
| Metadata pre-filter | RAG Engineer Agent | — | `retrieval/vector_store.py` |
| Rule-based reranker | RAG Engineer Agent | — | `retrieval/reranker.py` |
| Query expansion + entity extraction | RAG Engineer Agent | — | `retrieval/query_processor.py` |
| Xây eval set retrieval | Eval/QA Agent | `run-eval-suite` | `eval/eval_set_v1.json` (≥50 cases) |
| Đo baseline: BM25-only vs Dense-only vs Hybrid | Eval/QA Agent | `run-eval-suite` | Baseline comparison report |
| Review retrieval architecture | Reviewer Agent | — | Review report |

**🚪 Quality Gate 2**:
```
□ Precision@5 ≥ 0.70 trên eval set
□ Recall@5 ≥ 0.80 trên eval set
□ Temporal Recall@5 ≥ 0.80 (subset temporal cases)
□ Hybrid > BM25-only AND Hybrid > Dense-only (chứng minh giá trị hybrid)
□ Không bao giờ trả chunk có status = "het_hieu_luc" trong top 5
□ Latency < 3 giây cho retrieval
```

---

### Phase 3: Calculation & Drafting

**Mục tiêu**: 5 công thức tính toán chính xác 100%, 3 template soạn thảo hoàn chỉnh.

| Task | Agent phụ trách | Skill sử dụng | Deliverable |
|---|---|---|---|
| Đọc và phân tích luật gốc cho 5 công thức | Calculation Agent | — | Phân tích edge cases |
| Implement 5 hàm tính toán | Calculation Agent | `implement-calculation` | `calculation/*.py` |
| Unit tests cho mỗi hàm (≥5 cases/hàm) | Calculation Agent | `implement-calculation` | `tests/test_calculations/` |
| Thiết kế legal_constants.json | Calculation Agent | — | `config/legal_constants.json` |
| Thiết kế 3 templates + required fields | Drafting Agent | — | `drafting/models.py` |
| Implement Jinja2 templates | Drafting Agent | — | `drafting/templates/*.j2` |
| Implement renderer + .docx exporter | Drafting Agent | — | `drafting/renderer.py`, `exporter.py` |
| Param extractor (LLM → Pydantic) | Calculation Agent | — | `calculation/param_extractor.py` |
| Review tính chính xác pháp lý | Reviewer Agent | `validate-legal-citation` | Review report |

**🚪 Quality Gate 3**:
```
□ Calculation accuracy = 100% (0 sai số trên toàn bộ test cases)
□ Mỗi hàm có ≥ 5 unit tests passing (happy path + edge cases + boundary)
□ Mỗi hàm có docstring nêu rõ căn cứ pháp lý
□ 3 templates render đúng format văn bản hành chính VN
□ Templates validate required fields + format (CCCD, ngày tháng)
□ Param extractor parse đúng ≥ 90% câu hỏi tự nhiên
□ Reviewer sign-off: 0 Critical findings về legal accuracy
```

---

### Phase 4: Orchestration & API

**Mục tiêu**: Backend API hoạt động end-to-end, intent routing chính xác.

| Task | Agent phụ trách | Skill sử dụng | Deliverable |
|---|---|---|---|
| Thiết kế API contract | Orchestration Agent | `design-api-contract` | Pydantic request/response models |
| Setup FastAPI + routers | Orchestration Agent | — | `api/*.py` |
| Intent classifier (heuristic + LLM fallback) | Orchestration Agent | — | `core/intent_classifier.py` |
| Response assembler (citations + disclaimer) | Orchestration Agent | — | `core/response_assembler.py` |
| LLM client wrapper (Gemini + Groq fallback) | Orchestration Agent | — | `core/llm_client.py` |
| Ghép nối: Retrieval + Calc + Draft → Response | Orchestration Agent | — | `/api/chat` hoạt động |
| Integration tests | Eval/QA Agent | — | `tests/test_integration/` |
| Review API + architecture compliance | Reviewer Agent | — | Review report |

**🚪 Quality Gate 4**:
```
□ POST /api/chat xử lý đúng cả 4 intent types
□ POST /api/retrieve, /api/calculate, /api/draft hoạt động riêng lẻ
□ Mọi response có citations[] và disclaimer
□ Error handling: 400 (validation), 500 (internal) đúng format
□ Latency < 10 giây cho full pipeline (retrieval + LLM)
□ Intent classifier accuracy ≥ 90% trên eval set
```

---

### Phase 5: Frontend

**Mục tiêu**: Web app hoàn chỉnh, UX tốt, hiển thị citation chính xác.

| Task | Agent phụ trách | Skill sử dụng | Deliverable |
|---|---|---|---|
| Setup Next.js/Vite project | Frontend Agent | — | Frontend skeleton |
| Chat UI + markdown rendering | Frontend Agent | — | `ChatMessage.tsx` |
| Inline citations + Citation panel | Frontend Agent | — | `CitationPanel.tsx` |
| Calculation forms + breakdown display | Frontend Agent | — | `CalcForm.tsx` |
| Drafting form + live preview + export | Frontend Agent | — | `DraftPreview.tsx` |
| Responsive design (mobile) | Frontend Agent | — | CSS/Tailwind |
| Loading states, error messages, empty states | Frontend Agent | — | UX polish |
| Gợi ý câu hỏi mẫu | Frontend Agent | — | Welcome screen |
| API integration (gọi backend) | Frontend Agent | — | `lib/api.ts` |

**🚪 Quality Gate 5**:
```
□ Chat flow hoạt động: hỏi → loading → trả lời + citations
□ Calculation form: chọn loại → điền → kết quả + breakdown + trích dẫn
□ Drafting: chọn template → điền → preview → export .docx
□ Citation hiển thị: inline [1] với tooltip, panel expandable, status badge
□ Responsive: dùng tốt trên mobile (≥ 375px)
□ Disclaimer hiển thị ở mọi response
□ No console errors, no broken layouts
```

---

### Phase 6: Evaluation & Optimization

**Mục tiêu**: Đánh giá toàn diện, so sánh baselines, optimize bottlenecks.

| Task | Agent phụ trách | Skill sử dụng | Deliverable |
|---|---|---|---|
| Hoàn thiện eval set (≥90 cases) | Eval/QA Agent | `run-eval-suite` | `eval/eval_set_final.json` |
| Chạy full eval suite | Eval/QA Agent | `run-eval-suite` | `eval/eval_report.md` |
| So sánh 4 baselines | Eval/QA Agent | `run-eval-suite` | Baseline comparison |
| Validate citation accuracy | Eval/QA Agent | `validate-legal-citation` | Citation report |
| Phân tích failure cases | Eval/QA Agent | — | Root cause analysis |
| Fix retrieval issues | RAG Engineer Agent | — | Improved pipeline |
| Fix calculation edge cases | Calculation Agent | `implement-calculation` | Fixed functions |
| UI improvements dựa trên eval | Frontend Agent | — | UI fixes |
| Re-run eval → confirm improvement | Eval/QA Agent | `run-eval-suite` | Final metrics |
| Final review toàn bộ codebase | Reviewer Agent | — | Sign-off report |

**🚪 Quality Gate 6 (FINAL)**:
```
□ Precision@5 ≥ 0.70, Recall@5 ≥ 0.80, MRR ≥ 0.70
□ Temporal Recall@5 ≥ 0.80
□ Citation Precision ≥ 0.90, Citation Recall ≥ 0.80
□ Calculation Accuracy = 100%
□ Full pipeline > BM25-only > LLM-no-RAG (chứng minh giá trị RAG)
□ Reviewer Agent final sign-off: 0 Critical findings
□ README.md hoàn chỉnh
```

---

### Phase 7: Documentation & Packaging

**Mục tiêu**: Tài liệu hoàn chỉnh, demo sẵn sàng.

| Task | Agent phụ trách | Skill sử dụng | Deliverable |
|---|---|---|---|
| Viết báo cáo từng phần | Tất cả agents | `write-report-section` | `report/sections/*.md` |
| Tổng hợp báo cáo cuối | — | `write-report-section` | Báo cáo hoàn chỉnh |
| README.md + setup guide | — | — | README.md |
| Record demo | — | — | Demo video |
| Deploy (nếu cần) | Orchestration Agent + Frontend Agent | — | Live demo URL |

---

## 9. Sơ đồ Kiến trúc Tổng thể (End-to-End Flow)

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  USER (NLĐ/NSDLĐ/HR)                                                  │
│    │                                                                   │
│    │  "Tôi làm 5 năm lương 12 triệu, trợ cấp thôi việc bao nhiêu?"  │
│    │                                                                   │
│    ▼                                                                   │
│  FRONTEND (Next.js)                                                    │
│    │  POST /api/chat { query: "..." }                                 │
│    ▼                                                                   │
│  FASTAPI BACKEND                                                       │
│    │                                                                   │
│    ├─► INTENT CLASSIFIER                                               │
│    │     → intent: "multi" (vừa hỏi luật vừa cần tính)                │
│    │     → calc_type: "tro_cap_thoi_viec"                              │
│    │     → params: {luong: 12M, nam: 5}                                │
│    │                                                                   │
│    ├─► RETRIEVAL MODULE                                                │
│    │     → Qdrant filter: status != "het_hieu_luc"                     │
│    │     → Hybrid search: BM25 + Dense → RRF → Rerank                 │
│    │     → Top 5 chunks (Đ.46 BLLĐ, Đ.8 NĐ 145, ...)                 │
│    │                                                                   │
│    ├─► CALCULATION MODULE                                              │
│    │     → tinh_tro_cap_thoi_viec({luong: 12M, nam: 5, bhtn: 0})     │
│    │     → result: 30,000,000 VNĐ                                     │
│    │     → formula: "TC = 1/2 × 12M × 5"                              │
│    │                                                                   │
│    ├─► RESPONSE ASSEMBLER                                              │
│    │     → LLM synthesize (query + chunks + calc_result)               │
│    │     → Attach citations[]: [{Đ.46 K.1 BLLĐ 2019, ...}]           │
│    │     → Attach disclaimer                                           │
│    │     → Format markdown                                             │
│    │                                                                   │
│    ▼                                                                   │
│  RESPONSE JSON                                                         │
│    {                                                                   │
│      "answer": "Theo Điều 46 BLLĐ 2019 [1], trợ cấp thôi việc...",   │
│      "calculation_result": { "value": 30000000, "breakdown": [...] }, │
│      "citations": [                                                    │
│        { "doc": "BLLĐ 2019", "article": 46, "status": "✅" }          │
│      ],                                                                │
│      "disclaimer": "Thông tin mang tính tham khảo..."                  │
│    }                                                                   │
│    │                                                                   │
│    ▼                                                                   │
│  FRONTEND renders:                                                     │
│    • Câu trả lời + inline [1] citations                                │
│    • Bảng breakdown tính toán (30.000.000 VNĐ highlighted)            │
│    • Panel trích dẫn expandable                                        │
│    • Disclaimer (italic, muted)                                        │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Câu hỏi mở — Cần quyết định trước khi bắt đầu

| # | Câu hỏi | Impact | Đề xuất |
|---|---|---|---|
| Q1 | Máy dev có GPU không? (ảnh hưởng embedding deployment) | Embedding speed | Nếu không → dùng HF Inference API hoặc CPU |
| Q2 | Dùng Next.js hay React+Vite cho frontend? | Frontend complexity | Next.js nếu muốn SSR; Vite nếu muốn đơn giản hơn |
| Q3 | Eval set viết bằng tay hay dùng LLM generate + human verify? | Eval quality | Hybrid: LLM generate draft → human verify + edit |
| Q4 | Monorepo (frontend + backend cùng repo) hay tách? | Git workflow | Monorepo (đơn giản, dễ quản lý) |
| Q5 | Deploy demo ở đâu? (Vercel + Railway? Render? Self-host?) | Demo availability | Vercel (frontend) + Railway/Render free tier (backend) |
