# Review Phase 1 và thiết kế kỹ thuật

Ngày review: 2026-09-16. Phạm vi: mã ingestion/relation/graph, toàn bộ JSONL/JSON hiện có, nguồn Markdown/DOCX và các nguồn chính thức được ghi bên dưới.

## Tổ chức tài liệu sau phản hồi người dùng

Báo cáo này giữ nguyên findings tại thời điểm review. Thiết kế chi tiết v1.2 được [lưu tham khảo](design_review_v1.2.md). Bản tổng thể được giữ theo cấu trúc v1.1 và đính chính thành v1.3; triển khai theo `phase1_design.md`/`phase2_design.md`. Baseline bắt đầu đơn giản, không yêu cầu toàn bộ thiết kế nâng cao trước lần đo đầu.

## Kết luận

**Quality Gate 1: FAIL — cần mở lại Phase 1 trước khi index corpus chính thức.** Có nền tảng parser/chunker, dữ liệu nguồn và unit tests để tiếp tục; chưa có corpus đủ độ tin cậy cho Legal RAG. Không cần thay toàn bộ stack, nhưng cần sửa thiết kế dữ liệu và temporal retrieval trước Phase 2.

Đây là review và thiết kế, không phải bản sửa production. Mã trong `backend/`, dữ liệu nguồn và các file corpus được giữ nguyên. Script audit chỉ đọc và ghi báo cáo. Chưa chạy embedding, Qdrant hay evaluation retrieval; không có số liệu chứng minh chất lượng retrieval.

## 1. Phương pháp và số liệu tái lập

