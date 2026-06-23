"""
app/controllers/portfolio_controller.py
-------------------------------------------
Core virtual-trading business logic: BUY and SELL operations. Each trade:
  1. Validates the request (quantity, stock existence, sufficient funds/shares)
  2. Fetches the live current price via yfinance
  3. Writes an immutable row to `transactions`
  4. Updates the aggregated `portfolio` row
  5. Debits/credits the user's virtual_balance

These steps are wrapped so that if anything fails partway, earlier writes
in the SAME function call still leave the DB in a consistent state because
we validate everything BEFORE writing anything.
"""

from app.models import stock_model, portfolio_model, transaction_model, user_model
from app.utils.stock_data_service import get_current_price
from app.utils.validators import is_positive_integer


def buy_stock(user_id, stock_id, quantity):
    if not is_positive_integer(stock_id) or not is_positive_integer(quantity):
        return False, "Invalid stock or quantity.", None
    quantity = int(quantity)

    stock = stock_model.get_stock_by_id(stock_id)
    if not stock:
        return False, "Stock not found.", None

    price = get_current_price(stock["ticker_symbol"])
    if price is None:
        # fall back to last cached DB price if live API is unreachable
        price = float(stock["last_price"])
    if price <= 0:
        return False, "Could not fetch a valid current price for this stock.", None

    total_cost = round(price * quantity, 2)
    balance = user_model.get_user_balance(user_id)

    if balance < total_cost:
        return False, (f"Insufficient virtual balance. Required: {total_cost:.2f}, "
                        f"Available: {balance:.2f}"), None

    # Persist: transaction -> portfolio -> balance, and refresh cached stock price
    transaction_model.create_transaction(user_id, stock_id, "BUY", quantity, price)
    portfolio_model.upsert_buy(user_id, stock_id, quantity, price)
    user_model.adjust_user_balance(user_id, -total_cost)
    stock_model.update_stock_price(stock_id, price)

    return True, f"Successfully bought {quantity} share(s) of {stock['ticker_symbol']} at {price:.2f} each.", {
        "ticker": stock["ticker_symbol"], "quantity": quantity, "price": price, "total": total_cost
    }


def sell_stock(user_id, stock_id, quantity):
    if not is_positive_integer(stock_id) or not is_positive_integer(quantity):
        return False, "Invalid stock or quantity.", None
    quantity = int(quantity)

    stock = stock_model.get_stock_by_id(stock_id)
    if not stock:
        return False, "Stock not found.", None

    holding = portfolio_model.get_holding(user_id, stock_id)
    if not holding or holding["quantity"] < quantity:
        owned = holding["quantity"] if holding else 0
        return False, f"You only own {owned} share(s) of {stock['ticker_symbol']}.", None

    price = get_current_price(stock["ticker_symbol"])
    if price is None:
        price = float(stock["last_price"])
    if price <= 0:
        return False, "Could not fetch a valid current price for this stock.", None

    total_credit = round(price * quantity, 2)

    transaction_model.create_transaction(user_id, stock_id, "SELL", quantity, price)
    portfolio_model.reduce_on_sell(user_id, stock_id, quantity)
    user_model.adjust_user_balance(user_id, total_credit)
    stock_model.update_stock_price(stock_id, price)

    return True, f"Successfully sold {quantity} share(s) of {stock['ticker_symbol']} at {price:.2f} each.", {
        "ticker": stock["ticker_symbol"], "quantity": quantity, "price": price, "total": total_credit
    }


def get_full_portfolio_view(user_id):
    holdings = portfolio_model.get_portfolio_by_user(user_id)
    totals = portfolio_model.get_user_dashboard_totals(user_id)
    balance = user_model.get_user_balance(user_id)

    recent_transactions = transaction_model.get_transactions_by_user(
        user_id,
        limit=5
    )

    return {
        "holdings": holdings,
        "total_investment": float(totals.get("total_investment") or 0),
        "current_value": float(totals.get("current_value") or 0),
        "total_profit_loss": float(totals.get("total_profit_loss") or 0),
        "virtual_balance": balance,
        "recent_transactions": recent_transactions
    }