from decimal import Decimal
from unittest.mock import Mock

import pytest
import requests

from adapters.api import APISource, _is_retryable_error


def test_api_source_parses_valid_response(monkeypatch):
    response = Mock()
    response.json.return_value = {
        "base": "USD",
        "rates": {"BRL": 5.1234},
    }
    response.raise_for_status.return_value = None

    monkeypatch.setattr(
        requests,
        "get",
        Mock(return_value=response),
    )

    source = APISource(retry_wait_seconds=0)
    quote = source.fetch()

    assert quote.value == Decimal("5.1234")
    assert quote.base_currency == "USD"
    assert quote.target_currency == "BRL"
    assert quote.source == "api"


def test_api_source_rejects_missing_currency(monkeypatch):
    response = Mock()
    response.json.return_value = {
        "rates": {"EUR": 0.9},
    }
    response.raise_for_status.return_value = None

    monkeypatch.setattr(
        requests,
        "get",
        Mock(return_value=response),
    )

    with pytest.raises(ValueError, match="não encontrada"):
        APISource(retry_wait_seconds=0).fetch()


def test_api_source_rejects_invalid_json_shape(monkeypatch):
    response = Mock()
    response.json.return_value = []
    response.raise_for_status.return_value = None

    monkeypatch.setattr(
        requests,
        "get",
        Mock(return_value=response),
    )

    with pytest.raises(ValueError, match="objeto JSON"):
        APISource(retry_wait_seconds=0).fetch()


def test_retry_predicate_only_retries_transient_errors():
    assert _is_retryable_error(requests.Timeout())
    assert _is_retryable_error(requests.ConnectionError())

    client_error_response = Mock(status_code=400)
    server_error_response = Mock(status_code=503)

    client_error = requests.HTTPError(response=client_error_response)
    server_error = requests.HTTPError(response=server_error_response)

    assert not _is_retryable_error(client_error)
    assert _is_retryable_error(server_error)

    assert not _is_retryable_error(ValueError("invalid response"))