Chạy tại thư mục gốc:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& './venv/Scripts/python.exe' -m pytest tests -q -p no:cacheprovider
& './venv/Scripts/python.exe' scripts/audit_phase1.py
```

Kết quả unit tests: **10 passed**. Các test corpus hiện chỉ kiểm tra vài khóa của phần tử đầu tiên; kết quả này không đồng nghĩa Quality Gate 1 PASS.

Số liệu toàn corpus, xem [audit.json](audit.json) để lấy checksum, số dòng và mẫu tái lập:

- 107 DOCX đếm đệ quy; 102 Markdown; 103 cleaned JSON. Có 5 nhóm DOCX trùng basename, nhưng khác SHA-256. Không được coi các bản này là cùng một nguồn chỉ vì cùng tên.
- 2.041 chunks, **1.969 chunk ID duy nhất**; 36 nhóm trùng ID, 72 dòng dư nếu ép thành map theo ID. Có 27 nhóm trùng nội dung chính xác, 29 dòng dư; trùng nội dung cần xét phiên bản trước khi loại bỏ.
- **1.225 chunks** thuộc NĐ/TT/QĐ có số hiệu bị thay sai dấu gạch ngang. Tổng 1.480 chunks không khớp mẫu canonical số/năm/cơ quan của audit, bao gồm cả tên biểu mẫu đang bị dùng như số hiệu văn bản.
- **1.594/2.041 (78,1%)** thiếu ngày hiệu lực. Toàn bộ 2.041 chunks thiếu URL nguồn có giá trị.
- Sáu field trong schema v1.1 không xuất hiện: `issued_date`, `expiry_date`, `clause_range`, `content_length`, `source_url`, `crawled_at`. Một số có alias (`issue_date`, `chunk_length`, `url`), nhưng `clause_range` bị mất thực sự và chưa có schema version/migration.
- 142 chunks trên 2.000 ký tự; dài nhất **267.523 ký tự**. Đây là số ký tự, không phải số token. 244 chunks mang article `ALL*`; 28 chunks chưa ở Unicode NFC.
- Có **95 relations**, không phải 104 như session state; 90 không có ngày hiệu lực; 29 records nằm trong danh sách cần review. Không có evidence/reviewer metadata đủ để xác nhận duyệt.
- Crawl plan có 30 dòng nhưng chỉ 28 số hiệu khác nhau; chưa phải 30 văn bản đã được đối chiếu.

## 2. Findings — Critical

### F01 / P1 — BLLĐ 2019 biến mất khỏi corpus được xuất

**Vị trí:** `backend/ingestion/pipeline.py:64–72`, `data/chunks.jsonl`; cleaned còn `Bộ luật Lao động số 45-2019-QH14.json`.

**Bằng chứng:** 0 chunk có `doc_number=45/2019/QH14`; cleaned còn 220 article records mang ID này, nhưng không có Markdown tương ứng trong đầu vào pipeline. BLLĐ 2012 có 246 chunks và bị đánh dấu hết hiệu lực. Vì vậy lọc trạng thái không thể tự khôi phục luật nền tảng cho câu hỏi hiện tại.

**Nguyên nhân:** Chỉ glob một thư mục Markdown rồi ghi đè JSONL, không kiểm tra coverage theo manifest; thư mục cleaned giữ file từ lần chạy khác.

**Sửa:** Manifest phải liệt kê và xác thực nguồn bắt buộc, checksum và document identity; build vào release mới, kiểm tra coverage trước publish. Khôi phục nguồn BLLĐ 2019 được đối chiếu rồi reparse, không ghép mù cleaned cũ vì chính hierarchy của file này cũng có lỗi.

### F02 / P1 — Danh tính văn bản không nối được với metadata và graph

**Vị trí:** `backend/ingestion/pipeline.py:76–107`.

**Bằng chứng:** `145-2020-NĐ-CP` thành `145/2020/NĐ/CP`, trong khi metadata/relations dùng `145/2020/NĐ-CP`. `_normalize_doc_number()` chỉ được dùng ở extractor; test hàm này không bao phủ pipeline. Một file tên `Luật Bảo hiểm xã hội 58-2014-QH13.md` thực tế mở đầu là Luật BHYT **25/2008/QH12**, nhưng 55 chunks dùng cả tên file làm `doc_number`.

**Impact:** Mất hiệu lực, không nối được sửa đổi, sai tên citation, phân loại QĐ thành TT. Tên file không phải nguồn sự thật.

**Sửa:** Registry đối chiếu nội dung/số ký hiệu/nguồn, dùng chung một normalization function, có alias được duyệt. Kiểm tra foreign keys xuyên raw → cleaned → chunks → relations; tách `source_id` khỏi `doc_id`.

**Thứ tự sửa quan trọng:** Không chỉ sửa normalization rồi chạy lại pipeline cũ: các quan hệ sai toàn văn ở F05 sẽ bắt đầu match và có thể làm mất hiệu lực cả văn bản.

### F03 / P1 — Điều trong phụ lục/biểu mẫu bị gán thành Điều của Nghị định

**Vị trí:** `backend/ingestion/parser.py:67–92`, `backend/ingestion/chunker.py:121–125`.

**Bằng chứng:** `145-2020-NĐ-CP_D1` xuất hiện ở các dòng JSONL 1009, 1172, 1180, 1188. Nội dung lần lượt là phạm vi điều chỉnh, quyết định trích ký quỹ, quyết định thu hồi giấy phép và mẫu hợp đồng. `D115_K1-K2` cũng lặp với hai nội dung khác nhau. 36 nhóm ID collision đã kiểm tra trên toàn bộ dữ liệu.

**Impact:** Citation sai Điều; nếu dùng ID này cho upsert/map thì mất 72 records. UUID hóa chuỗi ID cũ không khắc phục collision.

**Sửa:** Parser có trạng thái body/annex/form/quoted-amendment và structural path. ID gồm văn bản + phiên bản + loại nội dung + đường dẫn cấu trúc + chunk part; duplicate key phải làm build thất bại.

### F04 / P1 — Chuyển DOCX mất numbering, parser che lỗi bằng ALL

**Vị trí:** nguồn `data/raw/word/Luật-84-2015-QH13.docx`, bản Markdown cùng tên; `backend/ingestion/parser.py:94–101`.

**Bằng chứng:** XML gốc của đoạn “Phạm vi điều chỉnh” có `numId=1`, trỏ đến abstract numbering với format `Điều %1.`. Markdown chỉ giữ tên điều, không giữ numbering. Cleaned của Luật ATVSLĐ có một article `ALL`, rồi sinh 81 chunks không có số Điều chuẩn.

**Sửa:** Đọc numbering, numbering overrides, styles và thứ tự paragraph/table của DOCX; lưu source spans. Với tài liệu loại luật mà không phát hiện được Điều, fail/quarantine; chỉ dùng ALL khi registry xác nhận nguồn là biểu mẫu/phụ lục không có Điều. Không suy số Điều theo thứ tự một cách thiếu căn cứ, không dùng OCR.

### F05 / P1 — Regex proposals được phát hành như quan hệ pháp lý đã xác minh

**Vị trí:** `backend/ingestion/extract_relations.py:42–89,138–166`; `backend/ingestion/pipeline.py:33–59`.

**Bằng chứng thực:** Relations chứa `70/2023/NĐ-CP thay_the toan_bo 152/2020/NĐ-CP` và `70/2023/NĐ-CP bai_bo toan_bo 35/2022/NĐ-CP`. Markdown NĐ 70 nói thay **cụm từ/biểu mẫu** và bãi bỏ **một số quy định**. Trang [NĐ 70 chính thức](https://chinhphu.vn/?docid=208673&pageid=27160) xác định đây là nghị định sửa đổi, bổ sung; đối chiếu bản ký ở trang đó khi duyệt từng scope.

**Bằng chứng tái lập:** Câu dẫn Hiến pháp đã được sửa đổi theo NQ 51/2001 bị diễn giải thành BLLĐ 2012 sửa đổi NQ đó. Giới hạn 300 ký tự hoặc chấm/chấm phẩy không giải quyết được chủ thể pháp lý. `seen=(source,target,type)` còn loại mất những scope khác nhau của cùng cặp văn bản; tất cả proposals có `status=active`.

**Sửa:** Tách candidate và verified relations; bắt buộc source provision, target locators, evidence span, ngày hiệu lực và người duyệt. “Không thấy Điều trong cửa sổ” phải là `scope=unknown`, không suy toàn bộ. Dedup phải bao gồm scope/target locator/operation/date. `bo_sung` cũng là thay đổi pháp lý cần duyệt.

### F06 / P1 — Kiểm tra hiệu lực sai cả lịch sử lẫn sửa đổi một phần

**Vị trí:** `backend/retrieval/graph_utils.py:30–62`; `backend/ingestion/pipeline.py:43–59`; `backend/ingestion/relations_builder.py:39–46`.

**Bằng chứng:** Quan hệ không có ngày được áp dụng kể cả `reference_date=1900-01-01`; `status=rejected` vẫn vô hiệu hóa; target `Điều 1 và 2` không match `Điều 1`. `mot_so_dieu` bị bỏ qua. Sửa một khoản có thể vô hiệu hóa cả Điều. Seed NĐ 35 dùng **28/05/2022** là ngày ban hành; ngày hiệu lực là **15/07/2022**, theo [nguồn Chính phủ](https://chinhphu.vn/?docid=205861&pageid=27160).

**Sửa:** Resolver theo phiên bản provision và khoảng `[valid_from, valid_to)`, chỉ dùng verified events. Phân biệt chưa có hiệu lực, đã hết, chưa rõ và điều kiện chuyển tiếp. Thiếu evidence/date không được tự gán còn hiệu lực. Sửa đổi một phần phải giữ phần không bị sửa và dẫn bản sửa đổi đúng.

### F07 / P1 — Corpus thiếu các thay đổi đã có hiệu lực trước ngày review

**Vị trí:** `data/documents_metadata.json`, crawl plan, relations và thiết kế v1.1 §2.1/4.5.

**Bằng chứng:** 58/2014 có 139 chunks và 38/2013 có 62 chunks mang trạng thái `con_hieu_luc`, trong khi thiếu luật thay thế trong output. Điều 140 Luật BHXH 41/2024 có hiệu lực 01/07/2025; Điều 54 Luật Việc làm 74/2025 có hiệu lực 01/01/2026. Điều 5 NĐ 293/2025 có hiệu lực 01/01/2026 và chấm dứt hiệu lực NĐ 74/2024.

Nguồn: [Luật BHXH 2024, Điều 140 và chuyển tiếp Điều 141](https://xaydungchinhsach.chinhphu.vn/toan-van-luat-so-41-2024-qh15-bao-hiem-xa-hoi-119240723163650489.htm), [Luật Việc làm 2025, Điều 54–55](https://xaydungchinhsach.chinhphu.vn/toan-van-luat-viec-lam-119250711173403835.htm), [NĐ 293/2025, Điều 5](https://xaydungchinhsach.chinhphu.vn/nghi-dinh-so-293-2025-nd-cp-quy-dinh-muc-luong-toi-thieu-doi-voi-nguoi-lao-dong-lam-viec-theo-hop-dong-lao-dong-119251110172808433.htm).

**Sửa:** Xây coverage matrix theo chủ đề/ngày áp dụng, bổ sung/verify văn bản mới và hướng dẫn, giữ phiên bản cũ cho lịch sử/chuyển tiếp. Những ví dụ trên chứng minh snapshot chưa sẵn sàng; không phải danh sách đầy đủ mọi cập nhật pháp luật đến 16/09/2026.

### F08 / P1 — Không có provenance đủ để xác minh citation

**Vị trí:** `backend/ingestion/chunker.py:140–162`; registry và schema hiện hành.

**Bằng chứng:** 2.041 URL rỗng; không có source hash/span trong chunks; `clause_range` truyền vào `build_chunk()` nhưng không ghi ra JSON. 107 DOCX bị flatten thành 102 Markdown, với 5 nhóm basename trùng mà bytes khác nhau. Audit chứng minh collision và mất sự phân biệt; chưa có mã converter trong repo để kết luận chính xác cơ chế overwrite.

**Sửa:** Giữ relative path/namespace và hash của mọi nguồn; đối chiếu duplicate theo nội dung và lineage; version hóa annex/form theo văn bản ban hành. Citation phải resolve được về nguồn, version và vị trí gốc.

## 3. Findings bổ sung

### F09 / P1 — Watermark filter có thể xóa cả quy định hợp lệ

`backend/ingestion/parser.py:16–31`: “1. Tuân thủ pháp luật Việt Nam.” bị xóa vì chứa `luật việt nam`; dòng chứa `www.` cũng bị xóa toàn bộ. Đây là **reproduction**, không khẳng định mọi corpus hiện tại đã bị mất đúng câu mẫu đó. Chỉ xóa watermark có cấu trúc được whitelist, giữ transformation log và đối chiếu text trước/sau.

### F10 / P2 — Hierarchy, quoted articles và giới hạn chunk chưa đúng

`parser.py:42–67`: không reset Mục khi sang Chương; Điều `1a` bị nhập vào Điều 1. Thực tế BLLĐ 2012 Điều 59 mang Mục 5 của chương trước. `Phần` matching lỏng còn làm metadata của cleaned BLLĐ 2019 nhận chuỗi “phần vốn nhà nước tại doanh nghiệp;”.

Parser không đóng Điều tại annex nên chunk `11-2020-TT-BLĐTBXH_D3_K3-K4` có **267.523 ký tự** (JSONL 1906), chứa cả danh mục nghề. Không được giải quyết bằng truncate embedding. Thiết kế phải có cây cấu trúc, child retrieval + parent evidence, và hard token budget không mất dữ liệu.

### F11 / P2 — Build chưa có tính toàn vẹn, relations vẫn có hai writer

`pipeline.py:72,135–138` ghi đè file chính trước khi hoàn tất và chỉ log exception; dữ liệu một phần vẫn có thể được báo là xong. `relations_builder.py:61–76` vẫn ghi đè file relations bằng 5 seed khi chạy module, trái với log “một điểm tích hợp duy nhất”. Các list sinh từ set và glob không sort làm output khó tái lập; dedup relation có thể giữ target scope khác tùy thứ tự.

Sửa bằng staging release + validations + atomic manifest publish, exit khác 0 khi lỗi nguồn bắt buộc; seed là input, không có writer độc lập. Pin dependencies và ghi tool/model versions. Đây là thiết kế sửa, chưa triển khai trong lần review.

### F12 / P2 — Quality Gate và báo cáo cũ không có bằng chứng đủ

`tests/test_data_quality.py:14–45` chỉ kiểm tra phần tử đầu; không test coverage, unique ID, provenance hay temporal truth. Báo cáo ingestion còn ghi “mock”, 33 văn bản; state ghi 107/104; output đo được 102 Markdown/95 relations. Không tìm thấy report sampling/sign-off đủ xác nhận gate đã PASS.

Sửa bằng report gắn input checksums, schema validation mọi record, coverage theo manifest, test corpus adversarial và reviewer evidence. Không sử dụng số chunk tối thiểu làm mục tiêu chất lượng vì tách biểu mẫu có thể làm số lượng tăng mà retrieval tệ hơn.

## 4. Sampling và giới hạn xác minh

Seed random cố định **20260916**, 10 dòng JSONL: **88, 223, 326, 757, 784, 1319, 1357, 1398, 1783, 1930**. 10/10 có các dòng nội dung tìm thấy trong Markdown tương ứng theo phép so khớp của audit; phép này không chứng minh đúng thứ tự, đúng luật hay đủ context. 0/10 có URL; 8/10 thiếu ngày hiệu lực. Vì vậy **không gọi đây là 10/10 PASS đối chiếu nguồn chính thức**.

Năm boundary checks (chọn có chủ đích): các dòng **1188, 1171, 1906, 1273, 986**, tương ứng mẫu HĐLĐ giả làm Điều 1 NĐ 145; biểu mẫu lọt vào Điều 115; danh mục nghề lọt Điều 3 TT 11/2020; mẫu QĐ lọt Điều 4 NĐ 152; phụ lục lọt Điều 9 NĐ 135. Xem `boundary_samples` trong audit JSON.

Ba kiểm tra relation có chủ đích: BLLĐ 2019 → 2012 có seed nhưng thiếu source trong index; NĐ 70 → NĐ 152 bị suy thay thế toàn bộ; NĐ 35 → NĐ 145 sai ngày và thiếu target khoản cụ thể. Không đủ điều kiện để sign-off coverage toàn graph.

Đã kiểm tra một số nguồn Chính phủ; nhiều endpoint VBPL/VBCP cũ trả 403/502 hoặc không đọc được. Chưa hoàn tất đối chiếu thủ công mọi mẫu với bản ký chính thức, chưa kiểm kê đầy đủ pháp luật năm 2026. Các điều còn chưa xác minh được giữ là blocker, không suy thành PASS. Việc xem cấu trúc DOCX dùng XML gốc, không dùng OCR và không thay nguồn trong corpus.

## 5. Đánh giá thiết kế v1.1

**Giữ:** ba module tách biệt, deterministic calculations, source-grounded generation, FastAPI/Pydantic, BGE-M3, BM25 + dense + RRF, ngân sách API $0, quality gates.

**Sửa bắt buộc:** registry/provenance; parser nhận biết numbering và annex/form; schema versioned; verified relations; resolver theo thời điểm và khoản/điểm; build đồng bộ BM25/Qdrant; coverage luật cập nhật; citation có evidence; eval theo logical provision.

Các khẳng định kỹ thuật cần sửa:

- BGE-M3 chuẩn có vector 1.024 chiều, context tối đa 8.192 token. Model card không phải căn cứ cho cam kết cắt còn 512 chiều giữ chất lượng hoặc số liệu top VN-MTEB; giữ 1.024 chiều và benchmark domain. BGE sparse là một lựa chọn riêng, không đồng nhất với BM25. [Model card chính thức](https://huggingface.co/BAAI/bge-m3).
- `QdrantClient(path=...)` là embedded local mode; payload indexes không có tác dụng như server. Thiết kế mới phân biệt embedded cho tests/smoke và server local cho integration/benchmark, không hứa filter O(1). [Mã nguồn qdrant-client](https://github.com/qdrant/qdrant-client/blob/master/qdrant_client/local/qdrant_local.py).
- `status != het_hieu_luc` không loại văn bản chưa hiệu lực/unknown và không trả đúng lịch sử. Filter phải dùng cùng predicate cho cả BM25 và dense, đồng thời kiểm tra phạm vi sửa đổi.
- `P@5 >= 0.70` không khả thi cho câu chỉ có một relevant provision (trần P@5 là 0.20). Báo cáo P@5 đúng định nghĩa; dùng Recall@5/nDCG@5/MRR làm gate, negatives đánh giá riêng.
- Các công thức mẫu của v1.1 không phải đặc tả pháp lý đủ dùng: phép năm có off-by-one ở mốc đủ 5 năm, thiếu mức 16 ngày; BHTN thiếu cap/eligibility/version; ví dụ thiếu thời gian BHTN không được mặc định 0. Thiết kế mới yêu cầu rule specification được duyệt trước implementation. [Giải thích Điều 113–114 trên Cổng Chính phủ](https://chinhsachonline.chinhphu.vn/nhan-vien-truong-hoc-co-duoc-nghi-he-khong-63703.htm).
- Quota/model availability không cố định: [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), [HF pricing](https://huggingface.co/docs/inference-providers/pricing), [Groq models](https://console.groq.com/docs/models). Không đưa quota ước lượng vào SLA hay kích hoạt dịch vụ trả phí.

## 6. Thứ tự khắc phục và điều kiện mở Phase 2

1. Xác minh inventory/identity/nguồn BLLĐ 2019 và BHYT; bảo toàn các bản DOCX cùng tên; lập coverage matrix hiện hành/lịch sử.
2. Chuẩn hóa ID và schema cùng với việc cách ly relations chưa duyệt. Khôi phục Word numbering, phân biệt body/annex/form/quoted amendment.
3. Hoàn thiện temporal events/evidence, sửa seed và duyệt tác động theo khoản/điểm; viết regression cho các lỗi trên.
4. Rebuild vào release mới, kiểm tra toàn bộ uniqueness/provenance/schema/coverage, đo token bằng tokenizer thực tế.
5. Sampling nguồn chính thức có evidence; chỉ publish khi không còn Critical. Sau đó mới embed/index corpus được duyệt. Có thể chuẩn bị môi trường BGE/Qdrant bằng fixtures trong thời gian sửa dữ liệu.

Thiết kế triển khai hiện hành nằm trong `phase1_design.md` và `phase2_design.md`; `technical_design.md` giữ vai trò tổng thể. Việc cập nhật design và ghi issue hoàn thành; việc sửa dữ liệu/production code và đóng Quality Gate 1 còn mở.
