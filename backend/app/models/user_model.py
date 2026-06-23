"""
app/models/user_model.py
--------------------------
Data-access functions for the `users` table. Each function maps directly to
a CRUD operation. Kept as plain functions (not a heavy ORM class) so the
raw SQL is transparent and easy to explain in a DBMS viva.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import query_db, execute_db


def create_user(full_name, email, username, password, virtual_balance=1000000.00):
    password_hash = generate_password_hash(password)
    user_id = execute_db(
        """INSERT INTO users (full_name, email, username, password_hash, role, virtual_balance)
           VALUES (%s, %s, %s, %s, 'user', %s)""",
        (full_name, email, username, password_hash, virtual_balance),
        return_lastrowid=True,
    )
    return user_id


def get_user_by_username(username):
    return query_db("SELECT * FROM users WHERE username = %s", (username,), one=True)


def get_user_by_email(email):
    return query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)


def get_user_by_id(user_id):
    return query_db("SELECT * FROM users WHERE user_id = %s", (user_id,), one=True)


def username_or_email_exists(username, email):
    return query_db(
        "SELECT user_id FROM users WHERE username = %s OR email = %s",
        (username, email),
        one=True,
    )


def verify_password(plain_password, password_hash):
    return check_password_hash(password_hash, plain_password)


def get_all_users():
    return query_db(
        """SELECT user_id, full_name, email, username, role, virtual_balance,
                  is_active, created_at
           FROM users ORDER BY created_at DESC"""
    )


def set_user_active_status(user_id, is_active):
    return execute_db("UPDATE users SET is_active = %s WHERE user_id = %s", (is_active, user_id))


def update_user_role(user_id, role):
    return execute_db("UPDATE users SET role = %s WHERE user_id = %s", (role, user_id))


def delete_user(user_id):
    return execute_db("DELETE FROM users WHERE user_id = %s", (user_id,))


def get_user_balance(user_id):
    row = query_db("SELECT virtual_balance FROM users WHERE user_id = %s", (user_id,), one=True)
    return float(row["virtual_balance"]) if row else 0.0


def adjust_user_balance(user_id, delta):
    """delta can be positive (credit, e.g. after a sell) or negative (debit, after a buy)."""
    return execute_db(
        "UPDATE users SET virtual_balance = virtual_balance + %s WHERE user_id = %s",
        (delta, user_id),
    )


def count_users():
    row = query_db("SELECT COUNT(*) AS cnt FROM users", one=True)
    return row["cnt"] if row else 0
