"""
app/utils/db.py
----------------
Centralized MySQL connection handling using mysql-connector-python.

Design notes for viva:
- We use a fresh connection per request (get_db / close_db hooked into
  Flask's `g` application context) rather than a long-lived global
  connection, which avoids stale-connection bugs and is the standard
  Flask pattern.
- `query_db` / `execute_db` are small helper wrappers so route/controller
  code doesn't repeat boilerplate cursor handling everywhere.
"""

import mysql.connector
from mysql.connector import Error
from flask import g, current_app


def get_db():
    """Return a MySQL connection stored on Flask's application context `g`,
    creating one if it doesn't exist yet for this request."""
    if "db" not in g:
        cfg = current_app.config
        g.db = mysql.connector.connect(
            host=cfg["DB_HOST"],
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            port=cfg["DB_PORT"],
            autocommit=False,
        )
    return g.db


def close_db(e=None):
    """Close the DB connection at the end of the request, if one was opened."""
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()


def query_db(query, args=(), one=False, dictionary=True):
    """Run a SELECT query and return rows (list of dicts by default)."""
    conn = get_db()
    cursor = conn.cursor(dictionary=dictionary)
    try:
        cursor.execute(query, args)
        rows = cursor.fetchall()
        return (rows[0] if rows else None) if one else rows
    finally:
        cursor.close()


def execute_db(query, args=(), return_lastrowid=False):
    """Run an INSERT/UPDATE/DELETE statement, commit, and optionally return
    the last inserted row id. Rolls back on error."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        conn.commit()
        last_id = cursor.lastrowid
        return last_id if return_lastrowid else cursor.rowcount
    except Error:
        conn.rollback()
        raise
    finally:
        cursor.close()


def init_app(app):
    """Register the close_db function to run automatically after every
    request/app context teardown."""
    app.teardown_appcontext(close_db)
