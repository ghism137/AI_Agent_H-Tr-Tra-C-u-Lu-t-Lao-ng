# Phase 1 — các việc còn mở để quay lại xử lý

Ngày ghi: 2026-09-18 (Asia/Ho_Chi_Minh). Trạng thái: **tạm dừng closeout; chưa có nghiệm thu độc lập cho candidate hiện tại**. Đây là danh sách triage, không phải quyết định pháp lý hay kết quả gate mới. Giữ nguyên hai handoff lúc 23:25 để làm lịch sử; `scratch/new_handoff.md` được viết trước lần sửa collision, còn `.claude/project/handoff_2026-09-18.md` được viết sau đó.

## Cách đọc mức độ

- **Critical/High** là tác động nếu đưa corpus này vào retrieval như dữ liệu đã được duyệt.
- **Khó vừa**: sửa một contract/script và regression có phạm vi rõ. **Khó cao**: cần nhiều file, dữ liệu và kiểm thử xuyên pipeline. **Rất khó**: còn phải đọc nguồn pháp lý, đối chiếu đầy đủ corpus hoặc thiết kế lại tính đúng theo thời gian. Đây là ước lượng công việc, không phải kết quả benchmark model.
- Các số bên dưới là ảnh chụp tại thời điểm ghi, có thể đổi sau rebuild. Không dùng `gate*: PASS` riêng lẻ làm dấu hoàn thành issue.

## Ảnh chụp có thể kiểm lại

- `data/staging/phase1-candidate/manifest.json`: `candidate-a13ef4f9d9d0e42c`, 61 văn bản, 20.416 chunks, 20.340 versions, Gate 1/2/3 đều PASS, nhưng `published=false` và `verified_as_of=null`.
- `data/active_release.json` vẫn trỏ `phase1-febf5129f0e33d40`, manifest SHA-256 `ef0c1688a72500c16958c5fcdeafd1893adc998db2cdfdabb8cd344b99e9d4ac`. Đó là release cũ; không được xem PASS của candidate mới là nghiệm thu release cũ hoặc ngược lại.
- `data/registry/operations.json`: 15 operation `verified`, gồm 13 stub `applicability` và 2 `replace`; cả 15 có `source_hash`/`target_hash` bằng chuỗi `unknown`.
- `reports/phase1-closeout/checklist.json`: 46/61 document, 15/15 coverage item và 30/30 sample review còn `pending`; các trường này mâu thuẫn với checklist M1–M8 toàn `yes` tại `phase1_closeout_checklist.json`.
- Chạy `venv/Scripts/python.exe scratch/check_chunk_collision.py` với `PYTHONPATH=.`: exit 0, không in `Collision!`. Phép thử chỉ dựng lại NĐ 145/2020 và không in số lượng chunk đã kiểm.
- `scratch/task-4265.log` được hai handoff viện dẫn nhưng hiện không có. `reports/phase1-closeout/packets/` cũng chưa có. Review độc lập lúc 10:50 trong `sol_review_2026-09-18_1050.md` là findings trên head trước đó, không tự động áp dụng nguyên trạng cho candidate 23:25; chưa tìm thấy sign-off mới trên đúng candidate này.

## Tồn đọng ưu tiên

