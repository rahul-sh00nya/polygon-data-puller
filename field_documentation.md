# Field Documentation

This document describes the schema for each CSV output file produced by `data_puller.py`.

---

# candles.csv

Each row contains one day's candlestick data with computed technical indicators for a stock.

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `ticker` | TEXT | Stock ticker symbol |
| `timestamp` | TIMESTAMP | Date/time of the candle opening |
| `open` | DOUBLE PRECISION | Opening price |
| `high` | DOUBLE PRECISION | Highest price during the day |
| `low` | DOUBLE PRECISION | Lowest price during the day |
| `close` | DOUBLE PRECISION | Closing price |
| `volume` | DOUBLE PRECISION | Total shares traded |
| `vw` | DOUBLE PRECISION | Volume-weighted average price (VWAP) |
| `n` | BIGINT | Number of transactions |

### Calculated Indicators

| Column | Type | Description |
|--------|------|-------------|
| `EMA8` | DOUBLE PRECISION | 8-day Exponential Moving Average of close |
| `EMA21` | DOUBLE PRECISION | 21-day Exponential Moving Average of close |
| `EMA34` | DOUBLE PRECISION | 34-day Exponential Moving Average of close |
| `SMA10` | DOUBLE PRECISION | 10-day Simple Moving Average of close |
| `SMA20` | DOUBLE PRECISION | 20-day Simple Moving Average of close |
| `SMA50` | DOUBLE PRECISION | 50-day Simple Moving Average of close |
| `RSI` | DOUBLE PRECISION | 14-period Relative Strength Index |
| `MACD` | DOUBLE PRECISION | MACD line (12-day EMA minus 26-day EMA) |
| `MACD_signal` | DOUBLE PRECISION | 9-day EMA of the MACD line |
| `MACD_hist` | DOUBLE PRECISION | MACD minus MACD_signal |

Rows with NaN values (from rolling window warm-up) are dropped.

---

# news.csv

Each row contains a single news article related to a stock ticker. Nested objects are flattened. Related tickers, keywords, and insights are stored in separate relational tables (see below).

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Unique article identifier (FK for news_insights, news_tickers, news_keywords) |
| `title` | TEXT | Article headline |
| `author` | TEXT | Author name |
| `published_utc` | TIMESTAMP | UTC publication timestamp (ISO 8601) |
| `article_url` | TEXT | Full article link |
| `image_url` | TEXT | Preview image URL (may be empty) |
| `description` | TEXT | Summary or excerpt |
| `publisher_name` | TEXT | Publisher name (flattened from `publisher.name`) |
| `publisher_homepage_url` | TEXT | Publisher website (flattened from `publisher.homepage_url`) |
| `publisher_logo_url` | TEXT | Publisher logo URL (flattened from `publisher.logo_url`) |
| `publisher_favicon_url` | TEXT | Publisher favicon URL (flattened from `publisher.favicon_url`) |

---

# news_insights.csv

Each row contains one sentiment insight for a news article. Flattened from the `insights` JSON array in the API response.

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `news_id` | TEXT | References `news.id` |
| `ticker` | TEXT | The ticker this insight relates to |
| `sentiment` | TEXT | One of: `positive`, `neutral`, `negative` |
| `sentiment_reasoning` | TEXT | Explanation of the sentiment classification |

---

# news_tickers.csv

Junction table linking news articles to stock tickers. Flattened from the `tickers` array in the API response.

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `news_id` | TEXT | References `news.id` |
| `ticker` | TEXT | Stock ticker symbol |

---

# news_keywords.csv

Each row contains one keyword tag for a news article. Flattened from the `keywords` array in the API response.

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `news_id` | TEXT | References `news.id` |
| `keyword` | TEXT | Keyword tag |

---

# balance_sheets.csv

Each row contains one quarterly or annual balance sheet filing for a company. All financial metric columns are flat numeric values.

## Metadata Fields

| Column | Type | Description |
|--------|------|-------------|
| `cik` | TEXT | SEC Central Index Key |
| `tickers` | TEXT | Comma-separated ticker(s) for the company |
| `filing_date` | DATE | Date the filing was submitted |
| `fiscal_year` | INTEGER | Fiscal year of the report |
| `fiscal_quarter` | INTEGER | Fiscal quarter (1-4), null for annual filings |
| `period_end` | DATE | End date of the reporting period |
| `timeframe` | TEXT | Reporting timeframe (e.g. `quarterly`, `annual`, `ttm`) |

## Financial Fields

