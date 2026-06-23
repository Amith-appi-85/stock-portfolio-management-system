# Testing Instructions

This document explains how to set up the project locally and verify every
feature works, in the order recommended for a viva demonstration.

> **Note:** This entire application was built and functionally tested end
> to end while creating it (real MySQL-compatible database, real Flask
> server, real HTTP requests for register/login/buy/sell/watchlist/admin).
> The steps below let you reproduce that on your own machine.

---

## 1. Prerequisites

- Python 3.10+
- MySQL 8.0+ (or MariaDB 10.6+, which is fully compatible with this schema)
- pip

## 2. Database Setup

```bash
# Log into MySQL
mysql -u root -p

# Inside the MySQL shell, run the schema file
source database/schema.sql;
exit;
```

Or directly from the terminal:

```bash
mysql -u root -p < database/schema.sql
```

This creates the `stock_portfolio_db` database, all 6 core tables, 3 views,
1 trigger, and seed data (7 sectors, 14 stocks, 1 placeholder admin user).

### Set the admin password

The schema inserts an admin user with a placeholder password hash (since
SQL can't compute a Werkzeug hash). Run the seed script to fix it:

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # or use a venv, see below
cd ../database
python seed.py
```

This sets:
- Username: `admin`
- Password: `Admin@123`

## 3. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set DB_USER / DB_PASSWORD to match your MySQL credentials
```

**Important:** If you use MySQL's default `root` account with a password,
make sure it's set up for password authentication (not `auth_socket`).
On a fresh MySQL install, create a dedicated app user instead (recommended,
mirrors real-world practice and avoids root-account issues):

```sql
CREATE USER 'stockapp'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON stock_portfolio_db.* TO 'stockapp'@'localhost';
FLUSH PRIVILEGES;
```

Then set `DB_USER=stockapp` and `DB_PASSWORD=your_password_here` in `.env`.

## 4. Run the Application

```bash
cd backend
python run.py
```

Visit **http://127.0.0.1:5000** in your browser.

---

## 5. Manual Test Checklist (Viva Walkthrough)

Work through these in order — this is exactly the flow an examiner would
expect to see demonstrated.

### A. Authentication
- [ ] Register a new account at `/auth/register` with a fresh username/email.
- [ ] Try registering again with the same username → should show a clear error.
- [ ] Try a password under 6 characters → should show a validation error.
- [ ] Log in with the new account → should land on `/dashboard/`.
- [ ] Log out → should return to the login page and block dashboard access
      if you try to navigate back (session cleared).

### B. Portfolio & Trading
- [ ] Go to **Portfolio** → click **New Trade** → buy a few shares of any stock.
- [ ] Confirm the holding appears in the table with correct average buy price.
- [ ] Buy more of the *same* stock → confirm the average buy price recalculates
      correctly (weighted average).
- [ ] Sell part of a holding → confirm quantity reduces and virtual cash balance
      increases.
- [ ] Try to sell more shares than you own → should show an error, not crash.
- [ ] Try to buy more than your virtual balance allows → should show an
      "Insufficient balance" error.

### C. Watchlist
- [ ] Go to **Watchlist** → add a stock you don't own.
- [ ] Confirm it appears with its current price.
- [ ] Try adding the same stock twice → should show "already in watchlist".
- [ ] Remove a stock from the watchlist → confirm it disappears.
- [ ] From the watchlist, click **Buy** directly → confirm the trade modal works.

### D. Stock Analysis
- [ ] Go to **Stock Analysis** → search by ticker (e.g. `AAPL`) and by company
      name (e.g. `Tesla`).
- [ ] Open a stock's detail page → confirm company info, current price, and
      52-week high/low display.
- [ ] Switch between **1M / 6M / 1Y** chart buttons → confirm the price chart
      reloads with different data ranges.
  > If you're on a restricted network (e.g. a college lab proxy/firewall
  > blocking `finance.yahoo.com`), the chart may show "data unavailable" —
  > this is expected; the app gracefully falls back to the last known DB
  > price everywhere else (buy/sell still work).
- [ ] Visit **Sector Analysis** → confirm stocks are grouped correctly by
      sector with a bar chart of counts.

### E. Dashboard
- [ ] Confirm Total Investment, Current Value, Profit/Loss, and Virtual Cash
      stat cards match what you'd expect from your trades.
- [ ] Confirm the **Top Performing** and **Worst Performing** stock cards
      show the correct holdings once you own 2+ stocks with different
      performance.
- [ ] Confirm the sector allocation pie chart and monthly investment trend
      chart render (Chart.js, fed via `/dashboard/api/chart-data`).

### F. Admin Panel
- [ ] Log out, log back in as `admin` / `Admin@123`.
- [ ] Confirm you're redirected to `/admin/` (not the regular user dashboard).
- [ ] **Manage Users**: disable a user, re-enable them, promote a user to
      admin and back, delete a test user.
- [ ] **Manage Stocks**: add a new stock by ticker (e.g. `MSFT` if not already
      present, or a new one like `IBM`) — confirm it validates against live
      yfinance data before saving. Edit a stock's sector/exchange. Delete a
      stock that has no holdings.
- [ ] **Transactions**: confirm every BUY/SELL across all users appears here.
- [ ] **Reports**: confirm the daily transaction volume chart and sector
      distribution chart render with real data.

### G. Authorization / Security Checks
- [ ] While logged out, try to directly visit `/dashboard/`, `/portfolio/`,
      or `/admin/` in the URL bar → should redirect to login, not show data.
- [ ] While logged in as a normal user, try to visit `/admin/` directly →
      should redirect back to the user dashboard with a permission warning.

---

## 6. Database-Level Verification (for viva DB questions)

You can demonstrate live DB behavior directly in the MySQL shell:

```sql
-- Show the trigger fires on every transaction
SELECT * FROM audit_log ORDER BY log_id DESC LIMIT 5;

-- Show the portfolio view computing profit/loss correctly
SELECT * FROM vw_portfolio_summary WHERE user_id = 1;

-- Show foreign key constraints are enforced
SHOW CREATE TABLE portfolio;

-- Try violating a constraint on purpose (should fail):
INSERT INTO portfolio (user_id, stock_id, quantity) VALUES (9999, 1, 10);
-- ERROR 1452: Cannot add or update a child row: a foreign key constraint fails
```

## 7. Automated Smoke Test (optional, for your own confidence)

A simple way to sanity-check the backend without a browser:

```bash
# After starting the Flask server in one terminal, in another:
curl -i http://127.0.0.1:5000/auth/login
# Expect: HTTP/1.1 200 OK

curl -i -X POST http://127.0.0.1:5000/auth/register \
  -d "full_name=Demo User" -d "email=demo@test.com" \
  -d "username=demouser" -d "password=Demo@123" -d "confirm_password=Demo@123"
# Expect: HTTP/1.1 302 FOUND (redirect to login on success)
```
