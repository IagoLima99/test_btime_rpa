"""Entidades e contratos centrais da aplicação, sem dependências de infraestrutura."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class Quote:
    """Representa uma cotação coletada."""

    base_currency: str
    target_currency: str
    value: Decimal
    collected_at: datetime
    source: str

    def __post_init__(self) -> None:
        if not self.base_currency or not self.target_currency:
            raise ValueError("As moedas de origem e destino são obrigatórias.")

        if not self.value.is_finite() or self.value <= 0:
            raise ValueError(
                "O valor da cotação deve ser um decimal finito e positivo."
            )

        if not self.source:
            raise ValueError("A fonte da cotação é obrigatória.")


class QuoteSource(Protocol):
    """Porta de entrada para qualquer fonte de cotação."""

    def fetch(self) -> Quote:
        """Coleta e retorna uma cotação."""
        ...


class QuoteExporter(Protocol):
    """Porta de saída para persistência de cotações."""

    def save(self, quotes: list[Quote], path: str) -> None:
        """Persiste as cotações no caminho informado."""
        ...
