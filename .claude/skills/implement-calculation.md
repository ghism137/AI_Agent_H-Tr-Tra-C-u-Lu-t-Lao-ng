---
name: implement-calculation
description: Skill for implementing rule-based legal calculation functions with mandatory legal basis citation, Pydantic models, unit tests, and edge case handling. Use when adding or modifying a legal calculation formula.
---

# Implement Legal Calculation

> Dùng khi cần implement hoặc sửa đổi một công thức tính toán pháp lý.

## Checklist bắt buộc

```
□ 1. Xác định căn cứ pháp lý (Điều/Khoản cụ thể, số hiệu văn bản)
□ 2. Viết công thức toán học + định nghĩa mọi biến
□ 3. Xác định edge cases:
     - Giá trị biên (0 năm, 0.5 năm, giá trị max)
     - Thiếu tham số bắt buộc
     - Giá trị âm hoặc phi logic
     - Thay đổi theo thời gian (mức lương tối thiểu, tỷ lệ đóng BHXH)
□ 4. Tạo Pydantic input model (với Field validation)
□ 5. Tạo Pydantic output model (result, formula, legal_basis, breakdown, warnings)
□ 6. Implement hàm tính toán (Python thuần, KHÔNG dùng LLM)
□ 7. Viết ≥ 5 unit tests:
     - 2 cases thường (happy path)
     - 1 case giá trị biên
     - 1 case thiếu tham số / giá trị phi logic → expect error
     - 1 case edge case pháp lý (ví dụ: mức tối thiểu trợ cấp mất việc)
□ 8. Chạy tests — PHẢI pass 100%
□ 9. Thêm docstring với căn cứ pháp lý
□ 10. Cập nhật session_state.md (đánh dấu task hoàn thành)
```

## Template code chuẩn

```python
from pydantic import BaseModel, Field
from typing import Optional

class TroCapThoiViecInput(BaseModel):
    """Input cho tính trợ cấp thôi việc.
    Căn cứ: Điều 46, Khoản 1, BLLĐ 2019 (45/2019/QH14)
    """
    luong_binh_quan_6_thang: float = Field(
        ..., gt=0,
        description="Tiền lương BQ 6 tháng liền kề theo HĐLĐ (VNĐ)"
    )
    tong_thoi_gian_lam_viec: float = Field(
        ..., ge=0,
        description="Tổng thời gian làm việc thực tế (năm)"
    )
    thoi_gian_dong_bhtn: float = Field(
        default=0, ge=0,
        description="Thời gian đã tham gia BHTN (năm)"
    )
    thoi_gian_da_nhan_tro_cap: float = Field(
        default=0, ge=0,
        description="Thời gian đã được chi trả trợ cấp trước đó (năm)"
    )

class CalculationOutput(BaseModel):
    """Output chuẩn cho mọi hàm tính toán"""
    result: float
    result_formatted: str
    formula_used: str
    legal_basis: str
    breakdown: list[str]
    warnings: list[str] = []


def tinh_tro_cap_thoi_viec(input: TroCapThoiViecInput) -> CalculationOutput:
    """
    Tính trợ cấp thôi việc.

    Căn cứ: Điều 46, Khoản 1, Bộ luật Lao động 2019 (45/2019/QH14)
    Công thức: TC = 1/2 × L_bq × N
    Trong đó:
      - L_bq: tiền lương BQ 6 tháng liền kề
      - N: thời gian làm việc tính trợ cấp
         = tổng thời gian - thời gian BHTN - thời gian đã nhận trợ cấp
    """
    n = (input.tong_thoi_gian_lam_viec
         - input.thoi_gian_dong_bhtn
         - input.thoi_gian_da_nhan_tro_cap)

    warnings = []
    if n <= 0:
        return CalculationOutput(
            result=0,
            result_formatted="0 VNĐ",
            formula_used="TC = 1/2 × L_bq × N (N ≤ 0 → không được trợ cấp)",
            legal_basis="Điều 46, Khoản 1, BLLĐ 2019 (45/2019/QH14)",
            breakdown=[f"N = {input.tong_thoi_gian_lam_viec} - {input.thoi_gian_dong_bhtn} - {input.thoi_gian_da_nhan_tro_cap} = {n} ≤ 0"],
            warnings=["Thời gian tính trợ cấp ≤ 0, không đủ điều kiện nhận trợ cấp thôi việc."]
        )

    result = 0.5 * input.luong_binh_quan_6_thang * n

    return CalculationOutput(
        result=result,
        result_formatted=f"{result:,.0f} VNĐ",
        formula_used="TC = 1/2 × L_bq × N",
        legal_basis="Điều 46, Khoản 1, BLLĐ 2019 (45/2019/QH14)",
        breakdown=[
            f"L_bq = {input.luong_binh_quan_6_thang:,.0f} VNĐ",
            f"N = {input.tong_thoi_gian_lam_viec} - {input.thoi_gian_dong_bhtn} - {input.thoi_gian_da_nhan_tro_cap} = {n} năm",
            f"TC = 0.5 × {input.luong_binh_quan_6_thang:,.0f} × {n} = {result:,.0f} VNĐ"
        ],
        warnings=warnings
    )
```

## Ví dụ unit test

```python
import pytest
from calculations import tinh_tro_cap_thoi_viec, TroCapThoiViecInput

def test_basic_case():
    result = tinh_tro_cap_thoi_viec(TroCapThoiViecInput(
        luong_binh_quan_6_thang=10_000_000,
        tong_thoi_gian_lam_viec=5,
    ))
    assert result.result == 25_000_000

def test_with_bhtn_deduction():
    result = tinh_tro_cap_thoi_viec(TroCapThoiViecInput(
        luong_binh_quan_6_thang=10_000_000,
        tong_thoi_gian_lam_viec=5,
        thoi_gian_dong_bhtn=2,
    ))
    assert result.result == 15_000_000  # 0.5 × 10M × 3

def test_zero_eligible_time():
    result = tinh_tro_cap_thoi_viec(TroCapThoiViecInput(
        luong_binh_quan_6_thang=10_000_000,
        tong_thoi_gian_lam_viec=3,
        thoi_gian_dong_bhtn=3,
    ))
    assert result.result == 0
    assert len(result.warnings) > 0
```

## Sau khi xong

Cập nhật task tương ứng trong `.claude/project/session_state.md` với `[x] [YYYY-MM-DD]`.
