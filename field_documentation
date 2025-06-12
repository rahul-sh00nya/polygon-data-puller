# Documentation for candles.jsonl

Each line in `candles.jsonl` contains one day's worth of candlestick data with computed indicators for a particular stock.

## Fields

- `timestamp` (string): ISO 8601 datetime of the candlestick's opening time.
- `open` (float): The opening price of the stock on that day.
- `high` (float): The highest price reached during the day.
- `low` (float): The lowest price reached during the day.
- `close` (float): The closing price of the stock.
- `volume` (float): The total number of shares traded.

### Calculated Indicators

- `EMA8` (float): 8-day Exponential Moving Average of close prices.
- `EMA21` (float): 21-day EMA.
- `EMA34` (float): 34-day EMA.
- `SMA10` (float): 10-day Simple Moving Average.
- `SMA20` (float): 20-day SMA.
- `SMA50` (float): 50-day SMA.
- `RSI` (float): 14-day Relative Strength Index.
- `MACD` (float): MACD line (12-day EMA - 26-day EMA).
- `MACD_signal` (float): 9-day EMA of the MACD line.
- `MACD_hist` (float): MACD - MACD_signal.
- `ticker` (string): Stock ticker symbol.


# Documentation for news.jsonl

Each line contains a single news article related to a stock ticker.

## Fields

- `id` (string): Unique article identifier.
- `publisher` (object):
  - `name` (string): Publisher name.
  - `homepage_url` (string): Website URL.
- `title` (string): Article headline.
- `author` (string): Author name.
- `published_utc` (string): UTC publication time (ISO 8601).
- `article_url` (string): Full article link.
- `tickers` (list[string]): Related stock tickers.
- `amp_url` (string, optional): AMP version link.
- `image_url` (string, optional): Preview image URL.
- `description` (string): Summary or excerpt.
- `keywords` (list[string], optional): Tags for classification.
- `source` (string, optional): Alternate source name.


# Documentation for financials.jsonl

Each line contains financial reporting data for a company.

## Top-Level Fields

- `ticker` (string): Stock ticker.
- `fiscal_period` (string): Fiscal period (e.g., Q1, FY).
- `fiscal_year` (int): Fiscal year.
- `fiscal_quarter` (int, optional): Fiscal quarter (1–4).
- `start_date` (string): Period start (ISO).
- `end_date` (string): Period end (ISO).
- `filed_date` (string): Filing date (ISO).
- `source_filing_url` (string): SEC filing link.

## Income Statement

- `revenues` (float)
- `cost_of_revenue` (float)
- `gross_profit` (float)
- `operating_expenses` (float)
- `net_income` (float)
- `eps` (float)
- `ebitda` (float)

## Balance Sheet

- `cash_and_cash_equivalents` (float)
- `total_assets` (float)
- `total_liabilities` (float)
- `shareholder_equity` (float)

## Cash Flow Statement

- `operating_cash_flow` (float)
- `investing_cash_flow` (float)
- `financing_cash_flow` (float)
- `free_cash_flow` (float)


# Documentation for yields.jsonl

Each line contains daily U.S. Treasury yield curve data.

## Fields

- `date` (string): ISO 8601 date.
- `1m` (float): 1-month Treasury yield.
- `2m` (float): 2-month yield.
- `3m` (float): 3-month yield.
- `4m` (float): 4-month yield.
- `6m` (float): 6-month yield.
- `1y` (float): 1-year yield.
- `2y` (float): 2-year yield.
- `3y` (float): 3-year yield.
- `5y` (float): 5-year yield.
- `7y` (float): 7-year yield.
- `10y` (float): 10-year yield.
- `20y` (float): 20-year yield.
- `30y` (float): 30-year yield.


# Documentation for ticker_details.jsonl

Each line describes metadata about a single stock ticker.

## Fields

- `ticker` (string)
- `name` (string)
- `market` (string)
- `locale` (string)
- `primary_exchange` (string)
- `type` (string)
- `active` (bool)
- `currency_name` (string)
- `cik` (string)
- `composite_figi` (string)
- `share_class_figi` (string)
- `last_updated_utc` (string)

## Optional Fields

- `description` (string)
- `homepage_url` (string)
- `total_employees` (int)
- `list_date` (string)
- `market_cap` (float)
- `weighted_shares_outstanding` (float)
