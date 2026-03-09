import asyncio
import aiohttp
import argparse
import csv
import time
import sys
from datetime import datetime

import pandas as pd
from tqdm import tqdm

# --- Constants ---

API_BASE_URL = "https://api.massive.com"

CANDLE_COLUMNS = [
    "ticker", "timestamp", "open", "high", "low", "close", "volume", "vw", "n",
    "EMA8", "EMA21", "EMA34", "SMA10", "SMA20", "SMA50", "RSI",
    "MACD", "MACD_signal", "MACD_hist",
]

TREASURY_COLUMNS = [
    "date", "yield_1_month", "yield_3_month", "yield_6_month",
    "yield_1_year", "yield_2_year", "yield_3_year", "yield_5_year",
    "yield_7_year", "yield_10_year", "yield_20_year", "yield_30_year",
]

TEN_K_SECTIONS_COLUMNS = [
    "cik", "ticker", "filing_date", "period_end", "section", "filing_url", "text",
]

EIGHT_K_TEXT_COLUMNS = [
    "accession_number", "cik", "ticker", "filing_date", "form_type",
    "filing_url", "items_text",
]

RISK_FACTORS_COLUMNS = [
    "cik", "ticker", "filing_date", "primary_category",
    "secondary_category", "tertiary_category", "supporting_text",
]

RISK_FACTORS_TAXONOMY_COLUMNS = [
    "taxonomy", "primary_category", "secondary_category",
    "tertiary_category", "description",
]

FILINGS_INDEX_COLUMNS = [
    "accession_number", "cik", "ticker", "issuer_name",
    "form_type", "filing_date", "filing_url",
]

SHORT_INTEREST_COLUMNS = [
    "ticker", "short_interest", "settlement_date",
    "days_to_cover", "avg_daily_volume",
]

SHORT_VOLUME_COLUMNS = [
    "ticker", "date", "short_volume", "total_volume",
    "short_volume_ratio", "exempt_volume", "non_exempt_volume",
    "adf_short_volume", "adf_short_volume_exempt",
    "nasdaq_carteret_short_volume", "nasdaq_carteret_short_volume_exempt",
    "nasdaq_chicago_short_volume", "nasdaq_chicago_short_volume_exempt",
    "nyse_short_volume", "nyse_short_volume_exempt",
]

FLOAT_COLUMNS = [
    "ticker", "effective_date", "free_float", "free_float_percent",
]

# --- PostgreSQL type maps ---

CANDLE_TYPES = {
    "ticker": "TEXT", "timestamp": "TIMESTAMP", "open": "DOUBLE PRECISION",
    "high": "DOUBLE PRECISION", "low": "DOUBLE PRECISION", "close": "DOUBLE PRECISION",
    "volume": "DOUBLE PRECISION", "vw": "DOUBLE PRECISION", "n": "BIGINT",
    "EMA8": "DOUBLE PRECISION", "EMA21": "DOUBLE PRECISION", "EMA34": "DOUBLE PRECISION",
    "SMA10": "DOUBLE PRECISION", "SMA20": "DOUBLE PRECISION", "SMA50": "DOUBLE PRECISION",
    "RSI": "DOUBLE PRECISION", "MACD": "DOUBLE PRECISION", "MACD_signal": "DOUBLE PRECISION",
    "MACD_hist": "DOUBLE PRECISION",
}

NEWS_TYPES = {
    "id": "TEXT", "title": "TEXT", "author": "TEXT",
    "published_utc": "TIMESTAMP", "article_url": "TEXT",
    "image_url": "TEXT", "description": "TEXT",
    "publisher_name": "TEXT", "publisher_homepage_url": "TEXT",
    "publisher_logo_url": "TEXT",
    "publisher_favicon_url": "TEXT",
}

NEWS_INSIGHTS_COLUMNS = ["news_id", "ticker", "sentiment", "sentiment_reasoning"]
NEWS_INSIGHTS_TYPES = {
    "news_id": "TEXT", "ticker": "TEXT",
    "sentiment": "TEXT", "sentiment_reasoning": "TEXT",
}