| ID | Mức độ / độ khó | Vấn đề và căn cứ | Điều kiện đóng |
|---|---|---|---|
| P1-01 | **Critical / rất khó** | 13 stub được gán `verified` để thỏa quan hệ bắt buộc; hai operation `replace` cũng dùng hash `unknown`. Gate 3 tại `scripts/build_phase1_stage.py` kiểm giá trị có mặt, không xác nhận hash nguồn/đích thật. `backend/ingestion/version_builder.py` áp dụng `applicability` bằng cách ghi lại `valid_from`; một stub rộng có thể đổi eligibility. | Loại hiệu lực giả khỏi corpus được duyệt; mỗi relation cần operation đúng verb, clause, target, payload/precondition, hash nguồn thật, review refs và đối chiếu pháp lý. Gate phải reject placeholder và ref sai. Rebuild rồi kiểm versions/chunks theo ngày và phạm vi. |
| P1-02 | **Critical / rất khó** | Chuỗi sửa đổi, bãi bỏ một phần, hồi tố, nhóm đối tượng và chuyển tiếp chưa có chứng cứ đầy đủ. Review độc lập 10:50 đã tìm sai nghĩa ở NĐ 188/2025, NĐ 75/2023, NĐ 74/2025 trên bản trước; cần kiểm lại thay đổi sau review, không coi findings đã tự giải quyết. Kế hoạch closeout 18/09 yêu cầu đủ 15 coverage items và 6 nhóm pháp lý. | Đối chiếu từng effect với văn bản gốc, target clause và khoảng ngày; xử lý mọi findings còn tái hiện; legal review có source hash, locator, scope, reviewer thật; unknown vẫn unknown khi thiếu evidence. |
| P1-03 | **High / rất khó** | Review fidelity toàn văn bản/section chưa hoàn tất: checklist vẫn còn 46 document và 30 sample pending. Candidate tăng từ 3.110 lên 20.416 chunks, nên review mẫu/release cũ không thể tự chứng nhận candidate mới. | Có manifest section và hash đủ cho 61 văn bản cùng mọi dependency trong scope; đối chiếu raw→parsed→versions→chunks, xử lý exception và stale review; reviewer xác nhận vùng thay đổi trên đúng input pinned. |
| P1-04 | **High / khó cao** | Materialization hiện sửa `valid_from`/`valid_to` trực tiếp trên version, có fallback payload sang nội dung đích và match document scope rộng (`version_builder.py:99–195`). Nguy cơ xóa lịch sử/đổi hiệu lực sai khi nhiều operation giao nhau. | Áp dụng deterministic với precondition và thứ tự rõ, giữ lineage, phân biệt partial/full repeal, replace/add, interval/population; regression source-backed trước/trong/sau ngày hiệu lực và trường hợp thiếu dữ kiện. |
| P1-05 | **High / khó cao** | Gate/acceptance chưa ràng buộc đầy đủ evidence: Gate 2 đọc `legal_verification.json` status PASS; Gate 3 cho `unknown` lọt. `phase1_closeout_checklist.json` ghi M1–M8 `yes` nhưng checklist chi tiết còn pending. | Tách technical PASS, legal/fidelity acceptance và reviewer sign-off; các gate fail khi thiếu/stale/hash sai/placeholder; lưu lệnh, exit code, input/output hashes và kết quả lỗi cố ý. Chỉ ghi `yes` cho checkpoint đã có evidence tương ứng. |
| P1-06 | **High / khó cao** | Release và handoff không cùng đối tượng: active pointer là release cũ, staging candidate mới chưa publish. Chưa có packet/sign-off trên đúng candidate mới; log được dẫn chiếu bị thiếu. | Pin input+candidate+evidence digest, reviewer độc lập nghiệm thu, kiểm immutable publish/rollback/reproducibility và active pointer; ghi release ID, manifest hash, thời điểm, reviewer, hạn chế trong handoff mới. |
| P1-07 | **Medium / khó vừa** | Hai handoff 23:25 mâu thuẫn về collision. Script hiện không báo collision cho NĐ 145/2020 nhưng chỉ kiểm một văn bản và dùng công thức UUID riêng so với `chunker_v2.py`; build có kiểm unique ID trước materialization (`build_phase1_stage.py:162–164`), cần kiểm lại output sau materialization. | Một phép kiểm trên toàn `chunks.jsonl` của candidate/release và sau `chunk_versions`, báo số chunks, số ID duy nhất, ID trùng và command/exit code; regression cho nguồn từng gây trùng. Không giữ blocker collision nếu không tái hiện. |
| P1-08 | **Medium / khó vừa** | Tài liệu trạng thái không nhất quán: handoff mới nói Phase 1 `Closed out`, `session_state.md` có cả PASS lịch sử và phần “Đang làm” ghi Gate 1 FAIL, checklist tổng `yes` trong khi checklist chi tiết pending. | Khi quay lại, cập nhật một trạng thái chuẩn theo candidate/release đã pin; các handoff cũ giữ lịch sử và ghi superseded; không tự gán sign-off. |

## Gợi ý phân công khi mở lại

- **Builder chính: GPT-6 Astra high/xhigh** cho P1-01–P1-05, vì cần giữ đồng thời schema, dữ liệu, temporal semantics, gate và bằng chứng pháp lý. Nếu giới hạn sử dụng/chi phí là yếu tố quyết định, **GPT-5.6 Sol high** cũng có thể làm builder theo từng checkpoint nhỏ, nhưng cần cùng bộ kiểm thử và review độc lập. Đây là khuyến nghị theo độ phức tạp công việc, không phải bảo đảm model tự xác minh luật đúng.
- **Sol-medium (GPT-5.6 Sol medium): reviewer độc lập** cho diff, hash/evidence, regression và verdict từng checkpoint; không nên vừa sửa vừa tự ký trên cùng candidate. Sol-medium phù hợp sửa P1-07/P1-08 hoặc lỗi code hẹp khi một reviewer khác sẽ nghiệm thu. Nếu Sol-medium làm builder, đổi reviewer sang một phiên độc lập khác với input hashes rõ ràng.
- Phần đối chiếu nguồn và quyết định pháp lý ở P1-02/P1-03 vẫn cần người có thẩm quyền review thực tế. Model hỗ trợ tìm sai lệch và lập hồ sơ, không thay chữ ký pháp lý/acceptance nếu dự án yêu cầu.
- Không tự bắt đầu agent, build, publish hay sửa dữ liệu khi đọc file này. Khi mở lại, bắt đầu từ WP0 của `.claude/project/phase1_closeout_plan_2026-09-18.md`, tái xác nhận hiện trạng và tránh dùng các số ảnh chụp trên như kết quả mới.

## Nguồn nội bộ chính

- `.claude/project/phase1_closeout_plan_2026-09-18.md` — scope, WP0–WP8 và acceptance.
- `reports/phase1-closeout/sol_review_2026-09-18_1050.md` — findings độc lập trên head trước candidate hiện tại.
- `data/staging/phase1-candidate/manifest.json`, `data/active_release.json`, `data/registry/operations.json` — trạng thái kỹ thuật hiện thấy.
- `reports/phase1-closeout/checklist.json`, `reports/phase1-closeout/phase1_closeout_checklist.json`, `reports/phase1-closeout/checkpoint_ledger.jsonl` — trạng thái review/checkpoint cần hòa giải.
