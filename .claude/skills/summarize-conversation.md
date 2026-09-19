---
name: summarize-conversation
description: "Tóm tắt conversation hiện tại thành một handoff document súc tích, dùng để bootstrap conversation mới với đầy đủ context. Dùng khi conversation đã dài, khi chuyển giao việc sang session khác, hoặc khi cần cập nhật session_state.md."
risk: low
source: project
date_added: "2026-09-15"
---

# Skill: Summarize Conversation (Handoff Summary)

## Dùng khi

- Conversation đã dài, gần hết context window
- Cần chuyển sang conversation mới để tiếp tục việc
- Muốn cập nhật `session_state.md` sau một buổi làm việc
- Muốn tạo handoff note cho người/agent khác tiếp tục

## KHÔNG dùng khi

- Conversation còn ngắn (< 10 turns) — không cần tóm tắt
- Cần tóm tắt tài liệu kỹ thuật (dùng `write-report-section` skill)

---

## Quy trình thực hiện

### Bước 1 — Thu thập thông tin

Trước khi tóm tắt, đọc hoặc nhớ lại:

```
1. Conversation hiện tại (toàn bộ turns)
2. .claude/project/session_state.md — trạng thái trước đó
3. .claude/CLAUDE.local.md — phase hiện tại
```

### Bước 2 — Tạo Handoff Summary

Viết tóm tắt theo **đúng cấu trúc** bên dưới. Lưu vào:

```
.claude/project/handoff_YYYY-MM-DD.md
```

### Bước 3 — Cập nhật session_state.md

Sau khi tạo handoff summary, cập nhật `session_state.md`:
- Đánh dấu `[x]` các task đã hoàn tất
- Ghi thêm quyết định mới vào bảng "Quyết định đã chốt"
- Cập nhật mục "Đang làm" và "File đang làm việc"
- Thêm bugs/blockers mới nếu có

---

## Cấu trúc Handoff Summary

```markdown
# Handoff Summary — [Ngày] [Giờ]

## 1. Tình trạng hiện tại (1 câu)
> Phase [N] — [Tên phase]. Vừa hoàn tất: [X]. Đang dở: [Y].

## 2. Việc đã làm trong session này

### Hoàn tất ✅
- [Task A] → Kết quả: [file/output cụ thể]
- [Task B] → Kết quả: [file/output cụ thể]

### Đã bắt đầu nhưng chưa xong 🟡
- [Task C] — dừng ở: [bước nào, lý do]
  - File đang sửa: [path]
  - Vấn đề còn lại: [mô tả ngắn]

## 3. Việc cần làm TIẾP THEO (ưu tiên cao → thấp)

1. **[Task tiếp theo 1]** — Agent: [tên agent]
   - Làm thế nào: [prompt gợi ý hoặc tham chiếu Operations Guide]
   - File input: [path]
   - Output mong muốn: [mô tả]

2. **[Task tiếp theo 2]** — Agent: [tên agent]
   - ...

## 4. Quyết định quan trọng đã chốt trong session này

| Quyết định | Lý do |
|---|---|
| [Quyết định A] | [Lý do ngắn] |

## 5. Vấn đề / Blocker cần giải quyết

- 🔴 **[Blocker nếu có]**: [Mô tả] → Cần: [action]
- ⚠️ **[Warning nếu có]**: [Mô tả]

## 6. Tài nguyên liên quan

| Tài liệu | Đường dẫn | Lý do liên quan |
|---|---|---|
| [Tên file] | [path] | [Tại sao cần đọc] |

## 7. Xác nhận chuyển tiếp (Handoff Sign-off)

- **Người thực hiện:** `[Tên Model/Agent của bạn]` đã hoàn thành các công việc trên.
- **Cơ sở thiết kế:** Dựa trên `[Tên file design/plan]`.
- **Chuyển tiếp / Kiểm tra:** Giao lại cho `[Tên Reviewer/Agent tiếp theo]` để xử lý các bước ở mục 3.

## 8. Prompt để bootstrap conversation mới

Paste đoạn sau vào đầu conversation mới:

---
Đọc các file theo thứ tự:
1. `.claude/CLAUDE.local.md` — phase hiện tại, bản đồ tài liệu
2. `.claude/project/session_state.md` — task chi tiết, quyết định đã chốt
3. `.claude/project/handoff_YYYY-MM-DD.md` — tóm tắt session vừa rồi (bao gồm Sign-off)

Sau đó tiếp tục từ: **[Task tiếp theo cụ thể]**
---
```

