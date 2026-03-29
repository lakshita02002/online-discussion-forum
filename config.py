"""Centralised configuration. Use environment variables to override secrets in production."""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Override SECRET_KEY with a strong random value in production.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Vercel's filesystem is read-only; /tmp is the only writable path.
    # Data in /tmp is ephemeral — it resets on cold starts.
    DATABASE = (
        "/tmp/forum.db"
        if os.environ.get("VERCEL")
        else os.path.join(BASE_DIR, "instance", "forum.db")
    )
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    POSTS_PER_PAGE = 10

    SESSION_COOKIE_HTTPONLY = True
    # SameSite=Lax prevents the cookie being sent on cross-site POST requests (CSRF mitigation).
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 7 * 24 * 3600  # 7 days


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    DATABASE = ":memory:"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

