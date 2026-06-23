"""
app/controllers/dashboard_controller.py
-------------------------------------------
Aggregates everything the dashboard page needs in one place: totals,
best/worst performer, sector allocation (for pie chart), and the monthly
investment trend (for line chart).
"""

from app.models import portfolio_model, transaction_model, user_model


def get_dashboard_data(user_id):
    totals = portfolio_model.get_user_dashboard_totals(user_id)
    best, worst = portfolio_model.get_best_and_worst_performers(user_id)
    sector_allocation = portfolio_model.get_sector_allocation(user_id)
    monthly_trend = transaction_model.get_monthly_investment_trend(user_id)
    balance = user_model.get_user_balance(user_id)

    total_investment = float(totals.get("total_investment") or 0)
    current_value = float(totals.get("current_value") or 0)
    total_profit_loss = float(totals.get("total_profit_loss") or 0)
    profit_loss_percent = (
        round((total_profit_loss / total_investment) * 100, 2) if total_investment > 0 else 0
    )

    return {
        "total_investment": total_investment,
        "current_value": current_value,
        "total_profit_loss": total_profit_loss,
        "profit_loss_percent": profit_loss_percent,
        "virtual_balance": balance,
        "best_performer": best,
        "worst_performer": worst,
        "sector_allocation": sector_allocation,
        "monthly_trend": monthly_trend,
    }
