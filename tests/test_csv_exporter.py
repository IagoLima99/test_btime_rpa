import csv
from datetime import datetime, timezone
from decimal import Decimal

from adapters.csv_exporter import CSVExporter
from domain import Quote


def test_csv_exporter_writes_expected_header_and_quote(tmp_path):
    output = tmp_path / "nested" / "quotes.csv"

    quote = Quote(
        base_currency="USD",
        target_currency="BRL",
        value=Decimal("5.123456"),
        collected_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        source="api",
    )

    CSVExporter().save([quote], str(output))

    with output.open(
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.reader(file))

    assert rows[0] == CSVExporter.HEADER

    assert rows[1] == [
        "USD",
        "BRL",
        "5.1235",
        "2026-01-01T00:00:00+00:00",
        "api",
    ]
