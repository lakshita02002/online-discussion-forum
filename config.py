import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Use the service_role key from Supabase Settings → API (NOT the anon key).
    SUPABASE_URL         = os.environ.get("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    POSTS_PER_PAGE = 10

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"   # prevents CSRF on cross-site POST requests
    PERMANENT_SESSION_LIFETIME = 7 * 24 * 3600  # 7 days


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

