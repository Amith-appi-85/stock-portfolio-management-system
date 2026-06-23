"""
app/routes/admin_routes.py
-----------------------------
Routes for the Admin Panel: manage users, manage stocks, view transactions,
generate reports.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.controllers import admin_controller
from app.models import stock_model
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@admin_required
def dashboard():
    report = admin_controller.generate_summary_report()
    return render_template("admin/dashboard.html", report=report)


# ---------------- User Management ----------------

@admin_bp.route("/users")
@admin_required
def users():
    all_users = admin_controller.get_all_users_for_admin()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    new_status = request.form.get("is_active") == "1"
    admin_controller.toggle_user_status(user_id, new_status)
    flash("User status updated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@admin_required
def change_role(user_id):
    role = request.form.get("role")
    success, message = admin_controller.change_user_role(user_id, role)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    admin_controller.remove_user(user_id)
    flash("User deleted.", "success")
    return redirect(url_for("admin.users"))


# ---------------- Stock Management ----------------

@admin_bp.route("/stocks")
@admin_required
def stocks():
    all_stocks = admin_controller.get_all_stocks_for_admin()
    sectors = stock_model.get_all_sectors()
    return render_template("admin/stocks.html", stocks=all_stocks, sectors=sectors)


@admin_bp.route("/stocks/add", methods=["POST"])
@admin_required
def add_stock():
    ticker = request.form.get("ticker_symbol", "")
    name = request.form.get("company_name", "")
    sector_id = request.form.get("sector_id") or None
    exchange = request.form.get("exchange", "")
    currency = request.form.get("currency", "USD")

    success, message, _data = admin_controller.add_new_stock(ticker, name, sector_id, exchange, currency)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.stocks"))


@admin_bp.route("/stocks/<int:stock_id>/edit", methods=["POST"])
@admin_required
def edit_stock(stock_id):
    name = request.form.get("company_name", "")
    sector_id = request.form.get("sector_id") or None
    exchange = request.form.get("exchange", "")
    currency = request.form.get("currency", "USD")
    is_active = request.form.get("is_active") == "1"

    admin_controller.edit_stock(stock_id, name, sector_id, exchange, currency, is_active)
    flash("Stock updated.", "success")
    return redirect(url_for("admin.stocks"))


@admin_bp.route("/stocks/<int:stock_id>/delete", methods=["POST"])
@admin_required
def delete_stock(stock_id):
    admin_controller.remove_stock(stock_id)
    flash("Stock deleted.", "success")
    return redirect(url_for("admin.stocks"))


# ---------------- Transactions & Reports ----------------

@admin_bp.route("/transactions")
@admin_required
def transactions():
    all_txns = admin_controller.get_all_transactions_for_admin()
    return render_template("admin/transactions.html", transactions=all_txns)


@admin_bp.route("/reports")
@admin_required
def reports():
    report = admin_controller.generate_summary_report()
    return render_template("admin/reports.html", report=report)


@admin_bp.route("/api/report-data")
@admin_required
def api_report_data():
    report = admin_controller.generate_summary_report()
    return jsonify({
        "txn_volume_by_day": [
            {"day": str(r["day"]), "txn_count": r["txn_count"], "volume": float(r["volume"])}
            for r in report["txn_volume_by_day"]
        ],
        "sector_distribution": [
            {"sector_name": r["sector_name"], "stock_count": r["stock_count"]}
            for r in report["sector_distribution"]
        ],
    })
