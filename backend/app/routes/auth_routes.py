"""
app/routes/auth_routes.py
----------------------------
Routes for registration, login, and logout.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.controllers import auth_controller

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        success, message, _data = auth_controller.register_user(
            full_name, email, username, password, confirm_password
        )
        flash(message, "success" if success else "danger")
        if success:
            return redirect(url_for("auth.login"))
        return render_template("auth/register.html", form_data=request.form)

    return render_template("auth/register.html", form_data={})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        success, message, user = auth_controller.authenticate_user(username, password)
        if success:
            session.permanent = True
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['full_name']}!", "success")
            if user["role"] == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("dashboard.index"))

        flash(message, "danger")
        return render_template("auth/login.html")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
