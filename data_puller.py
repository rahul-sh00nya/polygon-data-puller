import asyncio
import aiohttp
import argparse
import json
from datetime import datetime
import pandas as pd
from asyncio import Semaphore
from dateutil import parser as date_parser
import sys

# Set up a semaphore for rate limiting
MAX_CONCURRENT_REQUESTS = 5
semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)

# --- Utility Functions ---

def calculate_indicators(df):
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

    df['EMA8'] = ema(df['close'], 8)
    df['EMA21'] = ema(df['close'], 21)
    df['EMA34'] = ema(df['close'], 34)
    df['SMA10'] = sma(df['close'], 10)
    df['SMA20'] = sma(df['close'], 20)
    df['SMA50'] = sma(df['close'], 50)
    df['RSI'] = rsi(df['close'])
    macd_line, signal_line, hist = macd(df['close'])
    df['MACD'] = macd_line
    df['MACD_signal'] = signal_line
    df['MACD_hist'] = hist

    return df.dropna()

async def fetch_json(url, session, params={}):
    async with semaphore:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()

# --- Main Async Tasks ---

async def fetch_candles_and_indicators(api_key, stock, start_date, session):
    url = f"https://api.polygon.io/v2/aggs/ticker/{stock}/range/1/day/{start_date}/{datetime.today().strftime('%Y-%m-%d')}"
    params = {"apiKey": api_key, "adjusted": "true", "sort": "asc"}
    data = await fetch_json(url, session, params)
    results = data.get("results", [])

    if not results:
        return []

    df = pd.DataFrame(results)
    df.rename(columns={
        't': 'timestamp',
        'o': 'open',
        'h': 'high',
        'l': 'low',
        'c': 'close',
        'v': 'volume'
    }, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = calculate_indicators(df)
    df['ticker'] = stock
    # Convert timestamps to ISO strings
    df['timestamp'] = df['timestamp'].astype(str)
    return df.to_dict(orient='records')

async def fetch_news_data(api_key, ticker, session):
    url = f"https://api.polygon.io/v2/reference/news"
    params = {"apiKey": api_key, "ticker": ticker}
    data = await fetch_json(url, session, params)
    return data.get("results", [])

async def fetch_financials(api_key, ticker, session):
    url = f"https://api.polygon.io/vX/reference/financials"
    params = {"apiKey": api_key, "ticker": ticker}
    data = await fetch_json(url, session, params)
    return data.get("results", [])

async def fetch_treasury_yields(api_key, session):
    url = f"https://api.polygon.io/fed/v1/treasury-yields"
    params = {"apiKey": api_key}
    data = await fetch_json(url, session, params)
    return data.get("results", [])

# --- Main Orchestration ---

async def main(api_key, start_date, stocks):
    async with aiohttp.ClientSession() as session:
        tasks = []
        candle_tasks = []
        news_tasks = []
        financials_tasks = []

        for stock in stocks:
            candle_tasks.append(fetch_candles_and_indicators(api_key, stock, start_date, session))
            news_tasks.append(fetch_news_data(api_key, stock, session))
            financials_tasks.append(fetch_financials(api_key, stock, session))

        treasury_task = fetch_treasury_yields(api_key, session)

        candle_results, news_results, financials_results, treasury_result = await asyncio.gather(
            asyncio.gather(*candle_tasks),
            asyncio.gather(*news_tasks),
            asyncio.gather(*financials_tasks),
            treasury_task
        )

        with open("candles.jsonl", "w") as f:
            for stock_records in candle_results:
                for record in stock_records:
                    f.write(json.dumps(record) + "\n")

        with open("news.jsonl", "w") as f:
            for news_list in news_results:
                for item in news_list:
                    f.write(json.dumps(item) + "\n")

        with open("financials.jsonl", "w") as f:
            for financial_list in financials_results:
                for item in financial_list:
                    f.write(json.dumps(item) + "\n")

        with open("treasury_yields.jsonl", "w") as f:
            for item in treasury_result:
                f.write(json.dumps(item) + "\n")

# --- CLI Interface ---

def cli():
    parser = argparse.ArgumentParser(description="Polygon.io data fetcher")
    parser.add_argument("--api_key", required=True, help="Polygon.io API Key")
    parser.add_argument("--start_date", required=True, help="Start date for stock data in YYYY-MM-DD format")
    parser.add_argument("--stocks", nargs='+', required=True, help="List of stock tickers")

    if len(sys.argv) == 1:
        print("No arguments provided. Example usage:\npython script.py --api_key YOUR_API_KEY --start_date 2023-01-01 --stocks AAPL TSLA")
        sys.exit(1)

    args = parser.parse_args()
    asyncio.run(main(args.api_key, args.start_date, args.stocks))

if __name__ == "__main__":
    cli()

