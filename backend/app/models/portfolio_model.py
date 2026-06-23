"""
app/models/portfolio_model.py
-------------------------------
Data-access functions for the `portfolio` table — the aggregated current
holdings of each user. The portfolio table is kept in sync by the
transaction controller every time a BUY/SELL happens (see
app/controllers/portfolio_controller.py).
"""

from app.utils.db import query_db, execute_db


def get_portfolio_by_user(user_id):
    """Returns each holding joined with live stock info, plus computed
    current value / profit-loss using the vw_portfolio_summary view."""
    return query_db(
        "SELECT * FROM vw_portfolio_summary WHERE user_id = %s ORDER BY ticker_symbol ASC",
        (user_id,),
    )


def get_holding(user_id, stock_id):
    return query_db(
        "SELECT * FROM portfolio WHERE user_id = %s AND stock_id = %s",
        (user_id, stock_id),
        one=True,
    )


def upsert_buy(user_id, stock_id, quantity, price):
    """Adds to an existing holding (recomputing weighted average buy price)
    or creates a new holding row if none exists yet."""
    existing = get_holding(user_id, stock_id)
    trade_amount = quantity * price

    if existing:
        new_quantity = existing["quantity"] + quantity
        new_total_invested = float(existing["total_invested"]) + trade_amount
        new_avg_price = new_total_invested / new_quantity if new_quantity > 0 else 0
        execute_db(
            """UPDATE portfolio
               SET quantity = %s, average_buy_price = %s, total_invested = %s
               WHERE portfolio_id = %s""",
            (new_quantity, new_avg_price, new_total_invested, existing["portfolio_id"]),
        )
    else:
        execute_db(
            """INSERT INTO portfolio (user_id, stock_id, quantity, average_buy_price, total_invested)
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, stock_id, quantity, price, trade_amount),
        )


def reduce_on_sell(user_id, stock_id, quantity):
    """Reduces quantity after a SELL. total_invested is reduced proportionally
    (based on average_buy_price) so profit/loss tracking on the REMAINING
    shares stays accurate. Returns the realized amount at average cost for
    reference, or None if the holding doesn't exist / insufficient quantity."""
    existing = get_holding(user_id, stock_id)
    if not existing or existing["quantity"] < quantity:
        return None

    new_quantity = existing["quantity"] - quantity
    avg_price = float(existing["average_buy_price"])
    cost_removed = avg_price * quantity
    new_total_invested = max(float(existing["total_invested"]) - cost_removed, 0)

    if new_quantity == 0:
        execute_db(
            "UPDATE portfolio SET quantity = 0, total_invested = 0 WHERE portfolio_id = %s",
            (existing["portfolio_id"],),
        )
    else:
        execute_db(
            "UPDATE portfolio SET quantity = %s, total_invested = %s WHERE portfolio_id = %s",
            (new_quantity, new_total_invested, existing["portfolio_id"]),
        )
    return cost_removed


def get_user_dashboard_totals(user_id):
    row = query_db("SELECT * FROM vw_user_dashboard WHERE user_id = %s", (user_id,), one=True)
    if not row:
        return {"total_investment": 0, "current_value": 0, "total_profit_loss": 0}
    return row


def get_sector_allocation(user_id):
    return query_db(
        "SELECT * FROM vw_sector_allocation WHERE user_id = %s ORDER BY sector_value DESC",
        (user_id,),
    )


def get_best_and_worst_performers(user_id):
    """Returns (best, worst) holdings by profit_loss_percent, or (None, None)
    if the user has no holdings."""
    holdings = get_portfolio_by_user(user_id)
    if not holdings:
        return None, None
    best = max(holdings, key=lambda h: float(h["profit_loss_percent"]))
    worst = min(holdings, key=lambda h: float(h["profit_loss_percent"]))
    return best, worst
