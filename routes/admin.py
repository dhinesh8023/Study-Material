import os

from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Resource, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("resources.browse"))
        return f(*args, **kwargs)

    return decorated


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    resources = Resource.query.order_by(Resource.created_at.desc()).all()
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template(
        "admin/dashboard.html", resources=resources, users=users
    )


@admin_bp.route("/delete/<int:resource_id>", methods=["POST"])
@login_required
@admin_required
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)

    if resource.file_path:
        file_full_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], resource.file_path
        )
        if os.path.exists(file_full_path):
            os.remove(file_full_path)

    db.session.delete(resource)
    db.session.commit()
    flash(f'Resource "{resource.title}" removed.', "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/toggle-admin/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot change your own admin status.", "warning")
        return redirect(url_for("admin.dashboard"))

    user.is_admin = not user.is_admin
    db.session.commit()
    status = "granted" if user.is_admin else "revoked"
    flash(f"Admin access {status} for {user.username}.", "success")
    return redirect(url_for("admin.dashboard"))
