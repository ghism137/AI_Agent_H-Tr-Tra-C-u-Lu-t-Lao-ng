---
name: update-session-state
description: Skill for updating session_state.md with fine-grained task tracking by WP (Work Package), timestamps, and append-only decisions for continuous development.
---

# Update Session State Skill

This skill provides a strict workflow for updating `.claude/project/session_state.md` as the team progresses through development.

## 1. When to use

Use this skill whenever the user asks to "cập nhật tiến độ" (update progress), "chốt phiên" (end session), "log state", or explicitly asks to update `session_state.md`.

## 2. Reading the State

Always read the current `.claude/project/session_state.md` using `view_file` before making any edits. Do NOT assume its current contents.

## 3. Formatting Rules

When updating `session_state.md`, use `multi_replace_file_content` to surgically edit sections:

### A. Fine-Grained Task Tracking (theo WP)

Do not just check off a whole WP. Break down into sub-tasks using indented lists under WP1/WP2/WP3.

- Unstarted task: `- [ ] Task name`
- In-progress task: `- [/] Task name`
- Completed task: `- [x] [YYYY-MM-DD] Task name`

Example:
```
### WP1 — Data & Retrieval Pipeline
- [x] [2026-09-10] Thu thập dữ liệu BLLĐ 2019
- [/] Thiết kế metadata schema
    - [x] [2026-09-12] Draft schema v1
    - [/] Review với team
    - [ ] Finalize và document
- [ ] Chunking theo Điều/Khoản/Điểm
```

### B. Timestamping

Always prepend the current date `[YYYY-MM-DD]` when marking a sub-task as done `[x]` or when adding a new Decision/Blocker.

### C. Append-Only (Quyết định đã chốt & Bugs/Blockers)

Never delete historical decisions or bugs.

- **Quyết định kiến trúc**: Chỉ được append. Nếu quyết định cũ bị thay thế, gạch ngang dòng cũ: `~~Quyết định cũ~~ (Thay bởi: [mô tả ngắn], [ngày])`. KHÔNG xóa.
- **Bugs/Blockers**: Nếu đã fix, áp dụng gạch ngang: `~~[YYYY-MM-DD] Blocker text~~ (Đã fix: [ngày fix])`.

### D. Updating Metrics (Kết quả thực nghiệm)

If the user reports new evaluation metrics (Precision@5, Recall@5, MRR, Citation Accuracy, Calc Accuracy), locate the markdown table in "Kết quả thực nghiệm" and update the specific cell.

### E. Active Context

Update the "Đang làm" and "File quan trọng đang làm việc" sections to reflect the exact files and immediate task currently in focus.

## 4. Execution

1. Acknowledge the progress conceptually.
2. Read `session_state.md` using `view_file`.
3. Apply edits using `multi_replace_file_content`.
4. Respond with a brief summary of what was logged.
