"""
config.py
---------
Central configuration for the Flask application. Reads from environment
variables (loaded via .env in development) so secrets never live in code.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from a .env file into os.environ if present


class Config:
    # Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev_insecure_key_change_me")
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    # Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 8  # 8 hours

    # MySQL Database
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_NAME = os.environ.get("DB_NAME", "stock_portfolio_db")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))

    # App-specific
    DEFAULT_VIRTUAL_BALANCE = float(os.environ.get("DEFAULT_VIRTUAL_BALANCE", 1000000.00))

    # yfinance / stock data caching (seconds) to avoid hammering the API
    PRICE_CACHE_TTL_SECONDS = 60
