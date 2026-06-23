"""
app/__init__.py
------------------
Flask application factory. Registers config, the database teardown hook,
all blueprints, and a couple of global error handlers / template filters.
"""

from flask import Flask, render_template, session, redirect, url_for
from config import Config
from app.utils import db as db_utils
from flask import session
from app.models import user_model


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database connection teardown hook
    db_utils.init_app(app)

    # ---------------- Register Blueprints ----------------
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.portfolio_routes import portfolio_bp
    from app.routes.watchlist_routes import watchlist_bp
    from app.routes.analysis_routes import analysis_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(watchlist_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(admin_bp)

    # ---------------- Root route ----------------
    @app.route("/")
    def home():
        if "user_id" in session:
            if session.get("role") == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("dashboard.index"))
        return redirect(url_for("auth.login"))

    # ---------------- Template filters ----------------
    @app.template_filter("currency")
    def currency_filter(value):
        try:
            return f"{float(value):,.2f}"
        except (TypeError, ValueError):
            return value

    # ---------------- Error handlers ----------------
    @app.errorhandler(404)
    def not_found(_e):
        return render_template("partials/error.html", code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("partials/error.html", code=500, message="Internal server error"), 500
    

        # ---------------- Error handlers ----------------
    @app.errorhandler(404)
    def not_found(_e):
        return render_template("partials/error.html", code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("partials/error.html", code=500, message="Internal server error"), 500

    # ---------------- Global template variables ----------------
    @app.context_processor
    def inject_balance():

        if "user_id" in session:
            balance = user_model.get_user_balance(session["user_id"])
        else:
            balance = 0

        return {
            "g_virtual_balance": balance
        }

    return app

    return app
