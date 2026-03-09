# polygon-data-puller

Async Python CLI tool that fetches financial market data from the [Massive.com](https://massive.com) REST API and writes it to CSV files with companion PostgreSQL SQL files.

## Features

- Fetches candles (OHLCV), news, SEC filings (10-K, 8-K), risk factors, short interest/volume, float, and treasury yields
- Computes technical indicators: EMA (8/21/34), SMA (10/20/50), RSI (14), MACD (12/26/9)
- Outputs 14 CSV files + 14 PostgreSQL SQL files (`CREATE TABLE` + `\COPY`)
- Sliding-window rate limiter (5 API calls / 60 seconds)

## Requirements

Python 3.10+ with a virtualenv:

```bash
pip install aiohttp pandas
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

| CSV File | SQL File | PostgreSQL Table |
|----------|----------|-----------------|
| `candles.csv` | `candles.sql` | `candles` |
| `news.csv` | `news.sql` | `news` |
| `news_insights.csv` | `news_insights.sql` | `news_insights` |
| `news_tickers.csv` | `news_tickers.sql` | `news_tickers` |
| `news_keywords.csv` | `news_keywords.sql` | `news_keywords` |
| `treasury_yields.csv` | `treasury_yields.sql` | `treasury_yields` |
| `ten_k_sections.csv` | `ten_k_sections.sql` | `ten_k_sections` |
| `eight_k_text.csv` | `eight_k_text.sql` | `eight_k_text` |
| `risk_factors.csv` | `risk_factors.sql` | `risk_factors` |
| `risk_factors_taxonomy.csv` | `risk_factors_taxonomy.sql` | `risk_factors_taxonomy` |
| `filings_index.csv` | `filings_index.sql` | `filings_index` |
| `short_interest.csv` | `short_interest.sql` | `short_interest` |
| `short_volume.csv` | `short_volume.sql` | `short_volume` |
| `float.csv` | `float.sql` | `float` |

## Loading into PostgreSQL

The `load_db.sh` script automates database setup: it creates the database if it doesn't exist, drops all existing tables, and loads every `.sql` file in the project directory.

```bash
# With defaults (localhost:5432, user=test, db=stock_data)
./load_db.sh

# Custom connection
./load_db.sh -h myhost -p 5432 -U myuser -d stock_data -W
```

| Flag | Default | Description |
|------|---------|-------------|
| `-h` | `localhost` | PostgreSQL host |
| `-p` | `5432` | PostgreSQL port |
| `-U` | `test` | PostgreSQL user |
| `-d` | `stock_data` | Database name |
| `-W` | off | Prompt for password |

## API Endpoints

All requests go to `https://api.massive.com`:

| Data | Endpoint |
|------|----------|
| Candles | `GET /v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}` |
| News | `GET /v2/reference/news` |
| 10-K Sections | `GET /stocks/filings/10-K/vX/sections` |
| 8-K Text | `GET /stocks/filings/8-K/vX/text` |
| Risk Factors | `GET /stocks/filings/vX/risk-factors` |
| Risk Factors Taxonomy | `GET /stocks/taxonomies/vX/risk-factors` |
| Filings Index | `GET /stocks/filings/vX/index` |
| Short Interest | `GET /stocks/v1/short-interest` |
| Short Volume | `GET /stocks/v1/short-volume` |
| Float | `GET /stocks/vX/float` |
| Treasury Yields | `GET /fed/v1/treasury-yields` |
