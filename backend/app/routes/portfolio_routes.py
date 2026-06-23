"""
app/routes/portfolio_routes.py
---------------------------------
Routes for viewing the portfolio and executing BUY/SELL trades.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.controllers import portfolio_controller
from app.models import stock_model
from app.utils.decorators import login_required

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/portfolio")


@portfolio_bp.route("/")
@login_required
def index():
    view = portfolio_controller.get_full_portfolio_view(session["user_id"])
    all_stocks = stock_model.get_all_stocks()
    return render_template("portfolio/index.html", view=view, all_stocks=all_stocks)


@portfolio_bp.route("/buy", methods=["POST"])
@login_required
def buy():
    stock_id = request.form.get("stock_id")
    quantity = request.form.get("quantity")

    success, message, _data = portfolio_controller.buy_stock(session["user_id"], stock_id, quantity)
    flash(message, "success" if success else "danger")
    return redirect(url_for("portfolio.index"))


@portfolio_bp.route("/sell", methods=["POST"])
@login_required
def sell():
    stock_id = request.form.get("stock_id")
    quantity = request.form.get("quantity")

    success, message, _data = portfolio_controller.sell_stock(session["user_id"], stock_id, quantity)
    flash(message, "success" if success else "danger")
    return redirect(url_for("portfolio.index"))


@portfolio_bp.route("/api/buy", methods=["POST"])
@login_required
def api_buy():
    """JSON variant used by the AJAX trade modal on the front end."""
    payload = request.get_json(silent=True) or {}
    success, message, data = portfolio_controller.buy_stock(
        session["user_id"], payload.get("stock_id"), payload.get("quantity")
    )
    return jsonify({"success": success, "message": message, "data": data}), (200 if success else 400)


@portfolio_bp.route("/api/sell", methods=["POST"])
@login_required
def api_sell():
    payload = request.get_json(silent=True) or {}
    success, message, data = portfolio_controller.sell_stock(
        session["user_id"], payload.get("stock_id"), payload.get("quantity")
    )
    return jsonify({"success": success, "message": message, "data": data}), (200 if success else 400)
