"""Phone number normalization and validation (Iranian mobile numbers)."""
import re
from typing import Optional

# Persian (U+06F0..U+06F9) and Arabic-Indic (U+0660..U+0669) digits -> ASCII.
_DIGIT_TABLE = {
    **{0x06F0 + i: ord("0") + i for i in range(10)},
    **{0x0660 + i: ord("0") + i for i in range(10)},
}

# re.ASCII makes \d match only 0-9, so non-ASCII digits can never slip through.
PHONE_PATTERN = re.compile(r"^09\d{9}$", re.ASCII)


def normalize_phone(text: Optional[str]) -> str:
    """Convert Persian/Arabic digits to ASCII and drop spaces and hyphens."""
    cleaned = (text or "").translate(_DIGIT_TABLE)
    return re.sub(r"[\s\-]", "", cleaned)


def is_valid_phone(phone: str) -> bool:
    """Validate an already normalized phone number."""
    return PHONE_PATTERN.fullmatch(phone) is not None