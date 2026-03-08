# polygon-data-puller

Async Python CLI tool that fetches financial market data from the [Massive.com](https://massive.com) REST API and writes it to CSV files with companion ClickHouse SQL files.

## Features

- Fetches candles (OHLCV), news, balance sheets, income statements, cash flow statements, and treasury yields
- Computes technical indicators: EMA (8/21/34), SMA (10/20/50), RSI (14), MACD (12/26/9)
- Outputs 6 CSV files + 6 ClickHouse SQL files (`CREATE TABLE` + `INSERT FROM INFILE`)
- Sliding-window rate limiter (5 API calls / 60 seconds)
- Progress bars via `tqdm` and verbose per-request logging

## Requirements

Python 3.10+ with a virtualenv:

```bash
pip install aiohttp pandas tqdm
```

## Usage

```bash
python3 data_puller.py --api_key <YOUR_MASSIVE_API_KEY> --start_date 2024-01-01 --stocks AAPL TSLA NVDA
```

### Arguments

| Flag | Required | Description |
|------|----------|-------------|
| `--api_key` | Yes | Massive.com API key |
| `--start_date` | Yes | Start date in `YYYY-MM-DD` format |
| `--stocks` | Yes | One or more stock tickers (space-separated) |

### Bulk run with S&P 500

```bash
python3 data_puller.py --api_key <KEY> --start_date 2024-01-01 --stocks $(cat snp500.txt)
```

## Output

| CSV File | SQL File | ClickHouse Table |
|----------|----------|-----------------|
| `candles.csv` | `candles.sql` | `stock_data.candles` |
| `news.csv` | `news.sql` | `stock_data.news` |
| `balance_sheets.csv` | `balance_sheets.sql` | `stock_data.balance_sheets` |
| `income_statements.csv` | `income_statements.sql` | `stock_data.income_statements` |
| `cash_flow_statements.csv` | `cash_flow_statements.sql` | `stock_data.cash_flow_statements` |
| `treasury_yields.csv` | `treasury_yields.sql` | `stock_data.treasury_yields` |

### Loading into ClickHouse

```bash
clickhouse-client --multiquery < candles.sql
```

## API Endpoints

All requests go to `https://api.massive.com`:

| Data | Endpoint |
|------|----------|
| Candles | `GET /v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}` |
| News | `GET /v2/reference/news` |
| Balance Sheets | `GET /stocks/financials/v1/balance-sheets` |
| Income Statements | `GET /stocks/financials/v1/income-statements` |
| Cash Flow Statements | `GET /stocks/financials/v1/cash-flow-statements` |
| Treasury Yields | `GET /fed/v1/treasury-yields` |
