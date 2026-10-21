import pytest

from phone import is_valid_phone, normalize_phone


def _persian(digits: str) -> str:
    return "".join(chr(0x06F0 + int(d)) for d in digits)


def _arabic(digits: str) -> str:
    return "".join(chr(0x0660 + int(d)) for d in digits)


NUMBER = "09123456789"


@pytest.mark.parametrize(
    "raw",
    [
        NUMBER,
        _persian(NUMBER),
        _arabic(NUMBER),
        _persian("09") + "12345" + _persian("6789"),  # mixed digit scripts
        " 0912 345-6789 ",
    ],
)
def test_normalize_returns_ascii_number(raw):
    assert normalize_phone(raw) == NUMBER


def test_normalize_handles_none():
    assert normalize_phone(None) == ""


@pytest.mark.parametrize("raw", [NUMBER, _persian(NUMBER), _arabic(NUMBER)])
def test_normalized_valid_numbers_pass(raw):
    assert is_valid_phone(normalize_phone(raw))


@pytest.mark.parametrize(
    "phone",
    ["", "9123456789", "0912345678", "091234567890", "08123456789", "0912345678a"],
)
def test_invalid_numbers_fail(phone):
    assert not is_valid_phone(phone)


def test_non_ascii_digits_are_rejected_without_normalization():
    # Guards against the old behaviour where "09" + Persian digits matched \d.
    assert not is_valid_phone(_persian(NUMBER))
    assert not is_valid_phone("09" + _persian("123456789"))