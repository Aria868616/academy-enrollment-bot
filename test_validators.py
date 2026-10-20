import re
import pytest

# تابع اعتبارسنجی شماره تلفن (مشابه منطق پروژه شما)
def validate_phone(phone: str) -> bool:
    pattern = r"^09\d{9}$"
    return bool(re.match(pattern, phone))

@pytest.mark.parametrize("phone, expected", [
    ("09123456789", True),
    ("09901234567", True),
    ("0912345678", False),   # شماره کوتاه
    ("091234567890", False),  # شماره بلند
    ("0912-345-6789", False), # دارای کاراکتر اضافی
    ("12345678901", False),   # عدم شروع با 09
])
def test_phone_validation(phone, expected):
    assert validate_phone(phone) == expected