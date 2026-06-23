"""
seed.py
--------
Run this ONCE after creating the database with schema.sql, to:
1. Replace the placeholder admin password hash with a real Werkzeug hash.
2. (Optionally) verify the seed stock/sector data loaded correctly.

Usage:
    cd database
    python seed.py

Requires: backend virtualenv activated (needs mysql-connector-python, werkzeug)
"""

import sys
import os
import mysql.connector
from werkzeug.security import generate_password_hash

# Add backend to path so we can reuse config if desired
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "your_mysql_password"),
    "database": os.environ.get("DB_NAME", "stock_portfolio_db"),
}

ADMIN_USERNAME = "admin"
ADMIN_PLAINTEXT_PASSWORD = "Admin@123"   # change after first login in production


def main():
    print("Connecting to MySQL...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    hashed = generate_password_hash(ADMIN_PLAINTEXT_PASSWORD)

    cursor.execute(
        "UPDATE users SET password_hash = %s WHERE username = %s",
        (hashed, ADMIN_USERNAME),
    )
    conn.commit()
    print(f"Admin password set. Login with username='{ADMIN_USERNAME}', "
          f"password='{ADMIN_PLAINTEXT_PASSWORD}'")

    cursor.execute("SELECT COUNT(*) FROM stocks")
    stock_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM sectors")
    sector_count = cursor.fetchone()[0]
    print(f"Stocks seeded: {stock_count}")
    print(f"Sectors seeded: {sector_count}")

    cursor.close()
    conn.close()
    print("Seed complete.")


if __name__ == "__main__":
    main()
