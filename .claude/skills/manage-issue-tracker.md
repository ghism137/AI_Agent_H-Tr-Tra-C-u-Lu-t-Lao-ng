---
name: manage-issue-tracker
description: Skill for managing architectural decisions, tech debt, and project issues in open_issues.md with categorized OPEN/SOLVED tracking.
---

# Manage Issue Tracker Skill

This skill provides a standardized workflow for logging and resolving architectural flaws, design decisions, and technical issues in `.claude/project/open_issues.md`.

## 1. When to use

Use this skill when you discover:
- A deep logical flaw in the project architecture
- A complex design question needing multi-session resolution
- "Tech Debt" that takes multiple sessions to resolve
- A retrieval/calculation/drafting bug that reveals a design issue

Do **NOT** use for daily progress/small bugs (use `update-session-state` for that).

## 2. Formatting Rules

### A. Logging a New Issue

Append to the bottom of `open_issues.md`:

```markdown
### [OPEN] [YYYY-MM-DD] [CATEGORY] Tên vấn đề ngắn gọn
**Vấn đề:** Mô tả chi tiết tại sao đây là một vấn đề.
**Impact:** Module/WP nào bị ảnh hưởng.
**Đề xuất:** Cách giải quyết hoặc các thực nghiệm cần làm.
```

**Categories:**
- `[RETRIEVAL]` — liên quan đến embedding, vector DB, search quality
- `[CALCULATION]` — liên quan đến công thức tính toán pháp lý
- `[DRAFTING]` — liên quan đến template soạn thảo
- `[INTEGRATION]` — liên quan đến API contract, orchestration
- `[EVAL]` — liên quan đến evaluation, test quality
- `[FRONTEND]` — liên quan đến UI/UX
- `[ARCHITECTURE]` — liên quan đến thiết kế tổng thể

### B. Resolving an Issue (Append-Only / Strikethrough)

**NEVER delete an issue.** Historical mistakes are valuable for the final thesis defense.

When solved, apply Markdown strikethrough `~~` to the body, change tag to `[SOLVED]`, and add resolution note:

```markdown
### [SOLVED] [2026-09-15] [CALCULATION] Tên vấn đề ngắn gọn
~~**Vấn đề:** Mô tả chi tiết tại sao đây là một vấn đề.~~
~~**Impact:** Module/WP nào bị ảnh hưởng.~~
~~**Đề xuất:** Cách giải quyết hoặc các thực nghiệm cần làm.~~
**Resolution [2026-09-20]:** Đã giải quyết bằng phương pháp X. Commit: abc123.
```

## 3. Execution Flow

1. Read `.claude/project/open_issues.md` using `view_file`.
2. Format the new entry or locate the entry to resolve.
3. Apply edits to the file.
4. Briefly summarize the logged/resolved issue for the user.
