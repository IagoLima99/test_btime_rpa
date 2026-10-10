"""Ponto de entrada para coleta via Selenium."""

import logging
import os
import sys

from dotenv import load_dotenv

from adapters.csv_exporter import CSVExporter
from adapters.scraping import ScrapingSource
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
        headless_value = (
            os.getenv(
                "SCRAPING_HEADLESS",
                "true",
            )
            .strip()
            .lower()
        )

        if headless_value not in {
            "true",
            "false",
            "1",
            "0",
            "yes",
            "no",
        }:
            raise ValueError("SCRAPING_HEADLESS deve ser true/false, 1/0 ou yes/no.")

        headless = headless_value in {
            "true",
            "1",
            "yes",
        }

        source = ScrapingSource(
            url=os.getenv(
                "SCRAPING_URL",
                "https://www.melhorcambio.com/dolar-hoje",
            ),
            headless=headless,
            timeout=float(os.getenv("SCRAPING_TIMEOUT", "15")),
        )

        csv_path = os.getenv(
            "SCRAPING_CSV_PATH",
            "cotacao_scraping.csv",
        )

        service = CollectQuote(
            source=source,
            exporter=CSVExporter(),
        )

        quote = service.execute(csv_path)

        logger.info(
            "Coleta via scraping concluída: %s/%s = %s; arquivo: %s",
            quote.base_currency,
            quote.target_currency,
            quote.value,
            csv_path,
        )

        return 0

    except Exception:
        logger.exception("Falha na coleta via scraping.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
