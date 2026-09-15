---
name: design-api-contract
description: Thiết kế và document API contract giữa các module (WP1 Retrieval, WP2 Calculation/Drafting, WP3 Orchestration). Use when starting a new module or changing input/output format.
---

# Design API Contract

> Dùng khi bắt đầu module mới cần giao tiếp với module khác, hoặc khi thay đổi schema.

## When to use
- Tuần 1: thiết kế contract ban đầu giữa WP1/WP2/WP3
- Tuần 5-6: đồng bộ khi tích hợp
- Bất kỳ lúc nào thay đổi input/output format

## Template contract

### 1. Endpoint definition

```markdown
## [MODULE_NAME] API Contract

### POST /api/[endpoint]

**Description**: Mô tả ngắn chức năng

**Request Body**:
```json
{
  "field1": "type — description",
  "field2": "type — description (optional)"
}
```

**Success Response** (200):
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Responses**:
- 400: Bad Request — validation failed (thiếu field, format sai)
- 404: Not Found — resource không tồn tại
- 500: Internal Server Error — lỗi hệ thống

**Error Schema**:
```json
{
  "success": false,
  "error_code": "VALIDATION_ERROR",
  "error_message": "Thiếu trường luong_binh_quan_6_thang"
}
```
```

### 2. Inter-module contract

```markdown
## [Module A] → [Module B] Contract

**Data format**: JSON
**Transport**: Internal function call (cùng process) hoặc HTTP (nếu microservice)
**Async/Sync**: Sync (MVP)
**Timeout**: 10 giây

**Input schema** (Pydantic model):
  class RetrievalRequest(BaseModel):
      query: str
      filters: Optional[dict] = None
      top_k: int = 5

**Output schema** (Pydantic model):
  class RetrievalResponse(BaseModel):
      results: list[ChunkResult]
      method: str
      processing_time_ms: int
```

### 3. Example request/response

Luôn kèm ít nhất 1 example đầy đủ (happy path) và 1 example error case.

## Validation

- Cả 2 bên (caller + callee) viết test dựa trên contract
- Contract test: gửi example request → assert response matches schema
- Breaking change: nếu thay đổi schema → thông báo tất cả modules phụ thuộc

## Checklist khi tạo/thay đổi contract

```
□ Request schema defined (Pydantic model)
□ Response schema defined (Pydantic model)
□ Error schema defined
□ Example happy path
□ Example error case
□ Timeout specified
□ Team member phụ trách module kia đã review
□ Cập nhật vào session_state.md (quyết định đã chốt)
```
