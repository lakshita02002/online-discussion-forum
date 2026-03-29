"""Flask application factory."""

import os
from datetime import datetime
from markupsafe import Markup, escape
from flask import Flask
from config import config_map
from .database import init_db, close_db


def create_app(env: str = "default") -> Flask:
    """
    Create and return a configured Flask application instance.

    Parameters
    ----------
    env : str
        One of 'development', 'testing', 'production', or 'default'.
    """
    # On Vercel the project root is read-only; instance/ lives in /tmp instead.
    if not os.environ.get("VERCEL"):
        instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "instance")
        os.makedirs(instance_path, exist_ok=True)

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_map.get(env, config_map["default"]))

    @app.template_filter("nl2br")
    def nl2br_filter(value: str) -> Markup:
        """Convert newlines to <br> tags, escaping HTML entities."""
        escaped = escape(value)
        return Markup(str(escaped).replace("\n", "<br>\n"))

    @app.template_filter("fmtdate")
    def fmtdate_filter(value: str) -> str:
        """Format a SQLite datetime string ('YYYY-MM-DD HH:MM:SS') to 'Mon DD, YYYY'.

        Falls back gracefully if the value is None or malformed.
        """
        try:
            return datetime.strptime(str(value)[:19], "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y")
        except (ValueError, TypeError):
            return str(value)[:10] if value else ""

    app.teardown_appcontext(close_db)

    from flask import session as flask_session
    from .database import query_db

    @app.before_request
    def validate_session():
        """Clear any session whose user_id no longer exists in the database.

        This prevents FOREIGN KEY constraint errors (and other confusing
        failures) that occur when the database is reset while a browser
        still holds a session cookie from the previous run.
        """
        user_id = flask_session.get("user_id")
        if user_id is not None:
            row = query_db("SELECT id FROM users WHERE id = ?", (user_id,), one=True)
            if row is None:
                flask_session.clear()

    from .auth import auth_bp
    from .posts import posts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)

    @app.cli.command("init-db")
    def init_db_command():
        """Initialise the SQLite schema. Flask CLI provides the app context automatically."""
        init_db(app)
        print("✓ Database initialised successfully.")

    with app.app_context():
        init_db(app)

    return app

