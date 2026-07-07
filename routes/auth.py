import os

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import desc

from extensions import db
from models import Resource, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("resources.browse"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
        elif User.query.filter_by(username=username).first():
            flash("Username already taken.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("resources.browse"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page or url_for("resources.browse"))

        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("resources.browse"))


@auth_bp.route("/profile")
@login_required
def profile():
    user_resources = (
        Resource.query.filter_by(user_id=current_user.id)
        .order_by(desc(Resource.created_at))
        .all()
    )
    return render_template("auth/profile.html", user_resources=user_resources)


@auth_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")

        if not email:
            flash("Email is required.", "danger")
        elif email != current_user.email and User.query.filter_by(email=email).first():
            flash("Email already in use.", "danger")
        elif new_password and not current_user.check_password(current_password):
            flash("Current password is incorrect.", "danger")
        elif new_password and len(new_password) < 6:
            flash("New password must be at least 6 characters.", "danger")
        else:
            current_user.email = email
            if new_password:
                current_user.set_password(new_password)
            db.session.commit()
            flash("Profile updated successfully.", "success")
            return redirect(url_for("auth.profile"))

    return render_template("auth/edit_profile.html")
