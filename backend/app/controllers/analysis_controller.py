"""
app/controllers/analysis_controller.py
-------------------------------------------
Powers the Stock Analysis page: search, company info, current price,
historical chart data for 1mo/6mo/1y, and sector-level analysis.
"""

from app.models import stock_model
from app.utils import stock_data_service

PERIOD_MAP = {
    "1m": "1mo",
    "3m": "3mo",
    "6m": "6mo",
}


def search_for_stocks(search_term):
    if not search_term or len(search_term.strip()) == 0:
        return []
    return stock_model.search_stocks(search_term.strip())


def get_stock_analysis(stock_id):
    """Combines DB record with live yfinance company info + current price."""
    stock = stock_model.get_stock_by_id(stock_id)
    if not stock:
        return None

    ticker = stock["ticker_symbol"]
    info = stock_data_service.get_company_info(ticker)
    current_price = stock_data_service.get_current_price(ticker)
    if current_price is None:
        current_price = float(stock["last_price"])
    else:
        stock_model.update_stock_price(stock_id, current_price)

    return {
        "stock": stock,
        "company_info": info,
        "current_price": current_price,
    }


def get_chart_data(ticker_symbol, period_key):
    period = PERIOD_MAP.get(period_key, "1mo")
    return stock_data_service.get_historical_data(ticker_symbol, period)


def get_sector_analysis():
    """Returns sector-wise stock counts and (where available) average
    price movement, used for the 'Sector analysis' view."""
    sectors = stock_model.get_sector_wise_stock_count()
    all_stocks = stock_model.get_all_stocks()

    sector_map = {}
    for stock in all_stocks:
        sector_name = stock["sector_name"] or "Uncategorized"
        sector_map.setdefault(sector_name, []).append(stock)

    return {
        "sector_counts": sectors,
        "sector_stocks": sector_map,
    }