| Column | Type | Description |
|--------|------|-------------|
| `accounts_payable` | DOUBLE PRECISION | Amounts owed to suppliers |
| `accrued_and_other_current_liabilities` | DOUBLE PRECISION | Accrued expenses and other short-term obligations |
| `accumulated_other_comprehensive_income` | DOUBLE PRECISION | Cumulative unrealized gains/losses outside net income |
| `additional_paid_in_capital` | DOUBLE PRECISION | Capital received above par value from share issuance |
| `cash_and_equivalents` | DOUBLE PRECISION | Cash and short-term liquid investments |
| `commitments_and_contingencies` | DOUBLE PRECISION | Potential obligations from commitments and contingencies |
| `common_stock` | DOUBLE PRECISION | Par value of issued common shares |
| `debt_current` | DOUBLE PRECISION | Debt obligations due within one year |
| `deferred_revenue_current` | DOUBLE PRECISION | Revenue received but not yet earned (short-term) |
| `goodwill` | DOUBLE PRECISION | Excess purchase price over net assets in acquisitions |
| `intangible_assets_net` | DOUBLE PRECISION | Non-physical assets net of amortization |
| `inventories` | DOUBLE PRECISION | Raw materials, work-in-progress, and finished goods |
| `long_term_debt_and_capital_lease_obligations` | DOUBLE PRECISION | Debt and lease obligations due beyond one year |
| `noncontrolling_interest` | DOUBLE PRECISION | Equity in subsidiaries not owned by the parent |
| `other_assets` | DOUBLE PRECISION | Assets not classified elsewhere |
| `other_current_assets` | DOUBLE PRECISION | Short-term assets not classified elsewhere |
| `other_equity` | DOUBLE PRECISION | Equity items not classified elsewhere |
| `other_noncurrent_liabilities` | DOUBLE PRECISION | Long-term liabilities not classified elsewhere |
| `preferred_stock` | DOUBLE PRECISION | Par value of issued preferred shares |
| `property_plant_equipment_net` | DOUBLE PRECISION | Tangible fixed assets net of depreciation |
| `receivables` | DOUBLE PRECISION | Amounts owed by customers |
| `retained_earnings_deficit` | DOUBLE PRECISION | Cumulative net income less dividends |
| `short_term_investments` | DOUBLE PRECISION | Investments maturing within one year |
| `total_assets` | DOUBLE PRECISION | Sum of all assets |
| `total_current_assets` | DOUBLE PRECISION | Sum of all short-term assets |
| `total_current_liabilities` | DOUBLE PRECISION | Sum of all short-term liabilities |
| `total_equity` | DOUBLE PRECISION | Total shareholders' equity including noncontrolling interest |
| `total_equity_attributable_to_parent` | DOUBLE PRECISION | Equity attributable to the parent company |
| `total_liabilities` | DOUBLE PRECISION | Sum of all liabilities |
| `total_liabilities_and_equity` | DOUBLE PRECISION | Total liabilities plus total equity |
| `treasury_stock` | DOUBLE PRECISION | Cost of repurchased shares |

Not all fields are present for every company. Missing values are written as empty strings in the CSV.

---

# income_statements.csv

Each row contains one quarterly or annual income statement filing for a company.

## Metadata Fields

