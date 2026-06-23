"""
app/controllers/watchlist_controller.py
-------------------------------------------
Thin business-logic layer for the watchlist feature.
"""

from app.models import stock_model, watchlist_model
from app.utils.validators import is_positive_integer


def add_stock_to_watchlist(user_id, stock_id):
    if not is_positive_integer(stock_id):
        return False, "Invalid stock."

    stock = stock_model.get_stock_by_id(stock_id)
    if not stock:
        return False, "Stock not found."

    added = watchlist_model.add_to_watchlist(user_id, stock_id)
    if not added:
        return False, f"{stock['ticker_symbol']} is already in your watchlist."
    return True, f"{stock['ticker_symbol']} added to watchlist."


def remove_stock_from_watchlist(user_id, stock_id):
    if not is_positive_integer(stock_id):
        return False, "Invalid stock."
    rows_affected = watchlist_model.remove_from_watchlist(user_id, stock_id)
    if rows_affected == 0:
        return False, "Stock was not found in your watchlist."
    return True, "Removed from watchlist."


def get_user_watchlist(user_id):
    return watchlist_model.get_watchlist_by_user(user_id)