NEWS_TICKERS_COLUMNS = ["news_id", "ticker"]
NEWS_TICKERS_TYPES = {"news_id": "TEXT", "ticker": "TEXT"}

NEWS_KEYWORDS_COLUMNS = ["news_id", "keyword"]
NEWS_KEYWORDS_TYPES = {"news_id": "TEXT", "keyword": "TEXT"}

TREASURY_TYPES = {
    "date": "DATE", "yield_1_month": "DOUBLE PRECISION",
    "yield_3_month": "DOUBLE PRECISION", "yield_6_month": "DOUBLE PRECISION",
    "yield_1_year": "DOUBLE PRECISION", "yield_2_year": "DOUBLE PRECISION",
    "yield_3_year": "DOUBLE PRECISION", "yield_5_year": "DOUBLE PRECISION",
    "yield_7_year": "DOUBLE PRECISION", "yield_10_year": "DOUBLE PRECISION",
    "yield_20_year": "DOUBLE PRECISION", "yield_30_year": "DOUBLE PRECISION",
}

TEN_K_SECTIONS_TYPES = {
    "cik": "TEXT", "ticker": "TEXT", "filing_date": "DATE",
    "period_end": "DATE", "section": "TEXT", "filing_url": "TEXT",
    "text": "TEXT",
}

EIGHT_K_TEXT_TYPES = {
    "accession_number": "TEXT", "cik": "TEXT", "ticker": "TEXT",
    "filing_date": "DATE", "form_type": "TEXT", "filing_url": "TEXT",
    "items_text": "TEXT",
}

RISK_FACTORS_TYPES = {
    "cik": "TEXT", "ticker": "TEXT", "filing_date": "DATE",
    "primary_category": "TEXT", "secondary_category": "TEXT",
    "tertiary_category": "TEXT", "supporting_text": "TEXT",
}

RISK_FACTORS_TAXONOMY_TYPES = {
    "taxonomy": "TEXT", "primary_category": "TEXT",
    "secondary_category": "TEXT",
    "tertiary_category": "TEXT", "description": "TEXT",
}

FILINGS_INDEX_TYPES = {
    "accession_number": "TEXT", "cik": "TEXT", "ticker": "TEXT",
    "issuer_name": "TEXT", "form_type": "TEXT",
    "filing_date": "DATE", "filing_url": "TEXT",
}

SHORT_INTEREST_TYPES = {
    "ticker": "TEXT", "short_interest": "BIGINT",
    "settlement_date": "DATE", "days_to_cover": "DOUBLE PRECISION",
    "avg_daily_volume": "BIGINT",
}

SHORT_VOLUME_TYPES = {
    "ticker": "TEXT", "date": "DATE",
    "short_volume": "DOUBLE PRECISION", "total_volume": "DOUBLE PRECISION",
    "short_volume_ratio": "DOUBLE PRECISION",
    "exempt_volume": "DOUBLE PRECISION", "non_exempt_volume": "DOUBLE PRECISION",
    "adf_short_volume": "BIGINT", "adf_short_volume_exempt": "BIGINT",
    "nasdaq_carteret_short_volume": "BIGINT", "nasdaq_carteret_short_volume_exempt": "BIGINT",
    "nasdaq_chicago_short_volume": "BIGINT", "nasdaq_chicago_short_volume_exempt": "BIGINT",
    "nyse_short_volume": "BIGINT", "nyse_short_volume_exempt": "BIGINT",
}

FLOAT_TYPES = {
    "ticker": "TEXT", "effective_date": "DATE",
    "free_float": "BIGINT", "free_float_percent": "DOUBLE PRECISION",
}


# --- Rate Limiter ---

class RateLimiter:
    def __init__(self, max_calls=5, period=60.0):
        self.max_calls = max_calls
        self.period = period
        self.interval = period / max_calls
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            if elapsed < self.interval:
                await asyncio.sleep(self.interval - elapsed)
            self._last_call = time.monotonic()


