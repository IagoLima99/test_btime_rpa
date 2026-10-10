"""Adaptador HTTP para a API pública Frankfurter."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

import requests
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_fixed,
)

from domain import Quote


def _is_retryable_error(error: BaseException) -> bool:
    """Identifica falhas transitórias que justificam uma nova tentativa."""
    if isinstance(
        error,
        (requests.Timeout, requests.ConnectionError),
    ):
        return True

    if isinstance(error, requests.HTTPError):
        response = error.response

        return response is not None and (
            response.status_code == 429 or response.status_code >= 500
        )

    return False


class APISource:
    """Consulta a Frankfurter e converte a resposta para Quote."""

    def __init__(
        self,
        base_url: str = "https://api.frankfurter.dev/v1/latest",
        base_currency: str = "USD",
        target_currency: str = "BRL",
        timeout: float = 10,
        retry_attempts: int = 3,
        retry_wait_seconds: float = 2,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout deve ser maior que zero.")

        if retry_attempts < 1:
            raise ValueError("retry_attempts deve ser pelo menos 1.")

        if retry_wait_seconds < 0:
            raise ValueError("retry_wait_seconds não pode ser negativo.")

        self._base_url = base_url
        self._base_currency = base_currency.strip().upper()
        self._target_currency = target_currency.strip().upper()
        self._timeout = timeout
        self._retry_attempts = retry_attempts
        self._retry_wait_seconds = retry_wait_seconds

    def fetch(self) -> Quote:
        """Consulta a API e retorna a cotação."""
        rate = self._fetch_rate()

        return Quote(
            base_currency=self._base_currency,
            target_currency=self._target_currency,
            value=rate,
            collected_at=datetime.now(timezone.utc),
            source="api",
        )

    def _fetch_rate(self) -> Decimal:
        """Faz a requisição com retry limitado a erros transitórios."""

        @retry(
            retry=retry_if_exception(_is_retryable_error),
            stop=stop_after_attempt(self._retry_attempts),
            wait=wait_fixed(self._retry_wait_seconds),
            reraise=True,
        )
        def request_rate() -> Decimal:
            response = requests.get(
                self._base_url,
                params={
                    "base": self._base_currency,
                    "symbols": self._target_currency,
                },
                timeout=self._timeout,
            )

            response.raise_for_status()
            data: Any = response.json()

            if not isinstance(data, dict):
                raise ValueError(
                    "Resposta da API inválida: era esperado um objeto JSON."
                )

            rates = data.get("rates")

            if not isinstance(rates, dict):
                raise ValueError(
                    "Resposta da API inválida: campo 'rates' ausente ou inválido."
                )

            if self._target_currency not in rates:
                raise ValueError(
                    f"Moeda de destino '{self._target_currency}' "
                    "não encontrada na resposta."
                )

            try:
                value = Decimal(str(rates[self._target_currency]))
            except (
                InvalidOperation,
                TypeError,
                ValueError,
            ) as exc:
                raise ValueError("A API retornou uma cotação não numérica.") from exc

            if not value.is_finite() or value <= 0:
                raise ValueError(
                    "A API retornou uma cotação não finita ou não positiva."
                )

            return value

        return request_rate()
