---
name: validate-legal-citation
description: Kiểm tra trích dẫn pháp luật trong response có chính xác không — đúng số hiệu, điều/khoản, nội dung, và trạng thái hiệu lực. Use after generation pipeline creates a response.
---

# Validate Legal Citation

> Dùng sau khi generation pipeline tạo response, hoặc khi review output chất lượng.

## Quy trình kiểm tra

### 1. Extract citations từ response
- Tìm mọi mention trong response: "Điều X", "Khoản Y", "Điểm Z", số hiệu văn bản
- Parse thành structured list:
  ```
  citations_found:
    - {doc_number: "45/2019/QH14", article: 46, clause: 1, point: null}
    - {doc_number: "145/2020/NĐ-CP", article: 8, clause: null, point: null}
  ```

### 2. Cross-reference với corpus
Với mỗi citation tìm được, kiểm tra 3 điều:

| Kiểm tra | Câu hỏi | Pass/Fail |
|---|---|---|
| **Tồn tại** | Citation này có trong chunk database không? | ✅/❌ |
| **Nội dung khớp** | Nội dung trích dẫn trong response có match với source chunk không? | ✅/❌/⚠️ |
| **Còn hiệu lực** | Văn bản được trích dẫn còn hiệu lực không? (check `status` metadata) | ✅/🔴 |

### 3. Phân loại lỗi

| Loại lỗi | Mô tả | Severity |
|---|---|---|
| **Hallucinated** | Điều/khoản không tồn tại trong corpus | 🔴 Critical |
| **Misquoted** | Tồn tại nhưng nội dung bị trích dẫn sai | 🟡 Warning |
| **Expired** | Trích dẫn văn bản hết hiệu lực mà không ghi chú | 🔴 Critical |
| **Incomplete** | Thiếu khoản/điểm quan trọng liên quan đến câu hỏi | 🟡 Warning |
| **Wrong article** | Đúng văn bản nhưng sai số điều | 🔴 Critical |

### 4. Tính metrics

```
Citation Precision = correct_citations / total_citations_in_response
Citation Recall = correct_citations / expected_citations_from_eval_set
```

### 5. Output

```markdown
## Citation Validation Report

**Response ID**: resp_001
**Total citations found**: 3
**Correct**: 2 | **Incorrect**: 1

| # | Citation | Tồn tại? | Nội dung khớp? | Hiệu lực? | Verdict |
|---|---|---|---|---|---|
| [1] | Đ.46 K.1 BLLĐ 2019 | ✅ | ✅ | ✅ Còn HL | ✅ Correct |
| [2] | Đ.8 NĐ 145/2020 | ✅ | ⚠️ Gần đúng | ✅ Còn HL | ⚠️ Check |
| [3] | Đ.50 K.2 BLLĐ 2019 | ❌ K.2 không tồn tại | — | — | ❌ Hallucinated |

**Precision**: 2/3 = 66.7%
**Recommendation**: Kiểm tra lại Điều 50 — chỉ có Khoản 1, không có Khoản 2.
```
