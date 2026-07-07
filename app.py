import os
import subprocess
import sys


def ensure_dependencies():
    """Install requirements automatically if packages are missing."""
    try:
        import flask  # noqa: F401
        import flask_login  # noqa: F401
        import flask_sqlalchemy  # noqa: F401
    except ImportError:
        print("Missing dependencies — installing automatically...")
        req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
        print("Dependencies installed.\n")


ensure_dependencies()

from flask import Flask
from config import Config
from extensions import db, login_manager
from models import User
from routes import admin_bp, auth_bp, resources_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        _ensure_default_admin(app)

    return app


def _ensure_default_admin(app):
    """Create a default admin account if none exists."""
    if User.query.filter_by(is_admin=True).first():
        return

    admin_username = os.environ.get("ADMIN_USERNAME", "admin")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@studyplatform.local")

    if User.query.filter_by(username=admin_username).first():
        return

    admin = User(username=admin_username, email=admin_email, is_admin=True)
    admin.set_password(admin_password)
    db.session.add(admin)
    db.session.commit()
    app.logger.info(
        "Default admin created: username=%s (change password after first login)",
        admin_username,
    )


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, host="127.0.0.1", port=8080)
