from datetime import datetime, timezone
from decimal import Decimal

import pytest

from domain import Quote
from service import CollectQuote


def test_quote_rejects_non_positive_value():
    with pytest.raises(ValueError):
        Quote(
            "USD",
            "BRL",
            Decimal(0),
            datetime.now(timezone.utc),
            "api",
        )


def test_service_collects_and_exports():
    expected = Quote(
        "USD",
        "BRL",
        Decimal("5.1"),
        datetime.now(timezone.utc),
        "fake",
    )

    class FakeSource:
        def fetch(self):
            return expected

    class FakeExporter:
        def __init__(self):
            self.saved = None

        def save(self, quotes, path):
            self.saved = (quotes, path)

    exporter = FakeExporter()

    result = CollectQuote(
        FakeSource(),
        exporter,
    ).execute("out.csv")

    assert result == expected
    assert exporter.saved == ([expected], "out.csv")