rate_limiter = None


# --- Technical Indicator Functions ---

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()


def sma(series, window):
    return series.rolling(window=window).mean()


def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def calculate_indicators(df):
    df["EMA8"] = ema(df["close"], 8)
    df["EMA21"] = ema(df["close"], 21)
    df["EMA34"] = ema(df["close"], 34)
    df["SMA10"] = sma(df["close"], 10)
    df["SMA20"] = sma(df["close"], 20)
    df["SMA50"] = sma(df["close"], 50)
    df["RSI"] = rsi(df["close"])
    macd_line, signal_line, hist = macd(df["close"])
    df["MACD"] = macd_line
    df["MACD_signal"] = signal_line
    df["MACD_hist"] = hist
    return df.dropna()


# --- HTTP helpers ---

async def fetch_json(url, session, params=None, max_retries=3):
    if params is None:
        params = {}
    for attempt in range(max_retries):
        await rate_limiter.acquire()
        tqdm.write(f"  GET {url}")
        try:
            async with session.get(url, params=params) as response:
                if response.status == 429:
                    wait = 60 * (attempt + 1)
                    tqdm.write(f"  429 Too Many Requests — retrying {url} in {wait}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait)
                    continue
                if response.status != 200:
                    tqdm.write(f"  {response.status} {response.reason} — skipping {url}")
                    return {"results": []}
                data = await response.json()
                count = len(data.get("results", data.get("data", [])))
                tqdm.write(f"  {response.status} OK ({count} results)")
                return data
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            wait = 30 * (attempt + 1)
            tqdm.write(f"  {type(e).__name__} — retrying {url} in {wait}s (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(wait)
    tqdm.write(f"  Failed after {max_retries} retries — skipping {url}")
    return {"results": []}


async def fetch_json_paginated(url, session, params=None):
    all_results = []
    data = await fetch_json(url, session, params)
    all_results.extend(data.get("results", []))
    next_url = data.get("next_url")
    while next_url:
        data = await fetch_json(next_url, session)
        all_results.extend(data.get("results", []))
        next_url = data.get("next_url")
    return all_results


# --- Fetch functions ---

async def fetch_candles_and_indicators(api_key, stock, start_date, session):
    today = datetime.today().strftime("%Y-%m-%d")
    url = f"{API_BASE_URL}/v2/aggs/ticker/{stock}/range/1/day/{start_date}/{today}"
    params = {"apiKey": api_key, "adjusted": "true", "sort": "asc"}
    data = await fetch_json(url, session, params)
    results = data.get("results", [])
    if not results:
        return []
    df = pd.DataFrame(results)
    df.rename(columns={
        "t": "timestamp", "o": "open", "h": "high",
        "l": "low", "c": "close", "v": "volume",
    }, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = calculate_indicators(df)
    df["ticker"] = stock
    df["timestamp"] = df["timestamp"].astype(str)
    return df.to_dict(orient="records")


async def fetch_news_data(api_key, ticker, session):
    url = f"{API_BASE_URL}/v2/reference/news"
    params = {"apiKey": api_key, "ticker": ticker}
    data = await fetch_json(url, session, params)
    return data.get("results", [])


async def fetch_treasury_yields(api_key, session):
    url = f"{API_BASE_URL}/fed/v1/treasury-yields"
    params = {"apiKey": api_key}
    data = await fetch_json(url, session, params)
    return data.get("results", [])


async def fetch_ten_k_sections(api_key, ticker, session):
    url = f"{API_BASE_URL}/stocks/filings/10-K/vX/sections"
    params = {"apiKey": api_key, "ticker": ticker, "limit": 9999}
    return await fetch_json_paginated(url, session, params)


async def fetch_eight_k_text(api_key, ticker, session):
    url = f"{API_BASE_URL}/stocks/filings/8-K/vX/text"
    params = {"apiKey": api_key, "ticker": ticker, "limit": 999}
    return await fetch_json_paginated(url, session, params)


async def fetch_risk_factors(api_key, ticker, session):
    url = f"{API_BASE_URL}/stocks/filings/vX/risk-factors"
    params = {"apiKey": api_key, "ticker": ticker, "limit": 49999}
    return await fetch_json_paginated(url, session, params)


async def fetch_risk_factors_taxonomy(api_key, session):
    url = f"{API_BASE_URL}/stocks/taxonomies/vX/risk-factors"
    params = {"apiKey": api_key, "limit": 999}
    return await fetch_json_paginated(url, session, params)


async def fetch_filings_index(api_key, ticker, session):
    url = f"{API_BASE_URL}/stocks/filings/vX/index"
    params = {"apiKey": api_key, "ticker": ticker, "limit": 50000}
    return await fetch_json_paginated(url, session, params)


async def fetch_short_interest(api_key, ticker, session):
    url = f"{API_BASE_URL}/stocks/v1/short-interest"
    params = {"apiKey": api_key, "ticker": ticker, "limit": 50000}
    return await fetch_json_paginated(url, session, params)


async def fetch_short_volume(api_key, ticker, session):
    url = f"{API_BASE_URL}/stocks/v1/short-volume"
    params = {"apiKey": api_key, "ticker": ticker, "limit": 50000}
    return await fetch_json_paginated(url, session, params)


async def fetch_float(api_key, ticker, session):
    url = f"{API_BASE_URL}/stocks/vX/float"
    params = {"apiKey": api_key, "ticker": ticker, "limit": 50000}
    return await fetch_json_paginated(url, session, params)


# --- CSV Writers ---

def write_candles_csv(all_records, filename="candles.csv"):
    flat = [r for stock_records in all_records for r in stock_records]
    if not flat:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CANDLE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    print(f"Wrote {len(flat)} rows to {filename}")


def flatten_news_record(item):
    pub = item.get("publisher", {})
    flat = {k: v for k, v in item.items() if k not in ("publisher", "tickers", "keywords", "insights")}
    flat["publisher_name"] = pub.get("name", "")
    flat["publisher_homepage_url"] = pub.get("homepage_url", "")
    flat["publisher_logo_url"] = pub.get("logo_url", "")
    flat["publisher_favicon_url"] = pub.get("favicon_url", "")
    return flat


def extract_news_insights(all_results):
    rows = []
    for news_list in all_results:
        for item in news_list:
            news_id = item.get("id", "")
            for insight in (item.get("insights") or []):
                rows.append({
                    "news_id": news_id,
                    "ticker": insight.get("ticker", ""),
                    "sentiment": insight.get("sentiment", ""),
                    "sentiment_reasoning": insight.get("sentiment_reasoning", ""),
                })
    return rows


def extract_news_tickers(all_results):
    rows = []
    for news_list in all_results:
        for item in news_list:
            news_id = item.get("id", "")
            for ticker in (item.get("tickers") or []):
                rows.append({"news_id": news_id, "ticker": ticker})
    return rows


def extract_news_keywords(all_results):
    rows = []
    for news_list in all_results:
        for item in news_list:
            news_id = item.get("id", "")
            for keyword in (item.get("keywords") or []):
                rows.append({"news_id": news_id, "keyword": keyword})
    return rows


def write_rows_csv(rows, fieldnames, filename):
    if not rows:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {filename}")


def write_news_csv(all_results):
    flat = [flatten_news_record(item) for news_list in all_results for item in news_list]
    write_rows_csv(flat, list(NEWS_TYPES.keys()), "news.csv")
    write_rows_csv(extract_news_insights(all_results), NEWS_INSIGHTS_COLUMNS, "news_insights.csv")
    write_rows_csv(extract_news_tickers(all_results), NEWS_TICKERS_COLUMNS, "news_tickers.csv")
    write_rows_csv(extract_news_keywords(all_results), NEWS_KEYWORDS_COLUMNS, "news_keywords.csv")


def write_treasury_csv(records, filename="treasury_yields.csv"):
    if not records:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TREASURY_COLUMNS, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} rows to {filename}")


def write_ten_k_sections_csv(all_results, filename="ten_k_sections.csv"):
    flat = [r for result_list in all_results for r in result_list]
    if not flat:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TEN_K_SECTIONS_COLUMNS, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    print(f"Wrote {len(flat)} rows to {filename}")


def write_eight_k_text_csv(all_results, filename="eight_k_text.csv"):
    flat = [r for result_list in all_results for r in result_list]
    if not flat:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EIGHT_K_TEXT_COLUMNS, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    print(f"Wrote {len(flat)} rows to {filename}")


def write_risk_factors_csv(all_results, filename="risk_factors.csv"):
    flat = [r for result_list in all_results for r in result_list]
    if not flat:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RISK_FACTORS_COLUMNS, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    print(f"Wrote {len(flat)} rows to {filename}")


def write_risk_factors_taxonomy_csv(records, filename="risk_factors_taxonomy.csv"):
    if not records:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RISK_FACTORS_TAXONOMY_COLUMNS, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} rows to {filename}")


def write_filings_index_csv(all_results, filename="filings_index.csv"):
    flat = [r for result_list in all_results for r in result_list]
    if not flat:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FILINGS_INDEX_COLUMNS, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    print(f"Wrote {len(flat)} rows to {filename}")


def write_short_interest_csv(all_results, filename="short_interest.csv"):
    flat = [r for result_list in all_results for r in result_list]
    if not flat:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SHORT_INTEREST_COLUMNS, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    print(f"Wrote {len(flat)} rows to {filename}")


def write_short_volume_csv(all_results, filename="short_volume.csv"):
    flat = [r for result_list in all_results for r in result_list]
    if not flat:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SHORT_VOLUME_COLUMNS, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    print(f"Wrote {len(flat)} rows to {filename}")


def write_float_csv(all_results, filename="float.csv"):
    flat = [r for result_list in all_results for r in result_list]
    if not flat:
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FLOAT_COLUMNS, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat)
    print(f"Wrote {len(flat)} rows to {filename}")


