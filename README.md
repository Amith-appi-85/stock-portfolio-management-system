# Stock Market Portfolio & Analysis System

A full-stack **DBMS mini-project** simulating a virtual stock trading
platform: users register, get virtual cash, buy/sell real stocks at live
market prices, track a watchlist, analyze companies with historical charts,
and admins manage the whole platform.

Built for a 3rd-year Computer Science DBMS course — designed to be clear,
well-normalized, and easy to explain in a viva.

> ✅ **This project has been functionally tested end-to-end**: the schema
> was executed against a real MySQL-compatible server, and every major
> flow (register → login → buy → sell → watchlist → stock analysis →
> dashboard → admin panel → logout, plus auth/authorization edge cases)
> was verified over real HTTP requests during development. See
> `docs/testing_instructions.md` to reproduce this yourself.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5, vanilla JavaScript |
| Backend | Python 3, Flask (Blueprints, MVC-style layout) |
| Database | MySQL 8 (or MariaDB 10.6+) |
| Charts | Chart.js |
| Live Market Data | yfinance (Yahoo Finance) |

---

## Project Structure

```
stock_portfolio_system/
├── database/
│   ├── schema.sql              # Full DDL: tables, views, trigger, seed data
│   └── seed.py                 # Sets the real admin password hash
│
├── backend/
│   ├── run.py                  # App entry point
│   ├── config.py                # Central configuration (.env driven)
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── __init__.py          # Flask app factory + blueprint registration
│       ├── models/              # Data-access layer (raw parameterized SQL)
│       │   ├── user_model.py
│       │   ├── stock_model.py
│       │   ├── portfolio_model.py
│       │   ├── transaction_model.py
│       │   └── watchlist_model.py
│       ├── controllers/         # Business logic layer
│       │   ├── auth_controller.py
│       │   ├── portfolio_controller.py
│       │   ├── watchlist_controller.py
│       │   ├── analysis_controller.py
│       │   ├── admin_controller.py
│       │   └── dashboard_controller.py
│       ├── routes/               # Flask Blueprints (HTTP layer)
│       │   ├── auth_routes.py
│       │   ├── dashboard_routes.py
│       │   ├── portfolio_routes.py
│       │   ├── watchlist_routes.py
│       │   ├── analysis_routes.py
│       │   └── admin_routes.py
│       ├── utils/
│       │   ├── db.py                    # MySQL connection handling
│       │   ├── validators.py            # Input validation helpers
│       │   ├── decorators.py            # @login_required / @admin_required
│       │   └── stock_data_service.py    # yfinance wrapper + caching
│       ├── templates/            # Jinja2 + Bootstrap UI
│       │   ├── base.html
│       │   ├── partials/
│       │   ├── auth/
│       │   ├── dashboard/
│       │   ├── portfolio/
│       │   ├── watchlist/
│       │   ├── analysis/
│       │   └── admin/
│       └── static/
│           ├── css/style.css
│           └── js/ (main.js, charts.js, trading.js)
│
└── docs/
    ├── er_diagram.md                 # Mermaid ER diagram
    ├── normalization.md              # 1NF/2NF/3NF explanation
    ├── testing_instructions.md
    └── deployment_instructions.md
```

This follows a clean **Model → Controller → Route** separation:
- **Models** talk to the database only (raw SQL, no business rules).
- **Controllers** hold business logic (validation, trade calculations,
  balance checks) and call models.
- **Routes** handle HTTP only (parse request, call controller, render
  template or return JSON).

---

## Features

### 1. User Authentication
Registration, login, logout, and server-side session management
(Flask `session`, Werkzeug password hashing — passwords are never stored
in plaintext).

### 2. Portfolio Management (Virtual Trading)
- Buy/sell stocks at the **live current price** (fetched via yfinance,
  with automatic fallback to the last cached DB price if the API is
  unreachable, so the app stays usable even on restricted networks).
- Weighted-average buy price recalculated automatically on repeated buys.
- Virtual cash balance debited/credited on every trade.
- Total investment, current value, and profit/loss computed via a SQL view.

### 3. Watchlist
Add/remove/view stocks you're tracking without owning them.

### 4. Stock Analysis
Search by ticker or company name, view company info (sector, market cap,
P/E ratio, 52-week range, business summary), and 1-month / 6-month /
1-year historical price charts. Plus a dedicated sector-analysis view.

### 5. Dashboard
Total investment, current value, profit/loss, best/worst performing stock,
a sector-allocation pie chart, and a monthly investment-trend bar chart —
all powered by Chart.js consuming a JSON API endpoint.

### 6. Admin Panel
Manage users (enable/disable, promote/demote, delete), manage stocks
(add — validated live against yfinance — edit, delete), view every
transaction across all users, and generate aggregate reports with charts.

---

## Database Design Highlights

- **6 core tables**: `users`, `sectors`, `stocks`, `portfolio`,
  `transactions`, `watchlist` (+ `audit_log` for trigger demonstration).
- **3 SQL views** (`vw_portfolio_summary`, `vw_user_dashboard`,
  `vw_sector_allocation`) so complex profit/loss math lives in the
  database layer, not duplicated across Python code.
- **1 trigger** (`trg_after_transaction_insert`) auto-logs every trade to
  an audit table — a clean, demonstrable example of DB-level automation.
- **Normalized to 3NF** — see `docs/normalization.md` for the full
  explanation with functional dependencies, written specifically for
  viva questions.
- **8 foreign key relationships**, all with explicit `ON DELETE`/`ON UPDATE`
  behavior (e.g. deleting a user cascades to their portfolio/transactions/
  watchlist; deleting a sector sets `stocks.sector_id` to `NULL` rather
  than failing).

See `docs/er_diagram.md` for the full Mermaid ER diagram.

---

## Quick Start

```bash
# 1. Database
mysql -u root -p < database/schema.sql
cd database && python seed.py && cd ..

# 2. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit DB_USER / DB_PASSWORD

# 3. Run
python run.py
```

Visit **http://127.0.0.1:5000** — login with `admin` / `Admin@123` for the
admin panel, or register a new account for the regular user experience.

Full setup, testing checklist, and deployment options are in `docs/`.

---

## Default Virtual Balance

Every new user starts with **₹1,000,000** in virtual cash
(`DEFAULT_VIRTUAL_BALANCE` in `.env`) — enough to practice meaningful
portfolio diversification across the 14 seeded stocks spanning 7 sectors.
