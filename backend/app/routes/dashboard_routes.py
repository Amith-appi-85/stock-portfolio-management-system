"""
app/routes/dashboard_routes.py
---------------------------------
Routes for the main user dashboard.
"""

from flask import Blueprint, render_template, session, jsonify
from app.controllers import dashboard_controller
from app.utils.decorators import login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    data = dashboard_controller.get_dashboard_data(session["user_id"])
    return render_template("dashboard/index.html", data=data)


@dashboard_bp.route("/api/chart-data")
@login_required
def chart_data():
    """JSON endpoint consumed by Chart.js on the dashboard page for the
    sector allocation pie chart and the monthly investment trend chart."""
    data = dashboard_controller.get_dashboard_data(session["user_id"])

    sector_labels = [row["sector_name"] for row in data["sector_allocation"]]
    sector_values = [float(row["sector_value"]) for row in data["sector_allocation"]]

    trend_labels = [row["month"] for row in data["monthly_trend"]]
    trend_bought = [float(row["total_bought"]) for row in data["monthly_trend"]]
    trend_sold = [float(row["total_sold"]) for row in data["monthly_trend"]]

    return jsonify({
        "sector_allocation": {"labels": sector_labels, "values": sector_values},
        "investment_trend": {
            "labels": trend_labels,
            "bought": trend_bought,
            "sold": trend_sold,
        },
    })
