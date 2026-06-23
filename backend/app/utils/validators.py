"""
app/utils/validators.py
------------------------
Simple, dependency-free input validation helpers used across controllers.
Keeping validation centralized avoids duplicating regex/logic in every route.
"""

import re

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_]{3,30}$")


def is_valid_email(email: str) -> bool:
    return bool(email) and bool(EMAIL_REGEX.match(email.strip()))


def is_valid_username(username: str) -> bool:
    return bool(username) and bool(USERNAME_REGEX.match(username.strip()))


def is_valid_password(password: str) -> bool:
    """At least 6 characters. Kept simple for an academic project, but the
    check is centralized here so it's easy to strengthen later."""
    return bool(password) and len(password) >= 6


def is_positive_integer(value) -> bool:
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


def is_positive_number(value) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def is_non_empty_string(value) -> bool:
    return isinstance(value, str) and len(value.strip()) > 0


def validate_registration_form(full_name, email, username, password, confirm_password):
    """Returns (is_valid: bool, errors: list[str])"""
    errors = []
    if not is_non_empty_string(full_name):
        errors.append("Full name is required.")
    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    if not is_valid_username(username):
        errors.append("Username must be 3-30 characters (letters, numbers, underscore only).")
    if not is_valid_password(password):
        errors.append("Password must be at least 6 characters long.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    return (len(errors) == 0, errors)


def validate_trade_form(stock_id, quantity):
    errors = []
    if not is_positive_integer(stock_id):
        errors.append("Invalid stock selected.")
    if not is_positive_integer(quantity):
        errors.append("Quantity must be a positive whole number.")
    return (len(errors) == 0, errors)
