from datetime import datetime
from markupsafe import Markup, escape
from flask import Flask
from config import config_map


def create_app(env: str = "default") -> Flask:
    """Create and return a Flask app. env: 'development', 'testing', or 'production'."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_map.get(env, config_map["default"]))

    @app.template_filter("nl2br")
    def nl2br_filter(value: str) -> Markup:
        """Convert newlines to <br> tags, escaping HTML entities."""
        escaped = escape(value)
        return Markup(str(escaped).replace("\n", "<br>\n"))

    @app.template_filter("fmtdate")
    def fmtdate_filter(value: str) -> str:
        """Format an ISO datetime string to 'Mon DD, YYYY'. Falls back gracefully."""
        try:
            return datetime.strptime(str(value)[:19], "%Y-%m-%dT%H:%M:%S").strftime("%b %d, %Y")
        except (ValueError, TypeError):
            try:
                return datetime.strptime(str(value)[:19], "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y")
            except (ValueError, TypeError):
                return str(value)[:10] if value else ""

    from .auth import auth_bp
    from .posts import posts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)

    return app

