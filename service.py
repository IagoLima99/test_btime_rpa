"""Casos de uso da aplicação."""

from domain import Quote, QuoteExporter, QuoteSource


class CollectQuote:
    """Orquestra coleta e exportação sem depender de adaptadores concretos."""

    def __init__(
        self,
        source: QuoteSource,
        exporter: QuoteExporter,
    ) -> None:
        self._source = source
        self._exporter = exporter

    def execute(self, csv_path: str) -> Quote:
        """Executa o fluxo fetch -> save e retorna a cotação coletada."""
        quote = self._source.fetch()
        self._exporter.save([quote], csv_path)

        return quote