# --- SQL Generator ---

def generate_sql_file(table_name, column_types, indexes, csv_file, sql_file):
    col_defs = []
    for col, ctype in column_types.items():
        col_defs.append(f"    {col} {ctype}")
    col_defs_str = ",\n".join(col_defs)
    index_stmts = []
    for idx_name, idx_cols in indexes:
        cols_str = ", ".join(idx_cols)
        index_stmts.append(
            f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({cols_str});"
        )
    index_sql = "\n".join(index_stmts)
    sql = (
        f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        f"{col_defs_str}\n"
        f");\n\n"
        f"{index_sql}\n\n"
        f"\\COPY {table_name} FROM '{csv_file}' WITH (FORMAT csv, HEADER true);\n"
    )
    with open(sql_file, "w") as f:
        f.write(sql)
    print(f"Wrote {sql_file}")


SQL_TABLE_CONFIGS = {
    "candles": [
        ("candles", CANDLE_TYPES, [("idx_candles_ticker_timestamp", ["ticker", "timestamp"])]),
    ],
    "news": [
        ("news", NEWS_TYPES, [("idx_news_published_utc", ["published_utc"]), ("idx_news_id", ["id"])]),
        ("news_insights", NEWS_INSIGHTS_TYPES, [("idx_news_insights_news_id", ["news_id"])]),
        ("news_tickers", NEWS_TICKERS_TYPES, [("idx_news_tickers_news_id", ["news_id"]), ("idx_news_tickers_ticker", ["ticker"])]),
        ("news_keywords", NEWS_KEYWORDS_TYPES, [("idx_news_keywords_news_id", ["news_id"])]),
    ],
    "treasury_yields": [
        ("treasury_yields", TREASURY_TYPES, [("idx_treasury_yields_date", ["date"])]),
    ],
    "ten_k_sections": [
        ("ten_k_sections", TEN_K_SECTIONS_TYPES, [("idx_ten_k_sections_ticker_filing_date", ["ticker", "filing_date"])]),
    ],
    "eight_k_text": [
        ("eight_k_text", EIGHT_K_TEXT_TYPES, [("idx_eight_k_text_ticker_filing_date", ["ticker", "filing_date"])]),
    ],
    "risk_factors": [
        ("risk_factors", RISK_FACTORS_TYPES, [("idx_risk_factors_ticker_filing_date_category", ["ticker", "filing_date", "primary_category"])]),
    ],
    "risk_factors_taxonomy": [
        ("risk_factors_taxonomy", RISK_FACTORS_TAXONOMY_TYPES, [("idx_risk_factors_taxonomy_taxonomy_category", ["taxonomy", "primary_category"])]),
    ],
    "filings_index": [
        ("filings_index", FILINGS_INDEX_TYPES, [("idx_filings_index_ticker_filing_date", ["ticker", "filing_date"]), ("idx_filings_index_form_type", ["form_type"])]),
    ],
    "short_interest": [
        ("short_interest", SHORT_INTEREST_TYPES, [("idx_short_interest_ticker_date", ["ticker", "settlement_date"])]),
    ],
    "short_volume": [
        ("short_volume", SHORT_VOLUME_TYPES, [("idx_short_volume_ticker_date", ["ticker", "date"])]),
    ],
    "float": [
        ("float", FLOAT_TYPES, [("idx_float_ticker_date", ["ticker", "effective_date"])]),
    ],
}


