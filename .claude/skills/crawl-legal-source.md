---
name: crawl-legal-source
description: Thu thập văn bản pháp luật từ nguồn chính thống (vanban.chinhphu.vn, thuvienphapluat.vn). Xử lý rate limiting, dedup, validation. Use when adding new legal documents to corpus.
---

# Crawl Legal Source

> Dùng khi cần thu thập hoặc bổ sung văn bản pháp luật vào corpus.

## Nguồn ưu tiên (theo độ tin cậy)

| # | Nguồn | URL | Ưu điểm | Hạn chế |
|---|---|---|---|---|
| 1 | Cổng TTĐT Chính phủ | vanban.chinhphu.vn | Chính thống nhất, miễn phí | UI phức tạp, pagination |
| 2 | Thư viện Pháp luật | thuvienphapluat.vn | Phong phú, có consolidated | Có anti-scraping, rate limit |
| 3 | Cổng BHXH Việt Nam | baohiemxahoi.gov.vn | Chuyên biệt BHXH/BHYT/BHTN | Ít văn bản hơn |

## Quy trình

### 1. Lập danh sách văn bản cần crawl
- Dựa vào phạm vi trong `Project.md` (mục 1.3, 1.5)
- Core: BLLĐ 2019 + NĐ hướng dẫn + Luật BHXH/BHYT/Việc làm
- Ghi danh sách vào `data/crawl_plan.md`

### 2. Crawl respectfully
```python
import time
import requests

DELAY_SECONDS = 2  # Tối thiểu 2 giây giữa các request
HEADERS = {
    "User-Agent": "LaborLawRAG-Research/1.0 (academic project)"
}

def crawl_page(url: str) -> str:
    time.sleep(DELAY_SECONDS)
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text
```

### 3. Parse & extract
- Loại bỏ: navigation, sidebar, ads, footer
- Giữ: nội dung chính, bảng biểu, phụ lục
- Tools: BeautifulSoup4, regex cho structure recognition

### 4. Validate
Mỗi văn bản sau khi crawl phải có đủ:
```
□ Số hiệu (vd: 45/2019/QH14)
□ Tên đầy đủ
□ Ngày ban hành
□ Ngày hiệu lực
□ Cơ quan ban hành
□ Nội dung text ≥ 100 ký tự
□ Encoding UTF-8 hợp lệ
```

### 5. Dedup
- Kiểm tra `doc_number` đã có trong corpus chưa
- Nếu có: so sánh content → update nếu version mới hơn
- Nếu chưa: thêm mới

### 6. Lưu trữ
```
data/
├── raw/                    # HTML/PDF gốc (để re-parse nếu cần)
│   ├── 45_2019_QH14.html
│   └── 145_2020_ND-CP.html
├── cleaned/                # Text đã clean
│   ├── 45_2019_QH14.json
│   └── 145_2020_ND-CP.json
├── crawl_plan.md           # Danh sách văn bản cần crawl + status
└── crawl_log.json          # Log: URL, timestamp, status, errors
```

## Constraints

- Rate limit: ≤ 1 request / 2 giây — respect robots.txt
- Lưu raw HTML để có thể re-parse nếu cần
- Log MỌI lỗi crawl (URL fail, parse fail, timeout)
- KHÔNG crawl ngoài phạm vi đề tài
- KHÔNG dùng headless browser trừ khi bắt buộc (tiết kiệm resources)
- Nếu bị block: dừng lại, thử lại sau, hoặc chuyển sang nguồn khác

## Checklist sau khi crawl xong

```
□ Tất cả văn bản trong crawl_plan.md đã được crawl hoặc có lý do skip
□ Raw files đã lưu
□ Cleaned files đã validate đủ fields
□ Crawl log không có lỗi critical chưa giải quyết
□ Cập nhật session_state.md
```
