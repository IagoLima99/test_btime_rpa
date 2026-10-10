"""Exportação de cotações para CSV."""

import csv
from pathlib import Path

from domain import Quote


class CSVExporter:
    """Escreve cotações em CSV com cabeçalho estável."""

    HEADER = [
        "moeda_origem",
        "moeda_destino",
        "valor",
        "data_coleta",
        "fonte",
    ]

    def save(
        self,
        quotes: list[Quote],
        path: str,
    ) -> None:
        """Sobrescreve o arquivo informado e grava as cotações."""
        output_path = Path(path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(self.HEADER)

            for quote in quotes:
                writer.writerow(
                    [
                        quote.base_currency,
                        quote.target_currency,
                        f"{quote.value:.4f}",
                        quote.collected_at.isoformat(),
                        quote.source,
                    ]
                )