def generate_all_sql(endpoints):
    for endpoint in endpoints:
        for table_name, col_types, indexes in SQL_TABLE_CONFIGS.get(endpoint, []):
            generate_sql_file(table_name, col_types, indexes, f"{table_name}.csv", f"{table_name}.sql")


# --- Main Orchestration ---

async def _progress_wrap(coro, pbar):
    result = await coro
    pbar.update(1)
    return result


async def gather_with_progress(tasks, desc):
    pbar = tqdm(total=len(tasks), desc=desc, unit="req")
    results = await asyncio.gather(*[_progress_wrap(t, pbar) for t in tasks])
    pbar.close()
    return list(results)


async def fetch_all_data(api_key, start_date, stocks, endpoints):
    results = {}
    async with aiohttp.ClientSession() as session:
        if "candles" in endpoints:
            tasks = [fetch_candles_and_indicators(api_key, s, start_date, session) for s in stocks]
            results["candles"] = await gather_with_progress(tasks, "Candles")
        if "news" in endpoints:
            tasks = [fetch_news_data(api_key, s, session) for s in stocks]
            results["news"] = await gather_with_progress(tasks, "News")
        if "ten_k_sections" in endpoints:
            tasks = [fetch_ten_k_sections(api_key, s, session) for s in stocks]
            results["ten_k_sections"] = await gather_with_progress(tasks, "10-K sections")
        if "eight_k_text" in endpoints:
            tasks = [fetch_eight_k_text(api_key, s, session) for s in stocks]
            results["eight_k_text"] = await gather_with_progress(tasks, "8-K text")
        if "risk_factors" in endpoints:
            tasks = [fetch_risk_factors(api_key, s, session) for s in stocks]
            results["risk_factors"] = await gather_with_progress(tasks, "Risk factors")
        if "filings_index" in endpoints:
            tasks = [fetch_filings_index(api_key, s, session) for s in stocks]
            results["filings_index"] = await gather_with_progress(tasks, "Filings index")
        if "short_interest" in endpoints:
            tasks = [fetch_short_interest(api_key, s, session) for s in stocks]
            results["short_interest"] = await gather_with_progress(tasks, "Short interest")
        if "short_volume" in endpoints:
            tasks = [fetch_short_volume(api_key, s, session) for s in stocks]
            results["short_volume"] = await gather_with_progress(tasks, "Short volume")
        if "float" in endpoints:
            tasks = [fetch_float(api_key, s, session) for s in stocks]
            results["float"] = await gather_with_progress(tasks, "Float")
        if "treasury_yields" in endpoints:
            tqdm.write("\nFetching treasury yields...")
            results["treasury_yields"] = await fetch_treasury_yields(api_key, session)
        if "risk_factors_taxonomy" in endpoints:
            tqdm.write("\nFetching risk factors taxonomy...")
            results["risk_factors_taxonomy"] = await fetch_risk_factors_taxonomy(api_key, session)
    return results


