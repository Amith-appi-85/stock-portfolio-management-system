"""
app/controllers/admin_controller.py
-------------------------------------------
Business logic for the Admin Panel: manage users, manage stocks, view all
transactions, and generate simple aggregate reports.
"""

from app.models import user_model, stock_model, transaction_model
from app.utils import stock_data_service
from app.utils.validators import is_non_empty_string


def get_all_users_for_admin():
    return user_model.get_all_users()


def toggle_user_status(user_id, new_status):
    user_model.set_user_active_status(user_id, new_status)
    return True, "User status updated."


def change_user_role(user_id, role):
    if role not in ("user", "admin"):
        return False, "Invalid role."
    user_model.update_user_role(user_id, role)
    return True, "User role updated."


def remove_user(user_id):
    user_model.delete_user(user_id)
    return True, "User deleted."


def get_all_stocks_for_admin():
    return stock_model.get_all_stocks(active_only=False)


def add_new_stock(ticker_symbol, company_name, sector_id, exchange, currency):
    if not is_non_empty_string(ticker_symbol) or not is_non_empty_string(company_name):
        return False, "Ticker symbol and company name are required.", None

    ticker_symbol = ticker_symbol.strip().upper()

    existing = stock_model.get_stock_by_ticker(ticker_symbol)
    if existing:
        return False, "A stock with this ticker symbol already exists.", None

    # Validate against live market data before inserting
    if not stock_data_service.validate_ticker(ticker_symbol):
        return False, f"Could not validate '{ticker_symbol}' against live market data. Check the symbol.", None

    price = stock_data_service.get_current_price(ticker_symbol) or 0.0
    stock_id = stock_model.create_stock(ticker_symbol, company_name, sector_id or None, exchange, currency, price)
    return True, f"Stock {ticker_symbol} added successfully.", {"stock_id": stock_id}


def edit_stock(stock_id, company_name, sector_id, exchange, currency, is_active):
    stock_model.update_stock(stock_id, company_name, sector_id or None, exchange, currency, is_active)
    return True, "Stock updated successfully."


def remove_stock(stock_id):
    stock_model.delete_stock(stock_id)
    return True, "Stock deleted."


def get_all_transactions_for_admin():
    return transaction_model.get_all_transactions()


def generate_summary_report():
    """Simple aggregate report for the admin dashboard / 'Generate Reports' feature."""
    total_users = user_model.count_users()
    total_stocks = stock_model.count_stocks()
    total_transactions = transaction_model.count_transactions()
    txn_volume_by_day = transaction_model.get_admin_transaction_volume_by_day(30)
    sector_distribution = stock_model.get_sector_wise_stock_count()

    return {
        "total_users": total_users,
        "total_stocks": total_stocks,
        "total_transactions": total_transactions,
        "txn_volume_by_day": txn_volume_by_day,
        "sector_distribution": sector_distribution,
    }
