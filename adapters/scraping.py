"""Adaptador Selenium para a página de cotação do Melhor Câmbio."""

import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from selenium import webdriver
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from domain import Quote


class ScrapingSource:
    """Extrai a cotação comercial da página configurada."""

    def __init__(
        self,
        url: str = "https://www.melhorcambio.com/dolar-hoje",
        headless: bool = True,
        timeout: float = 15,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout deve ser maior que zero.")

        self._url = url
        self._headless = headless
        self._timeout = timeout

    def fetch(self) -> Quote:
        """Abre o navegador, extrai a cotação e fecha o navegador."""
        driver = self._open_browser()

        try:
            value = self._extract_value(driver)
        finally:
            driver.quit()

        return Quote(
            base_currency="USD",
            target_currency="BRL",
            value=value,
            collected_at=datetime.now(timezone.utc),
            source="scraping",
        )

    def _open_browser(self) -> webdriver.Chrome:
        """Cria o navegador e configura os timeouts."""
        options = Options()

        if self._headless:
            options.add_argument("--headless=new")

        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(self._timeout)
            return driver

        except WebDriverException as exc:
            raise RuntimeError(
                "Não foi possível iniciar o Chrome/ChromeDriver. "
                "Verifique se o Chrome está instalado e se o Selenium "
                "Manager consegue obter um driver compatível."
            ) from exc

    def _extract_value(
        self,
        driver: webdriver.Chrome,
    ) -> Decimal:
        """Carrega a página, espera pelo campo e interpreta o valor."""
        try:
            driver.get(self._url)

            element = WebDriverWait(
                driver,
                self._timeout,
            ).until(EC.presence_of_element_located((By.ID, "comercial")))

        except TimeoutException as exc:
            raise RuntimeError(
                "O campo de cotação 'comercial' não apareceu dentro "
                "do tempo limite. A página pode ter mudado, estar "
                "indisponível ou ter bloqueado a solicitação."
            ) from exc

        except WebDriverException as exc:
            raise RuntimeError(
                "Falha ao carregar a página de cotação. Verifique a conexão e a URL."
            ) from exc

        raw_value = element.get_attribute("value")

        if not raw_value:
            raw_value = element.text

        return self._parse_value(raw_value or "")

    @staticmethod
    def _parse_value(text: str) -> Decimal:
        """Converte valores como 'R$ 5.743,20' para Decimal."""
        cleaned = (
            text.replace("R$", "")
            .replace("\u00a0", "")
            .replace("\u202f", "")
            .replace(" ", "")
            .strip()
        )

        if not cleaned:
            raise ValueError("O site retornou um valor de cotação vazio.")

        # Formato brasileiro: ponto para milhar e vírgula decimal.
        if "," in cleaned:
            cleaned = cleaned.replace(".", "")
            cleaned = cleaned.replace(",", ".")

        # Aceita número inteiro ou decimal com ponto.
        if not re.fullmatch(
            r"[+-]?\d+(?:\.\d+)?",
            cleaned,
        ):
            raise ValueError(
                f"Formato de cotação inesperado retornado pelo site: {text!r}"
            )

        try:
            value = Decimal(cleaned)

        except InvalidOperation as exc:
            raise ValueError(
                f"Não foi possível converter a cotação {text!r} para Decimal."
            ) from exc

        if not value.is_finite() or value <= 0:
            raise ValueError("O site retornou uma cotação não finita ou não positiva.")

        return value
