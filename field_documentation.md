# Documentation for candles.jsonl

Each line contains one day's worth of candlestick data with computed indicators for a particular stock.

## Fields

- `timestamp` (string): ISO 8601 datetime of the candlestick's opening time.
- `open` (float): The opening price of the stock on that day.
- `high` (float): The highest price reached during the day.
- `low` (float): The lowest price reached during the day.
- `close` (float): The closing price of the stock.
- `volume` (float): The total number of shares traded.
- `vw` (float): VWAP indicator value at the candle.
- `n` (int): The number of transactions in which shares were traded during the candle

### Calculated Indicators

- `EMA8` (float): 8-day Exponential Moving Average of close prices (EMA8).
- `EMA21` (float): 21-day Exponential Moving Average of close prices(EMA21).
- `EMA34` (float): 34-day Exponential Moving Average of close prices (EMA34).
- `SMA10` (float): 10-day Simple Moving Average of close prices (SMA10).
- `SMA20` (float): 20-day Simple Moving Average of close prices (SMA20).
- `SMA50` (float): 50-day Simple Moving Average of close prices (SMA50).
- `RSI` (float): 14-day Relative Strength Index (RSI).
- `MACD` (float): MACD line (12-day EMA - 26-day EMA) ( MACD line ).
- `MACD_signal` (float): 9-day EMA of the MACD line ( MACD signal line ).
- `MACD_hist` (float): MACD - MACD_signal.
- `ticker` (string): Stock ticker symbol.


# Documentation for news.jsonl

Each line contains a single news article related to a stock ticker.

## Fields

- `id` (string): Unique article identifier.
- `publisher` (object):
  - `name` (string): Publisher name.
  - `homepage_url` (string): Website URL.
  - `logo_url` (string): URL of the website logo
  - `logo_url` (string) favicon of the website
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
- `insights` (string): The sentiment insights related to the article.
  - `ticker` (string): The ticker corresponding to this insight
  - `sentiment` (string): enum (positive, neutral, negative) The sentiment of the insight
  - `sentiment_reasoning` (string): The reasoning behind the sentiment

# Documentation for financials.jsonl

Each line contains financial reporting data for a company. The currency is all USD.

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

- `revenues` (float): Revenue in the duration
- `cost_of_revenue` (float): Cost of revenue in the duration
- `gross_profit` (float): Gross profit in the duration
- `operating_expenses` (float): Operating expenses in the duration
- `net_income` (float): Net income in the duration
- `eps` (float): Earnings per share in the duration
- `ebitda` (float): EBITDA (  Earnings Before Interest, Taxes, Depreciation, and Amortization ) in the duration

## Balance Sheet

- `cash_and_cash_equivalents` (float): Cash and cash equivalents
- `total_assets` (float): Total assets of the company  
- `total_liabilities` (float): Total liabilities of the company
- `shareholder_equity` (float): Shareholder equity, that is (Total Assets) − ( Total Liabilities )

## Cash Flow Statement

- `operating_cash_flow` (float): Operating cash flow (OCF) represents the cash a company generates from its core business operations.
- `investing_cash_flow` (float): Investing cash flow, found on a company's cash flow statement, tracks the cash impact of a company's investments in long-term assets and securities. It essentially shows how much cash is spent on or generated from investments. This section is crucial for understanding a company's investment strategy and its impact on future growth and profitability
- `financing_cash_flow` (float): Cash flow financing aka Financing cash flow is a form of business financing. Under these terms, a loan made to a company is backed by a company's expected cash flows. Cash flow is the amount of cash that flows in and out of a business in a specific period
- `free_cash_flow` (float): Free cash flow (FCF) is the amount of cash that a company has left after accounting for spending on operations and capital asset maintenance. Investors and analysts rely on it as one measurement of a company's profitability


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
