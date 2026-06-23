"""
app/utils/decorators.py
-------------------------
Route-protection decorators built on top of Flask's session object.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request


def login_required(view_func):
    """Redirects to login page (or returns 401 JSON for API calls) if the
    user does not have an active session."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Authentication required."}), 401
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapped


def admin_required(view_func):
    """Allows access only if the logged-in user has role == 'admin'."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("dashboard.index"))
        return view_func(*args, **kwargs)
    return wrapped
