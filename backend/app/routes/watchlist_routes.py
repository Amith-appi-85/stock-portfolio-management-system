"""
app/routes/watchlist_routes.py
---------------------------------
Routes for adding/removing/viewing watchlist stocks.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.controllers import watchlist_controller
from app.models import stock_model
from app.utils.decorators import login_required

watchlist_bp = Blueprint("watchlist", __name__, url_prefix="/watchlist")


@watchlist_bp.route("/")
@login_required
def index():
    items = watchlist_controller.get_user_watchlist(session["user_id"])
    all_stocks = stock_model.get_all_stocks()
    return render_template("watchlist/index.html", items=items, all_stocks=all_stocks)


@watchlist_bp.route("/add", methods=["POST"])
@login_required
def add():
    stock_id = request.form.get("stock_id")
    success, message = watchlist_controller.add_stock_to_watchlist(session["user_id"], stock_id)
    flash(message, "success" if success else "warning")
    return redirect(url_for("watchlist.index"))


@watchlist_bp.route("/remove/<int:stock_id>", methods=["POST"])
@login_required
def remove(stock_id):
    success, message = watchlist_controller.remove_stock_from_watchlist(session["user_id"], stock_id)
    flash(message, "success" if success else "warning")
    return redirect(url_for("watchlist.index"))


@watchlist_bp.route("/api/add", methods=["POST"])
@login_required
def api_add():
    payload = request.get_json(silent=True) or {}
    success, message = watchlist_controller.add_stock_to_watchlist(session["user_id"], payload.get("stock_id"))
    return jsonify({"success": success, "message": message}), (200 if success else 400)
