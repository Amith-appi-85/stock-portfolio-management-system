"""
app/models/watchlist_model.py
--------------------------------
Data-access functions for the `watchlist` table.
"""

from app.utils.db import query_db, execute_db


def get_watchlist_by_user(user_id):
    return query_db(
        """SELECT w.watchlist_id, w.added_at, s.stock_id, s.ticker_symbol,
                  s.company_name, s.last_price, s.currency, sec.sector_name
           FROM watchlist w
           JOIN stocks s ON s.stock_id = w.stock_id
           LEFT JOIN sectors sec ON sec.sector_id = s.sector_id
           WHERE w.user_id = %s
           ORDER BY w.added_at DESC""",
        (user_id,),
    )


def is_in_watchlist(user_id, stock_id):
    row = query_db(
        "SELECT watchlist_id FROM watchlist WHERE user_id = %s AND stock_id = %s",
        (user_id, stock_id),
        one=True,
    )
    return row is not None


def add_to_watchlist(user_id, stock_id):
    if is_in_watchlist(user_id, stock_id):
        return False
    execute_db(
        "INSERT INTO watchlist (user_id, stock_id) VALUES (%s, %s)",
        (user_id, stock_id),
    )
    return True


def remove_from_watchlist(user_id, stock_id):
    return execute_db(
        "DELETE FROM watchlist WHERE user_id = %s AND stock_id = %s",
        (user_id, stock_id),
    )
