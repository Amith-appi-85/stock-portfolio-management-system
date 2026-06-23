# Deployment Instructions

This covers running the project locally for a viva/demo, and optionally
deploying it to a real server for a more polished presentation.

---

## Option A — Local Demo (Recommended for Viva)

This is the simplest and most reliable setup for a college lab demo since
it has no external dependencies beyond MySQL.

```bash
# 1. Database
mysql -u root -p < database/schema.sql
cd database && python seed.py && cd ..

# 2. Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your DB credentials

# 3. Run
python run.py
```

Open **http://127.0.0.1:5000**. That's it — no separate frontend build step
is needed because Flask serves the Bootstrap/JS templates directly via
Jinja2 + the `static/` folder.

---

## Option B — Production-style Deployment (Gunicorn + Nginx, on Linux)

Useful if you want to deploy this on a VPS (DigitalOcean, AWS EC2, etc.)
to show a live URL during your presentation.

### 1. Server prep

```bash
sudo apt update
sudo apt install python3-pip python3-venv mysql-server nginx -y
```

### 2. Clone/copy the project and set up the virtual environment

```bash
cd /var/www/stock_portfolio_system/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env   # set production DB credentials and a strong FLASK_SECRET_KEY
```

Set `FLASK_DEBUG=0` in `.env` for production.

### 3. Set up the database

```bash
mysql -u root -p < ../database/schema.sql
cd ../database && python seed.py
```

### 4. Run with Gunicorn

```bash
cd backend
gunicorn -w 4 -b 127.0.0.1:8000 run:app
```

For a persistent service, create `/etc/systemd/system/stockfolio.service`:

```ini
[Unit]
Description=Stock Portfolio Flask App
After=network.target mysql.service

[Service]
User=www-data
WorkingDirectory=/var/www/stock_portfolio_system/backend
Environment="PATH=/var/www/stock_portfolio_system/backend/venv/bin"
ExecStart=/var/www/stock_portfolio_system/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable stockfolio
sudo systemctl start stockfolio
sudo systemctl status stockfolio
```

### 5. Nginx reverse proxy

Create `/etc/nginx/sites-available/stockfolio`:

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location /static/ {
        alias /var/www/stock_portfolio_system/backend/app/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/stockfolio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Your app is now reachable at `http://your_domain_or_ip`.

(Optional) Add HTTPS with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain
```

---

## Option C — Quick Cloud Deploy (PaaS)

If you'd rather not manage a VPS, platforms like **Render**, **Railway**, or
**PythonAnywhere** can run a Flask + MySQL app with minimal config:

1. Push the project to a GitHub repository.
2. Create a new "Web Service" pointing at the `backend/` folder, with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn -w 2 -b 0.0.0.0:$PORT run:app`
3. Provision a managed MySQL instance (most PaaS providers offer one) and
   set the `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` environment
   variables in the platform's dashboard instead of a `.env` file.
4. Run `schema.sql` against the managed database (most providers give you
   a connection string you can pass to the `mysql` CLI or use their web
   SQL console).

---

## Important Production Notes (good viva talking points)

- **Never commit `.env`** — only `.env.example` should be in version control.
  Real secrets (DB password, `FLASK_SECRET_KEY`) must be set per-environment.
- **`FLASK_DEBUG` must be `0` in production** — debug mode exposes a Python
  console on error pages, which is a serious security risk.
- **yfinance rate limits**: Yahoo Finance is not an official paid API and
  can throttle frequent requests. The app caches prices for 60 seconds
  (`PRICE_CACHE_TTL_SECONDS` in `config.py`) to reduce load; for a class
  project this is sufficient, but a real production system would want a
  paid market-data provider with an SLA.
- **Database backups**: in production, schedule `mysqldump` backups:
  ```bash
  mysqldump -u root -p stock_portfolio_db > backup_$(date +%F).sql
  ```
