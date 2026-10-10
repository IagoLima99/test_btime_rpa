# btime-rpa

Projeto de coleta da cotação USD/BRL por duas fontes independentes:
web scraping com Selenium e API pública Frankfurter.

As duas execuções geram arquivos CSV com o mesmo cabeçalho.

## Arquitetura

A aplicação usa uma arquitetura Hexagonal simplificada
(Ports & Adapters):

- `domain.py`: entidade `Quote` e contratos `QuoteSource` e
  `QuoteExporter`.
- `service.py`: caso de uso `CollectQuote`, que coordena coleta
  e exportação.
- `adapters/api.py`: integração HTTP com a Frankfurter.
- `adapters/scraping.py`: extração via Selenium.
- `adapters/csv_exporter.py`: persistência em CSV.
- `main_api.py` e `main_scraper.py`: pontos de entrada e composição
  das dependências.
- `tests/`: testes unitários de parsing, API, serviço e exportação.

## Requisitos

- Python 3.10 ou superior.
- Google Chrome instalado para executar o scraping.
- A API Frankfurter não exige chave de autenticação.

## Instalação

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env