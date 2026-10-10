from decimal import Decimal

import pytest

from adapters.scraping import ScrapingSource


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("R$ 5,7430", Decimal("5.7430")),
        ("5,7430", Decimal("5.7430")),
        ("R$ 5.743,20", Decimal("5743.20")),
        ("5743.20", Decimal("5743.20")),
    ],
)
def test_parse_value_valid_formats(raw, expected):
    assert ScrapingSource._parse_value(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "abc",
        "R$ --",
        "0",
        "-1",
        "NaN",
    ],
)
def test_parse_value_rejects_invalid_values(raw):
    with pytest.raises(ValueError):
        ScrapingSource._parse_value(raw)
