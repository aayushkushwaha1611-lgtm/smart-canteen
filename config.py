"""Application configuration for Smart Canteen.

All secrets and environment-specific values are loaded from environment
variables (optionally via a local `.env` file). No secret is hardcoded.
"""
import os
import secrets
import sys

from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, ".env"))


def _load_secret_key() -> str:
    """Resolve SECRET_KEY from the environment.

    - production: missing key is a hard error.
    - development/testing: an ephemeral random key is generated with a warning
      so the app can boot without any secret being committed to code.
    """
    key = os.environ.get("SECRET_KEY", "").strip()
    if key and key != "change-me-to-a-long-random-string":
        return key

    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        raise RuntimeError(
            "SECRET_KEY must be set to a strong random value in production. "
            "See .env.example for instructions."
        )

    generated = secrets.token_hex(32)
    print(
        "[config] WARNING: SECRET_KEY not set - generated an ephemeral key. "
        "Sessions will reset on restart. Set SECRET_KEY in .env for persistence.",
        file=sys.stderr,
    )
    return generated


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = _load_secret_key()

    _db_url = os.environ.get("DATABASE_URL", "").strip()
    if _db_url:
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
            BASEDIR, "instance", "canteen.db"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Sessions
    PERMANENT_SESSION_LIFETIME = int(
        os.environ.get("SESSION_LIFETIME_SECONDS", 60 * 60 * 24 * 7)
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 14

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASEDIR, "app", "static", "uploads", "foods")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_UPLOAD_SIZE", 5 * 1024 * 1024))
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # WTF / CSRF
    WTF_CSRF_TIME_LIMIT = 60 * 60 * 8
    WTF_CSRF_SSL_STRICT = False  # dev-friendly; proxies terminate TLS

    # Application
    CANTEEN_NAME = os.environ.get("CANTEEN_NAME", "Smart Canteen")
    ORDERS_PER_PAGE = 10
    MENU_PER_PAGE = 9
    STUDENTS_PER_PAGE = 12
    ACTIVITY_PER_PAGE = 15

    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
    SEED_DEMO_ACCOUNTS = os.environ.get("SEED_DEMO_ACCOUNTS", "1") == "1"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None) -> type[Config]:
    """Return the configuration class for the given (or current) environment."""
    name = name or os.environ.get("FLASK_ENV", "development")
    return config_by_name.get(name, DevelopmentConfig)