---

## Ví dụ thực tế

### Ví dụ handoff sau Phase 1 (Data Foundation):

```markdown
# Handoff Summary — 2026-09-15 22:00

## 1. Tình trạng hiện tại
> Phase 1 — Data Foundation. Vừa hoàn tất: crawl + chunking 15/30 VB.
> Đang dở: chunking NĐ 145/2020.

## 2. Việc đã làm

### Hoàn tất ✅
- Crawl BLLĐ 2019 → `data/raw/45_2019_QH14.html`
- Parse + clean BLLĐ 2019 → `data/cleaned/45_2019_QH14.json`
- Chunking BLLĐ 2019 → 287 chunks trong `data/chunks.jsonl`
- Crawl NĐ 12/2022 → done
- Crawl NĐ 74/2024 → done

### Đang dở 🟡
- Chunking NĐ 145/2020 — dừng giữa chừng ở Điều 32
  - File: `data/cleaned/145_2020_ND-CP.json`
  - Vấn đề: Điều 32 có bảng phức tạp, cần xử lý riêng

## 3. Việc cần làm TIẾP THEO

1. **Hoàn tất chunking NĐ 145/2020** — Ingestion Agent
   - Input: `data/cleaned/145_2020_ND-CP.json`
   - Vấn đề Điều 32: tách bảng thành 4 chunks riêng, mỗi chunk = 1 hàng
   - Tham chiếu: Technical Design § 2.2
   - **Yêu cầu bắt buộc (Handoff Sign-off):** Khi hoàn thành, phải để lại xác nhận rõ ràng: "Người thực hiện: [Model] hoàn thành [Task]. Cơ sở thiết kế: Dựa trên [File]. Chuyển tiếp/Kiểm tra: Giao cho [Reviewer/Agent] kiểm tra".

2. **Crawl 15 VB còn lại** — Ingestion Agent
   - Xem danh sách: `data/crawl_plan.md` (cột status = "pending")
   - **Yêu cầu bắt buộc (Handoff Sign-off):** Tương tự như trên.

## 5. Blockers
- ⚠️ thuvienphapluat.vn rate limit sau 50 requests/hour
  → Dùng vanban.chinhphu.vn làm primary source thay thế

## 7. Xác nhận chuyển tiếp (Handoff Sign-off)
- **Người thực hiện:** Gemini 3.1 pro đã hoàn thành crawl và parse 15/30 VB.
- **Cơ sở thiết kế:** Dựa trên plan trong `operations_guide.md`.
- **Chuyển tiếp / Kiểm tra:** Giao lại cho Ingestion Agent phiên sau xử lý tiếp Điều 32, sau đó Reviewer (Sol-Medium) vào kiểm tra toàn bộ chunks.

## 8. Bootstrap prompt

Đọc:
1. `.claude/CLAUDE.local.md`
2. `.claude/project/session_state.md`
3. `.claude/project/handoff_2026-09-15.md`

Tiếp tục: **Hoàn tất chunking NĐ 145/2020** (Điều 32 đang dở)
```

---

## Lưu ý quan trọng

> [!TIP]
> **Handoff summary tốt** = Người đọc không cần hỏi thêm gì, biết ngay làm gì tiếp.

> [!WARNING]  
> KHÔNG viết chung chung như "đã làm một số việc". Phải ghi **file cụ thể**, **bước cụ thể**, **kết quả đo được**.

> [!NOTE]
> Mỗi session chỉ cần 1 handoff file. Nếu session ngắn (< 2 giờ) và ít thay đổi, chỉ cần cập nhật `session_state.md` là đủ, không cần tạo handoff file riêng.

> [!NOTE]
> Nếu summary vào một hand-off đã có thì không ghi đè hay xóa, cập nhật thêm vào file đó đồng thời luôn ghi mốc thời gian được summary.
