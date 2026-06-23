"""
app/utils/stock_data_service.py
----------------------------------
Wraps the `yfinance` library to fetch live stock data: current price,
company info, historical OHLC data for charts, and simple search/validation.

A tiny in-memory TTL cache is used so the dashboard/portfolio pages
(which may request the same ticker multiple times within seconds) don't
hammer Yahoo Finance on every request — this also makes the app usable
on poor/offline networks during a viva demo (falls back to last cached
value if the API call fails).
"""

import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

# In-memory cache: { ticker: {"data": {...}, "timestamp": float} }
_price_cache = {}
_info_cache = {}
CACHE_TTL = 60  # seconds


def _is_cache_valid(cache_dict, key):
    entry = cache_dict.get(key)
    if not entry:
        return False
    return (time.time() - entry["timestamp"]) < CACHE_TTL


def get_current_price(ticker_symbol):
    if _is_cache_valid(_price_cache, ticker_symbol):
        return _price_cache[ticker_symbol]["data"]

    try:
        url = (
            f"{BASE_URL}"
            f"?function=GLOBAL_QUOTE"
            f"&symbol={ticker_symbol}"
            f"&apikey={API_KEY}"
        )

        response = requests.get(url, timeout=10)
        data = response.json()

        quote = data.get("Global Quote", {})
        price = float(quote.get("05. price"))

        _price_cache[ticker_symbol] = {
            "data": price,
            "timestamp": time.time()
        }

        return price

    except Exception as e:
        print(f"Price API Error: {e}")
        return None


def get_company_info(ticker_symbol):

    if _is_cache_valid(_info_cache, ticker_symbol):
        return _info_cache[ticker_symbol]["data"]

    try:

        url = (
            f"{BASE_URL}"
            f"?function=OVERVIEW"
            f"&symbol={ticker_symbol}"
            f"&apikey={API_KEY}"
        )

        response = requests.get(url, timeout=10)
        info = response.json()

        result = {
            "longName": info.get("Name", ticker_symbol),
            "sector": info.get("Sector", "N/A"),
            "industry": info.get("Industry", "N/A"),
            "marketCap": int(info.get("MarketCapitalization", 0))
                if info.get("MarketCapitalization") else None,
            "currency": "USD",
            "exchange": info.get("Exchange", "N/A"),
            "fiftyTwoWeekHigh": float(info.get("52WeekHigh", 0))
                if info.get("52WeekHigh") else None,
            "fiftyTwoWeekLow": float(info.get("52WeekLow", 0))
                if info.get("52WeekLow") else None,
            "previousClose": None,
            "open": None,
            "dayHigh": None,
            "dayLow": None,
            "volume": None,
            "trailingPE": float(info.get("PERatio", 0))
                if info.get("PERatio") else None,
            "dividendYield": float(info.get("DividendYield", 0))
                if info.get("DividendYield") else None,
            "website": info.get("OfficialSite", "N/A"),
            "longBusinessSummary": info.get(
                "Description",
                "No description available."
            )
        }

        _info_cache[ticker_symbol] = {
            "data": result,
            "timestamp": time.time()
        }

        return result

    except Exception as e:
        print(f"Company Info API Error: {e}")

        return {
            "longName": ticker_symbol,
            "sector": "N/A",
            "industry": "N/A",
            "marketCap": None,
            "currency": "USD",
            "exchange": "N/A",
            "fiftyTwoWeekHigh": None,
            "fiftyTwoWeekLow": None,
            "previousClose": None,
            "open": None,
            "dayHigh": None,
            "dayLow": None,
            "volume": None,
            "trailingPE": None,
            "dividendYield": None,
            "website": "N/A",
            "longBusinessSummary": "No description available."
        }


def get_historical_data(ticker_symbol, period="1mo"):

    try:

        url = (
            f"{BASE_URL}"
            f"?function=TIME_SERIES_DAILY"
            f"&symbol={ticker_symbol}"
            f"&outputsize=compact"
            f"&apikey={API_KEY}"
        )

        response = requests.get(url, timeout=10)
        data = response.json()
        print("API RESPONSE KEYS:", data.keys())
        print(data)

        series = data.get("Time Series (Daily)", {})

        if not series:
            return {
                "labels": [],
                "prices": [],
                "volumes": []
            }

        dates = sorted(series.keys())
          
        if period == "1mo":
            dates = dates[-22:]

        elif period == "3mo":
            dates = dates[-66:]

        elif period == "6mo":
            dates = dates[-100:]


        labels = []
        prices = []
        volumes = []

        for date in dates:
            labels.append(date)
            prices.append(float(series[date]["4. close"]))
            volumes.append(int(series[date]["5. volume"]))

        return {
            "labels": labels,
            "prices": prices,
            "volumes": volumes
        }

    except Exception as e:
        print(f"History API Error: {e}")

        print("DATES:", labels[:5])
        print("PRICES:", prices[:5])
        print("COUNT:", len(labels))

        return {
            "labels": [],
            "prices": [],
            "volumes": []
        }


def validate_ticker(ticker_symbol):
    """Quick check used by the admin 'add stock' form to confirm a ticker
    is real before inserting it into the database."""
    price = get_current_price(ticker_symbol)
    return price is not None


def get_batch_prices(ticker_symbols):
    """Fetch current prices for multiple tickers at once (used to refresh
    the `stocks.last_price` cache column in bulk)."""
    results = {}
    for symbol in ticker_symbols:
        results[symbol] = get_current_price(symbol)
    return results
