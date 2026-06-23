"""
app/models/transaction_model.py
----------------------------------
Data-access functions for the immutable `transactions` ledger.
"""

from app.utils.db import query_db, execute_db


def create_transaction(user_id, stock_id, transaction_type, quantity, price_per_share):
    total_amount = quantity * price_per_share
    return execute_db(
        """INSERT INTO transactions (user_id, stock_id, transaction_type, quantity, price_per_share, total_amount)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (user_id, stock_id, transaction_type, quantity, price_per_share, total_amount),
        return_lastrowid=True,
    )


def get_transactions_by_user(user_id, limit=100):
    return query_db(
        """SELECT t.*, s.ticker_symbol, s.company_name
           FROM transactions t
           JOIN stocks s ON s.stock_id = t.stock_id
           WHERE t.user_id = %s
           ORDER BY t.transaction_date DESC
           LIMIT %s""",
        (user_id, limit),
    )


def get_all_transactions(limit=200):
    """Admin view: every transaction across all users."""
    return query_db(
        """SELECT t.*, u.username, s.ticker_symbol, s.company_name
           FROM transactions t
           JOIN users u ON u.user_id = t.user_id
           JOIN stocks s ON s.stock_id = t.stock_id
           ORDER BY t.transaction_date DESC
           LIMIT %s""",
        (limit,),
    )


def count_transactions():
    row = query_db("SELECT COUNT(*) AS cnt FROM transactions", one=True)
    return row["cnt"] if row else 0


def get_monthly_investment_trend(user_id):
    """Aggregates BUY/SELL totals per month for the trend chart on the dashboard.

    Note: mysql-connector-python does NOT require doubling '%' inside the
    literal SQL string (unlike pymysql/psycopg2) -- only %s placeholders are
    treated specially. Using '%%' here would be sent to MySQL literally and
    DATE_FORMAT would output the string '%Y-%m' instead of formatting the date.
    """
    return query_db(
        """SELECT
               DATE_FORMAT(transaction_date, '%Y-%m') AS month,
               SUM(CASE WHEN transaction_type = 'BUY' THEN total_amount ELSE 0 END) AS total_bought,
               SUM(CASE WHEN transaction_type = 'SELL' THEN total_amount ELSE 0 END) AS total_sold
           FROM transactions
           WHERE user_id = %s
           GROUP BY month
           ORDER BY month ASC""",
        (user_id,),
    )


def get_admin_transaction_volume_by_day(days=30):
    return query_db(
        """SELECT DATE(transaction_date) AS day, COUNT(*) AS txn_count,
                  SUM(total_amount) AS volume
           FROM transactions
           WHERE transaction_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
           GROUP BY day
           ORDER BY day ASC""",
        (days,),
    )