def write_all_csv(results, endpoints):
    if "candles" in endpoints:
        write_candles_csv(results.get("candles", []))
    if "news" in endpoints:
        write_news_csv(results.get("news", []))
    if "treasury_yields" in endpoints:
        write_treasury_csv(results.get("treasury_yields", []))
    if "ten_k_sections" in endpoints:
        write_ten_k_sections_csv(results.get("ten_k_sections", []))
    if "eight_k_text" in endpoints:
        write_eight_k_text_csv(results.get("eight_k_text", []))
    if "risk_factors" in endpoints:
        write_risk_factors_csv(results.get("risk_factors", []))
    if "risk_factors_taxonomy" in endpoints:
        write_risk_factors_taxonomy_csv(results.get("risk_factors_taxonomy", []))
    if "filings_index" in endpoints:
        write_filings_index_csv(results.get("filings_index", []))
    if "short_interest" in endpoints:
        write_short_interest_csv(results.get("short_interest", []))
    if "short_volume" in endpoints:
        write_short_volume_csv(results.get("short_volume", []))
    if "float" in endpoints:
        write_float_csv(results.get("float", []))


async def main(api_key, start_date, stocks, endpoints):
    per_stock_endpoints = ["candles", "news", "ten_k_sections", "eight_k_text", "risk_factors", "filings_index", "short_interest", "short_volume", "float"]
    single_call_endpoints = ["treasury_yields", "risk_factors_taxonomy"]
    per_stock = sum(1 for e in per_stock_endpoints if e in endpoints)
    single_calls = sum(1 for e in single_call_endpoints if e in endpoints)
    paginated = any(e in endpoints for e in ["ten_k_sections", "eight_k_text", "risk_factors", "risk_factors_taxonomy", "filings_index", "short_interest", "short_volume", "float"])
    total_api_calls = per_stock * len(stocks) + single_calls
    prefix = "~" if paginated else ""
    print(f"Fetching data for {len(stocks)} stock(s): {', '.join(stocks)}")
    print(f"Endpoints: {', '.join(sorted(endpoints))}")
    print(f"Total API calls: {prefix}{total_api_calls} (rate limit: {rate_limiter.max_calls}/min)\n")

    results = await fetch_all_data(api_key, start_date, stocks, endpoints)
    print("\n--- Writing CSV files ---")
    write_all_csv(results, endpoints)
    print("\n--- Generating SQL files ---")
    generate_all_sql(endpoints)
    print("\nDone.")


# --- CLI Interface ---

def cli():
    parser = argparse.ArgumentParser(description="Massive.com data fetcher")
    parser.add_argument("--api_key", required=True, help="Massive.com API Key")
    parser.add_argument("--start_date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--stocks", nargs="+", required=True, help="List of stock tickers")
    parser.add_argument("--rate_limit", type=int, default=5, help="Max API requests per minute (default: 5)")
    all_endpoints = [
        "candles", "news", "treasury_yields",
        "ten_k_sections", "eight_k_text",
        "risk_factors", "risk_factors_taxonomy",
        "filings_index", "short_interest",
        "short_volume", "float",
    ]
    parser.add_argument(
        "--endpoints", nargs="+", default=all_endpoints,
        choices=all_endpoints,
        help="Endpoints to fetch (default: all)",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    global rate_limiter
    rate_limiter = RateLimiter(max_calls=args.rate_limit, period=60.0)
    asyncio.run(main(args.api_key, args.start_date, args.stocks, set(args.endpoints)))


if __name__ == "__main__":
    cli()