Same as [balance_sheets.csv](#metadata-fields).

## Financial Fields

| Column | Type | Description |
|--------|------|-------------|
| `basic_earnings_per_share` | DOUBLE PRECISION | Net income per basic share |
| `basic_shares_outstanding` | DOUBLE PRECISION | Weighted average basic shares outstanding |
| `consolidated_net_income_loss` | DOUBLE PRECISION | Net income/loss including noncontrolling interests |
| `cost_of_revenue` | DOUBLE PRECISION | Direct costs of goods/services sold |
| `depreciation_depletion_amortization` | DOUBLE PRECISION | Non-cash charges for asset value reduction |
| `diluted_earnings_per_share` | DOUBLE PRECISION | Net income per diluted share |
| `diluted_shares_outstanding` | DOUBLE PRECISION | Weighted average diluted shares outstanding |
| `discontinued_operations` | DOUBLE PRECISION | Income/loss from discontinued business segments |
| `ebitda` | DOUBLE PRECISION | Earnings before interest, taxes, depreciation, and amortization |
| `equity_in_affiliates` | DOUBLE PRECISION | Share of earnings from equity-method investments |
| `extraordinary_items` | DOUBLE PRECISION | Gains/losses from unusual non-recurring events |
| `gross_profit` | DOUBLE PRECISION | Revenue minus cost of revenue |
| `income_before_income_taxes` | DOUBLE PRECISION | Pre-tax income |
| `income_taxes` | DOUBLE PRECISION | Income tax expense |
| `interest_expense` | DOUBLE PRECISION | Cost of borrowed funds |
| `interest_income` | DOUBLE PRECISION | Income earned on investments and deposits |
| `net_income_loss_attributable_common_shareholders` | DOUBLE PRECISION | Net income available to common shareholders |
| `noncontrolling_interest` | DOUBLE PRECISION | Net income attributable to noncontrolling interests |
| `operating_income` | DOUBLE PRECISION | Profit from core business operations |
| `other_income_expense` | DOUBLE PRECISION | Non-operating income and expenses |
| `other_operating_expenses` | DOUBLE PRECISION | Operating expenses not classified elsewhere |
| `preferred_stock_dividends_declared` | DOUBLE PRECISION | Dividends declared on preferred shares |
| `research_development` | DOUBLE PRECISION | Research and development expenditure |
| `revenue` | DOUBLE PRECISION | Total revenue / net sales |
| `selling_general_administrative` | DOUBLE PRECISION | SG&A expenses |
| `total_operating_expenses` | DOUBLE PRECISION | Sum of all operating expenses |
| `total_other_income_expense` | DOUBLE PRECISION | Sum of all non-operating income and expenses |

Not all fields are present for every company. Missing values are written as empty strings in the CSV.

---

# cash_flow_statements.csv

Each row contains one quarterly or annual cash flow statement filing for a company.

## Metadata Fields

Same as [balance_sheets.csv](#metadata-fields).

## Financial Fields

| Column | Type | Description |
|--------|------|-------------|
| `cash_from_operating_activities_continuing_operations` | DOUBLE PRECISION | Cash from operating activities of continuing operations |
| `change_in_cash_and_equivalents` | DOUBLE PRECISION | Net change in cash and equivalents |
| `change_in_other_operating_assets_and_liabilities_net` | DOUBLE PRECISION | Net change in other operating assets and liabilities |
| `depreciation_depletion_and_amortization` | DOUBLE PRECISION | Non-cash depreciation, depletion, and amortization |
| `dividends` | DOUBLE PRECISION | Cash dividends paid |
| `effect_of_currency_exchange_rate` | DOUBLE PRECISION | Impact of exchange rate changes on cash |
| `income_loss_from_discontinued_operations` | DOUBLE PRECISION | Cash impact from discontinued operations |
| `long_term_debt_issuances_repayments` | DOUBLE PRECISION | Net long-term borrowing and repayment |
| `net_cash_from_financing_activities` | DOUBLE PRECISION | Total cash from financing activities |
| `net_cash_from_financing_activities_continuing_operations` | DOUBLE PRECISION | Financing cash flows from continuing operations |
| `net_cash_from_financing_activities_discontinued_operations` | DOUBLE PRECISION | Financing cash flows from discontinued operations |
| `net_cash_from_investing_activities` | DOUBLE PRECISION | Total cash from investing activities |
| `net_cash_from_investing_activities_continuing_operations` | DOUBLE PRECISION | Investing cash flows from continuing operations |
| `net_cash_from_investing_activities_discontinued_operations` | DOUBLE PRECISION | Investing cash flows from discontinued operations |
| `net_cash_from_operating_activities` | DOUBLE PRECISION | Total cash from operating activities |
| `net_cash_from_operating_activities_discontinued_operations` | DOUBLE PRECISION | Operating cash flows from discontinued operations |
| `net_income` | DOUBLE PRECISION | Net income (starting point for indirect method) |
| `noncontrolling_interests` | DOUBLE PRECISION | Cash flows attributable to noncontrolling interests |
| `other_cash_adjustments` | DOUBLE PRECISION | Other adjustments to reconcile net income to cash |
| `other_financing_activities` | DOUBLE PRECISION | Other financing cash flows not classified elsewhere |
| `other_investing_activities` | DOUBLE PRECISION | Other investing cash flows not classified elsewhere |
| `other_operating_activities` | DOUBLE PRECISION | Other operating cash flows not classified elsewhere |
| `purchase_of_property_plant_and_equipment` | DOUBLE PRECISION | Capital expenditures |
| `sale_of_property_plant_and_equipment` | DOUBLE PRECISION | Proceeds from asset disposals |
| `short_term_debt_issuances_repayments` | DOUBLE PRECISION | Net short-term borrowing and repayment |
| `stock_based_compensation` | DOUBLE PRECISION | Non-cash stock-based compensation expense |

Not all fields are present for every company. Missing values are written as empty strings in the CSV.

---

# treasury_yields.csv

Each row contains daily U.S. Treasury yield curve rates.

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Observation date |
| `yield_1_month` | DOUBLE PRECISION | 1-month Treasury yield (%) |
| `yield_3_month` | DOUBLE PRECISION | 3-month Treasury yield (%) |
| `yield_6_month` | DOUBLE PRECISION | 6-month Treasury yield (%) |
| `yield_1_year` | DOUBLE PRECISION | 1-year Treasury yield (%) |
| `yield_2_year` | DOUBLE PRECISION | 2-year Treasury yield (%) |
| `yield_3_year` | DOUBLE PRECISION | 3-year Treasury yield (%) |
| `yield_5_year` | DOUBLE PRECISION | 5-year Treasury yield (%) |
| `yield_7_year` | DOUBLE PRECISION | 7-year Treasury yield (%) |
| `yield_10_year` | DOUBLE PRECISION | 10-year Treasury yield (%) |
| `yield_20_year` | DOUBLE PRECISION | 20-year Treasury yield (%) |
| `yield_30_year` | DOUBLE PRECISION | 30-year Treasury yield (%) |

---

# ten_k_sections.csv

Each row contains one section of text from a 10-K annual filing for a company. Fetched from `/stocks/filings/10-K/vX/sections`.

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `cik` | TEXT | SEC Central Index Key |
| `ticker` | TEXT | Stock ticker symbol |
| `filing_date` | DATE | Date the filing was submitted |
| `period_end` | DATE | End date of the reporting period |
| `section` | TEXT | Section identifier within the 10-K (e.g. Item 1, Item 1A, Item 7, etc.) |
| `filing_url` | TEXT | Direct link to the SEC EDGAR filing document |
| `text` | TEXT | Full text content of the section |

---

# eight_k_text.csv

Each row contains the text content of an 8-K current report filing for a company. Fetched from `/stocks/filings/8-K/vX/text`.

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `accession_number` | TEXT | Unique SEC filing identifier (e.g. `0000320193-25-000079`) |
| `cik` | TEXT | SEC Central Index Key |
| `ticker` | TEXT | Stock ticker symbol |
| `filing_date` | DATE | Date the filing was submitted |
| `form_type` | TEXT | SEC form type (e.g. `8-K`, `8-K/A`) |
| `filing_url` | TEXT | Direct link to the SEC EDGAR filing document |
| `items_text` | TEXT | Combined text content of all items in the 8-K filing |

---

# risk_factors.csv

Each row contains one categorized risk factor extracted from SEC filings for a company. Fetched from `/stocks/filings/vX/risk-factors`.

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `cik` | TEXT | SEC Central Index Key |
| `ticker` | TEXT | Stock ticker symbol |
| `filing_date` | DATE | Date the filing was submitted |
| `primary_category` | TEXT | Top-level risk category |
| `secondary_category` | TEXT | Mid-level risk sub-category |
| `tertiary_category` | TEXT | Most specific risk sub-category |
| `supporting_text` | TEXT | Excerpt from the filing supporting the risk classification |

---

# risk_factors_taxonomy.csv

Each row defines one entry in the risk factors taxonomy hierarchy. Fetched from `/stocks/taxonomies/vX/risk-factors`. This is a single global call, not per-ticker.

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `taxonomy` | TEXT | Taxonomy name/version |
| `primary_category` | TEXT | Top-level risk category |
| `secondary_category` | TEXT | Mid-level risk sub-category |
| `tertiary_category` | TEXT | Most specific risk sub-category |
| `description` | TEXT | Description of what this category covers |

---

# filings_index.csv

Each row contains metadata for one SEC filing from the EDGAR master index. Fetched from `/stocks/filings/vX/index`.

## Fields

| Column | Type | Description |
|--------|------|-------------|
| `accession_number` | TEXT | Unique SEC filing identifier (e.g. `0000320193-25-000079`) |
| `cik` | TEXT | SEC Central Index Key |
| `ticker` | TEXT | Stock ticker symbol (may be empty if unavailable) |
| `issuer_name` | TEXT | Filing entity name |
| `form_type` | TEXT | SEC form type (10-K, 10-Q, 8-K, S-1, 4, etc.) |
| `filing_date` | DATE | Date the filing was submitted |
| `filing_url` | TEXT | Direct link to the SEC EDGAR filing document |
