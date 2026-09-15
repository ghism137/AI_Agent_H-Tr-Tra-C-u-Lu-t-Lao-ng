# Tech Defaults — AI Agent Luật Lao Động

## Ràng buộc ngân sách: $0

Mọi lựa chọn công nghệ PHẢI tuân thủ: free-tier hoặc open-source self-hosted.
Nếu đề xuất dịch vụ trả phí, PHẢI kèm phương án thay thế miễn phí.

## Stack mặc định

### Backend
- **Python 3.11+** — ngôn ngữ chính
- **FastAPI** — API framework (async, auto-docs, type hints)
- **Pydantic v2** — validation & serialization

### Embedding & Vector DB
- **Embedding model**: `intfloat/multilingual-e5-base` hoặc `BAAI/bge-m3`
  (open-source, hỗ trợ tiếng Việt, chạy local hoặc free inference API)
- **Vector DB**: Qdrant (local mode, không cần server) hoặc ChromaDB
- **BM25**: rank_bm25 hoặc Elasticsearch (nếu cần hybrid search)

### LLM
- **Primary**: Google Gemini free-tier (gemini-1.5-flash / gemini-2.0-flash)
- **Fallback**: Groq free-tier (llama-3.1-70b)
- **Local option**: Ollama + quantized model (nếu máy đủ mạnh)

### Frontend
- **Framework**: Next.js hoặc React + Vite
- **Styling**: Tailwind CSS
- **Deployment**: Vercel free-tier hoặc self-host

### Testing & Evaluation
- **Unit test**: pytest (bắt buộc cho calculation module)
- **Retrieval eval**: precision@k, recall@k trên eval set tự xây
- **Generation eval**: faithfulness score, citation accuracy
- **CI**: GitHub Actions free-tier

### Data & Storage
- **Legal text storage**: JSON/JSONL với metadata schema chuẩn
- **Database (nếu cần)**: SQLite (đơn giản) hoặc PostgreSQL
- **File storage**: local filesystem hoặc GitHub repo

## Conventions

- Python: Black formatter, Ruff linter, type hints bắt buộc
- Git: conventional commits (feat/fix/docs/refactor/test)
- API: RESTful, response format thống nhất có trường `citations[]`
- Environment: .env file cho API keys, KHÔNG commit secrets
