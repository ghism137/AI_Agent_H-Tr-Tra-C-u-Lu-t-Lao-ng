# Đầu mối chuỗi pháp lý cho Gate 1 — 17/09/2026

Trạng thái của tất cả mục dưới đây: **candidate cần đối chiếu bản gốc, ngày hiệu lực từng điều khoản và nhóm đối tượng**. Đây là kết quả tra cứu nguồn chính thức để định hướng thu thập, chưa phải sign-off hay provision version. Không đưa các mục này thẳng vào `relations_verified.json`.

**Cập nhật thu thập 17/09/2026:** Bản Công báo toàn số của Luật 71/2025, 113/2025 và 124/2025 đã lưu trong `data/raw/official/`, có SHA-256 ở `acquisition_gaps.json`, chọn đúng khoảng trang và parse vào candidate 40 văn bản. Đã đối chiếu điều sửa/điều hiệu lực: 71 Điều 49(4), 50(1); 113 Điều 29(1)–(2), 30(1); 124 Điều 43(1), 44(1)–(2). **Luật 113 có xung đột ngay trong bản Công báo:** Điều 29 ghi BLLĐ `49/2019/QH14` và BHXH `41/2024/QH14`, khác số hiệu bản gốc trong registry. Luật 124 Điều 43(1) dẫn đúng BLLĐ `45/2019/QH14` và liệt kê Luật 113 là sửa đổi trước đó; bản [Luật 142/2025 trên VBPL](https://vbpl.vn/FileData/TW/Lists/vbpq/Attachments/187584/VanBanGoc_2026_44_142_2025_QH15%20%281%29.pdf) dẫn đúng BHXH `41/2024/QH15` và liệt kê Luật 113. Hai nguồn sau hỗ trợ định danh target, nhưng sự sai khác phải được ghi trong relation review; chưa áp dụng amendment vào version.

## BHXH 41/2024/QH15

- [Luật 73/2025/QH15 (Luật Nhà giáo)](https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=179262&Keyword=) sửa Điều 66 Luật BHXH 41/2024; trang VBPL ghi hiệu lực chung 01/01/2026. Cần trích đúng điều sửa, nội dung và đối tượng nhà giáo.
- **Xung đột metadata nguồn:** [trang Công báo của Luật 41/2024](https://congbao.chinhphu.vn/van-ban/luat-so-41-2024-qh15-42576.htm) hiển thị “Hiệu lực: 29/06/2024” trùng ngày ban hành, trong khi [Điều 140 toàn văn luật trên cổng Chính phủ](https://xaydungchinhsach.chinhphu.vn/toan-van-luat-so-41-2024-qh15-bao-hiem-xa-hoi-119240723163650489.htm) ghi hiệu lực 01/07/2025. Registry phải dùng điều khoản thi hành/bản ký sau đối chiếu, ghi conflict; không copy ngày từ thuộc tính trang Công báo.
- [Hồ sơ hợp nhất 58/VBHN-VPQH](https://vbpl.vn/TW/Pages/vbpq-thuoctinh-hopnhat.aspx?ItemID=182335&View=0) liệt kê cả Luật 73/2025 và Luật 84/2025 trong các văn bản được hợp nhất với Luật 41/2024. Bản hợp nhất xác thực ngày 15/08/2025, nên không chứng minh toàn bộ sửa đổi sau ngày đó.
- [Luật 142/2025/QH15 (Luật Phục hồi, phá sản)](https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=187584), khoản 2 Điều 86, sửa điểm a khoản 1 Điều 37 Luật BHXH 41/2024. Trang VBPL ghi hiệu lực chung 01/03/2026 và nêu các sửa đổi trước bởi Luật 73/2025, 84/2025, 113/2025. Cần kiểm tra điều khoản thi hành có ngoại lệ trước khi gán ngày cho event.
- [Công báo 2026](https://vbpl.moj.gov.vn/TW/Pages/vbpq-print.aspx?ItemID=188248) vẫn dẫn Luật BHXH 41/2024 cùng bốn luật sửa đổi trên. Dùng như cross-check, không làm nguồn thay thế các điều sửa bản gốc.
- [NĐ 162/2026/NĐ-CP tại Công báo](https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-162-2026-nd-cp-469551.htm) điều chỉnh lương hưu, trợ cấp BHXH và trợ cấp hằng tháng; [toàn văn Chính phủ](https://xaydungchinhsach.chinhphu.vn/toan-van-nghi-dinh-162-2026-nd-cp-dieu-chinh-luong-huu-tro-cap-bhxh-va-tro-cap-hang-thang-119260517105056705.htm) ghi ngày ban hành 15/05/2026. Đây là dependency cho các câu hỏi về mức hưởng sau 01/07/2026; cần xác minh điều khoản hiệu lực và đối tượng trước khi đưa vào coverage.

## BHTN và Luật Việc làm

- [NĐ 61/2020/NĐ-CP](https://vbpl.vn/bolaodong/Pages/vbpq-toanvan.aspx?ItemID=142819&Keyword=) sửa NĐ 28/2015/NĐ-CP từ Điều 1; trang VBPL ghi NĐ 61 đã hết hiệu lực toàn bộ. Corpus hiện có NĐ 28 và NĐ 374/2025 nhưng thiếu NĐ 61, nên giai đoạn lịch sử 2020–2025 có thể sai nếu bỏ qua amendment này.
- [Hồ sơ hợp nhất 3922/VBHN-BLĐTBXH](https://vbpl.vn/TW/Pages/vbpq-thuoctinh-hopnhat.aspx?ItemID=147923) ghi NĐ 61 là thành phần hợp nhất của quy định BHTN cũ; dùng để kiểm tra chain và nội dung, không thay ngày hiệu lực văn bản gốc.
- [Trang VBPL của NĐ 374/2025/NĐ-CP](https://vbpl.vn/bonoivu/Pages/vbpq-vanbanlienquan.aspx?ItemID=186281) ghi hiệu lực chung 01/01/2026 và liên kết NĐ 61/2020. Cần đối chiếu điều khoản bãi bỏ/chuyển tiếp với bản ký NĐ 374.
- [Toàn văn Luật 74/2025/QH15](https://vbpl.vn/ninhthuan/Pages/vbpq-toanvan.aspx?ItemID=179273) ghi các hợp đồng tín dụng ký trước hiệu lực được tiếp tục theo luật cũ đã sửa bởi Luật 41/2024; đây là một applicability transition cần giữ theo nhóm hồ sơ.

## Bộ luật Lao động 45/2019/QH14

- [Luật Giáo dục nghề nghiệp 124/2025/QH15, Điều 43](https://vbpl.vn/TW/Pages/vbpq-print.aspx?ItemID=187742) sửa điểm a khoản 2 Điều 59 và khoản 3 Điều 61 BLLĐ 2019, đồng thời văn bản dẫn các sửa đổi trước bởi Luật 71/2025 và Luật 113/2025. Đây là ba amendment dependencies còn thiếu trong registry cho các chủ đề tương ứng.
- [Luật Công nghiệp công nghệ số 71/2025/QH15](https://vbpl.vn/uybandantoc/Pages/vbpq-toanvan.aspx?ItemID=179989) bổ sung khoản 8a vào Điều 154 BLLĐ về trường hợp lao động nước ngoài không thuộc diện cấp giấy phép; [Công báo](https://congbao.chinhphu.vn/van-ban/luat-so-71-2025-qh15-45555.htm) ghi hiệu lực chung 01/01/2026. Điều này liên quan trực tiếp scope NĐ 219/2025; cần kiểm tra ngày áp dụng cụ thể.
- [Công báo Luật Dân số 113/2025/QH15](https://congbao.chinhphu.vn/van-ban/luat-so-113-2025-qh15-468675.htm) ghi ban hành 10/12/2025, hiệu lực chung 01/07/2026. Bản hợp nhất xuất bản sau đó [chỉ rõ điểm sửa ở Điều 29](https://congbaocdn.chinhphu.vn/180507251028987904/2026/3/5/468972-1772691642_v1_1772691941_signed.pdf); cần kiểm tra bản gốc để gắn đúng target provision và ngày riêng.
- [Giải thích chính sách trên cổng Chính phủ](https://xaydungchinhsach.chinhphu.vn/nguoi-lao-dong-huong-tro-cap-thai-san-may-thang-khi-sinh-con-thu-2-119260803104602087.htm) xác nhận khoản 1 Điều 29 Luật Dân số sửa khoản 1 Điều 139 BLLĐ, quy định thời gian nghỉ thai sản khi sinh con thứ hai. Đây là sửa đổi có thể làm sai câu trả lời thực tế về nghỉ thai sản sau 01/07/2026 nếu chỉ dùng BLLĐ gốc; vẫn phải đối chiếu văn bản luật trước khi tạo version.

## BHYT

- [Toàn văn NĐ 188/2025/NĐ-CP](https://vbpl.vn/TW/Pages/ivbpq-toanvan.aspx?ItemID=179711) liệt kê chuỗi sửa Luật BHYT 25/2008: Luật 32/2013, 46/2014, 97/2015, 35/2018, 68/2020, 30/2023 và 51/2024. Corpus hiện không đủ các nguồn này để trình bày bản 25/2008 như nội dung hiện hành.
- Cũng tại NĐ 188, điều khoản hiệu lực/bãi bỏ viện dẫn NĐ 146/2018 đã sửa bởi NĐ 75/2023 và 02/2025, và NĐ 74/2025 cho nhóm quốc phòng/an ninh. Cần kiểm tra đúng phạm vi đối tượng và phần nội dung còn áp dụng.

## Việc phải làm từ các đầu mối

1. Lấy bản ký/Công báo của mỗi văn bản thiếu, lưu raw và SHA-256; ghi source URL, ngày thu thập, locator.
2. Trích đúng điều sửa/bãi bỏ/chuyển tiếp; tách document/provision/fragment scope và effective interval, kể cả ngoại lệ.
3. Xác minh liệu điều khoản có nằm trong 15 coverage hiện tại hay trong 37 văn bản nền; mở coverage dependency khi cần. Không đưa vào corpus chỉ từ căn cứ văn bản khác hoặc search snippet.
4. Duyệt từng event và tạo version/eligibility tests cho trước, tại và sau mốc hiệu lực.
