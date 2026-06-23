"""
app/routes/analysis_routes.py
---------------------------------
Routes for stock search, company analysis page, chart data API, and
sector analysis.
"""

from flask import Blueprint, render_template, request, jsonify
from app.controllers import analysis_controller
from app.utils.decorators import login_required

analysis_bp = Blueprint("analysis", __name__, url_prefix="/analysis")


@analysis_bp.route("/")
@login_required
def index():
    search_term = request.args.get("q", "").strip()
    results = analysis_controller.search_for_stocks(search_term) if search_term else []
    return render_template("analysis/index.html", results=results, search_term=search_term)


@analysis_bp.route("/stock/<int:stock_id>")
@login_required
def stock_detail(stock_id):
    analysis = analysis_controller.get_stock_analysis(stock_id)
    if not analysis:
        return render_template("analysis/not_found.html"), 404
    return render_template("analysis/stock_detail.html", analysis=analysis)


@analysis_bp.route("/api/search")
@login_required
def api_search():
    search_term = request.args.get("q", "").strip()
    results = analysis_controller.search_for_stocks(search_term) if search_term else []
    return jsonify({"results": results})


@analysis_bp.route("/api/chart/<ticker_symbol>")
@login_required
def api_chart(ticker_symbol):
    period_key = request.args.get("period", "1m")
    data = analysis_controller.get_chart_data(ticker_symbol, period_key)
    return jsonify(data)


@analysis_bp.route("/sectors")
@login_required
def sectors():
    data = analysis_controller.get_sector_analysis()
    return render_template("analysis/sectors.html", data=data)
