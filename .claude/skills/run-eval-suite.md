---
name: run-eval-suite
description: Chạy toàn bộ bộ đánh giá (eval suite) và tổng hợp kết quả — retrieval metrics, citation accuracy, calculation accuracy. Use after pipeline changes or before milestones.
---

# Run Eval Suite

> Dùng sau thay đổi retrieval/generation pipeline, trước khi merge PR quan trọng, hoặc tại milestone (tuần 7).

## Quy trình

### 1. Load eval set
- Đọc file `eval/eval_set_v{N}.json` (version mới nhất)
- Thống kê: tổng số cases, phân bố theo category

### 2. Chạy Retrieval Eval
```
Mỗi question trong eval set:
  → Gọi retrieval API (POST /api/retrieve)
  → So sánh retrieved articles vs expected_articles
  → Tính: Precision@5, Recall@5, MRR
```

Tách riêng metric cho:
- Category "retrieval" (tra cứu thông thường)
- Category "temporal" (hỏi về điều khoản đã sửa đổi/hết hiệu lực)

### 3. Chạy Calculation Eval
```
Mỗi calculation case:
  → Gọi calculation API (POST /api/calculate/{type})
  → So sánh result vs expected_calculation.result
  → Target: Accuracy = 100%
```

Báo lỗi ngay lập tức nếu có bất kỳ case nào sai.

### 4. Chạy End-to-End Eval
```
Mỗi question:
  → Gọi /api/chat (full pipeline)
  → Kiểm tra: citation accuracy, answer chứa expected_answer_contains
  → Tính: Citation Precision, Citation Recall
```

### 5. Tổng hợp kết quả

```markdown
## Eval Report — [YYYY-MM-DD]

### Summary Metrics

| Metric | Baseline (BM25) | Previous Run | Current Run | Delta |
|---|---|---|---|---|
| Precision@5 | X.XX | X.XX | X.XX | +X.XX |
| Recall@5 | X.XX | X.XX | X.XX | +X.XX |
| MRR | X.XX | X.XX | X.XX | +X.XX |
| Temporal Recall@5 | X.XX | X.XX | X.XX | +X.XX |
| Citation Precision | X.XX | X.XX | X.XX | +X.XX |
| Citation Recall | X.XX | X.XX | X.XX | +X.XX |
| Calc Accuracy | 100% | 100% | X% | — |

### Regression Alert
- ⚠️ [METRIC] giảm X% so với run trước → cần investigate

### Failed Cases
- TC-015: expected Điều 46 but retrieved Điều 47
- TC-032: calculation off by 500,000 VNĐ

### Recommendations
- ...
```

### 6. Post-eval actions
- Cập nhật bảng "Kết quả thực nghiệm" trong `session_state.md`
- Nếu regression > 5%: tạo issue trong `open_issues.md`
- Lưu report vào `eval/eval_report_YYYY-MM-DD.md`
