"""
app/models/stock_model.py
---------------------------
Data-access functions for the `stocks` and `sectors` tables.
"""

from app.utils.db import query_db, execute_db


def get_all_stocks(active_only=True):
    sql = """SELECT s.*, sec.sector_name
             FROM stocks s
             LEFT JOIN sectors sec ON sec.sector_id = s.sector_id"""
    if active_only:
        sql += " WHERE s.is_active = 1"
    sql += " ORDER BY s.ticker_symbol ASC"
    return query_db(sql)


def get_stock_by_id(stock_id):
    return query_db(
        """SELECT s.*, sec.sector_name
           FROM stocks s
           LEFT JOIN sectors sec ON sec.sector_id = s.sector_id
           WHERE s.stock_id = %s""",
        (stock_id,),
        one=True,
    )


def get_stock_by_ticker(ticker_symbol):
    return query_db(
        """SELECT s.*, sec.sector_name
           FROM stocks s
           LEFT JOIN sectors sec ON sec.sector_id = s.sector_id
           WHERE s.ticker_symbol = %s""",
        (ticker_symbol,),
        one=True,
    )


def search_stocks(search_term):
    like_term = f"%{search_term}%"
    return query_db(
        """SELECT s.*, sec.sector_name
           FROM stocks s
           LEFT JOIN sectors sec ON sec.sector_id = s.sector_id
           WHERE s.is_active = 1
             AND (s.ticker_symbol LIKE %s OR s.company_name LIKE %s)
           ORDER BY s.ticker_symbol ASC
           LIMIT 25""",
        (like_term, like_term),
    )


def create_stock(ticker_symbol, company_name, sector_id, exchange, currency, last_price=0.0):
    return execute_db(
        """INSERT INTO stocks (ticker_symbol, company_name, sector_id, exchange, currency, last_price)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (ticker_symbol, company_name, sector_id, exchange, currency, last_price),
        return_lastrowid=True,
    )


def update_stock(stock_id, company_name, sector_id, exchange, currency, is_active):
    return execute_db(
        """UPDATE stocks
           SET company_name = %s, sector_id = %s, exchange = %s, currency = %s, is_active = %s
           WHERE stock_id = %s""",
        (company_name, sector_id, exchange, currency, is_active, stock_id),
    )


def update_stock_price(stock_id, new_price):
    return execute_db(
        "UPDATE stocks SET last_price = %s WHERE stock_id = %s",
        (new_price, stock_id),
    )


def delete_stock(stock_id):
    return execute_db("DELETE FROM stocks WHERE stock_id = %s", (stock_id,))


def get_all_sectors():
    return query_db("SELECT * FROM sectors ORDER BY sector_name ASC")


def create_sector(sector_name, description=None):
    return execute_db(
        "INSERT INTO sectors (sector_name, description) VALUES (%s, %s)",
        (sector_name, description),
        return_lastrowid=True,
    )


def count_stocks():
    row = query_db("SELECT COUNT(*) AS cnt FROM stocks", one=True)
    return row["cnt"] if row else 0


def get_sector_wise_stock_count():
    return query_db(
        """SELECT sec.sector_name, COUNT(s.stock_id) AS stock_count
           FROM sectors sec
           LEFT JOIN stocks s ON s.sector_id = sec.sector_id AND s.is_active = 1
           GROUP BY sec.sector_id, sec.sector_name
           ORDER BY stock_count DESC"""
    )
