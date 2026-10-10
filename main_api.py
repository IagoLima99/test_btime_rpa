"""Ponto de entrada para coleta via API Frankfurter."""

import logging
import os
import sys

from dotenv import load_dotenv

from adapters.api import APISource
from adapters.csv_exporter import CSVExporter
from service import CollectQuote

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> int:
    """Carrega configuração, monta dependências e executa a coleta."""
    load_dotenv()

    try:
        source = APISource(
            base_url=os.getenv(
                "API_BASE_URL",
                "https://api.frankfurter.dev/v1/latest",
            ),
            base_currency=os.getenv(
                "API_BASE_CURRENCY",
                "USD",
            )
            .strip()
            .upper(),
            target_currency=os.getenv(
                "API_TARGET_CURRENCY",
                "BRL",
            )
            .strip()
            .upper(),
            timeout=float(os.getenv("API_TIMEOUT", "10")),
            retry_attempts=int(os.getenv("API_RETRY_ATTEMPTS", "3")),
            retry_wait_seconds=float(os.getenv("API_RETRY_WAIT_SECONDS", "2")),
        )

        csv_path = os.getenv(
            "API_CSV_PATH",
            "cotacao_api.csv",
        )

        service = CollectQuote(
            source=source,
            exporter=CSVExporter(),
        )

        quote = service.execute(csv_path)

        logger.info(
            "Coleta via API concluída: %s/%s = %s; arquivo: %s",
            quote.base_currency,
            quote.target_currency,
            quote.value,
            csv_path,
        )

        return 0

    except Exception:
        logger.exception("Falha na coleta via API.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
