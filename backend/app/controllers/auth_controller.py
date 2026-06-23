"""
app/controllers/auth_controller.py
-------------------------------------
Business logic for registration, login, and logout. Routes call into these
functions; they return (success: bool, message: str, data: dict|None)
so the route layer can decide how to render the response (HTML flash vs
JSON for API consumers).
"""

from flask import current_app
from app.models import user_model
from app.utils.validators import validate_registration_form, is_valid_username, is_valid_password


def register_user(full_name, email, username, password, confirm_password):
    is_valid, errors = validate_registration_form(full_name, email, username, password, confirm_password)
    if not is_valid:
        return False, " ".join(errors), None

    if user_model.username_or_email_exists(username, email):
        return False, "An account with this username or email already exists.", None

    starting_balance = current_app.config["DEFAULT_VIRTUAL_BALANCE"]
    user_id = user_model.create_user(full_name, email, username, password, starting_balance)
    return True, "Registration successful! You can now log in.", {"user_id": user_id}


def authenticate_user(username, password):
    if not username or not password:
        return False, "Username and password are required.", None

    user = user_model.get_user_by_username(username)
    if not user:
        return False, "Invalid username or password.", None

    if not user["is_active"]:
        return False, "Your account has been disabled. Contact the administrator.", None

    if not user_model.verify_password(password, user["password_hash"]):
        return False, "Invalid username or password.", None

    return True, "Login successful.", user
