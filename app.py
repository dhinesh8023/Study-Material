import os

from flask import Flask
from config import Config
from extensions import db, login_manager
from models import User
from routes import admin_bp, auth_bp, resources_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Create upload folder
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(admin_bp)

    # Create database and default admin
    with app.app_context():
        db.create_all()
        _ensure_default_admin(app)

    return app


def _ensure_default_admin(app):
    """Create a default admin account if one does not exist."""

    if User.query.filter_by(is_admin=True).first():
        return

    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    admin_email = os.environ.get(
        "ADMIN_EMAIL",
        "admin@studyplatform.local"
    )

    if User.query.filter_by(username=admin_username).first():
        return

    admin = User(
        username=admin_username,
        email=admin_email,
        is_admin=True
    )

    admin.set_password(admin_password)

    db.session.add(admin)
    db.session.commit()

    app.logger.info(
        "Default admin created: %s",
        admin_username
    )


# ==================================================
# IMPORTANT FOR VERCEL
# ==================================================
app = create_app()


# ==================================================
# LOCAL DEVELOPMENT
# ==================================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )