"""
Application configuration.

Secrets and environment-specific values are read from environment variables
(loaded from a local `.env` file in development via python-dotenv). Nothing
sensitive is hard-coded here — see `.env.example` for the full list of
variables and copy it to `.env` to configure a local instance.
"""

import os
import secrets
import tempfile

from dotenv import load_dotenv

# Load variables from a local .env file if present. This is a no-op in
# production if the file does not exist (real env vars take precedence).
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _env_bool(name, default=False):
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


# -------------------------------------------------------------------
# Environment detection
# -------------------------------------------------------------------
# APP_ENV=production enables the hardened production profile.
APP_ENV = os.getenv("APP_ENV", os.getenv("FLASK_ENV", "development")).lower()
IS_PRODUCTION = APP_ENV == "production"


# -------------------------------------------------------------------
# Database location
# -------------------------------------------------------------------
# In production, persist SQLite in an `instance/` directory that survives
# restarts (or, preferably, point DATABASE_URL at a managed database).
# In development we fall back to the OS temp dir for convenience.
def sqlite_uri(path):
    return "sqlite:///" + os.path.abspath(path).replace("\\", "/")


if os.getenv("DATABASE_URL"):
    DATABASE_DIR = None
    DATABASE_PATH = None
else:
    if IS_PRODUCTION:
        DATABASE_DIR = os.getenv("DATABASE_DIR", os.path.join(BASE_DIR, "instance"))
    else:
        DATABASE_DIR = os.getenv("DATABASE_DIR", tempfile.gettempdir())
    os.makedirs(DATABASE_DIR, exist_ok=True)
    DATABASE_PATH = os.path.join(DATABASE_DIR, "database.db")


# -------------------------------------------------------------------
# Secret key
# -------------------------------------------------------------------
# A stable SECRET_KEY is required to keep sessions valid across restarts.
# In production it MUST be provided via the environment; we refuse the weak
# built-in default. In development we generate an ephemeral one if missing.
def _resolve_secret_key():
    key = os.getenv("SECRET_KEY")
    if key and key != "typemaster":
        return key
    if IS_PRODUCTION:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set (or is the insecure "
            "default). Generate a strong value, e.g.:\n"
            "    python -c \"import secrets; print(secrets.token_hex(32))\"\n"
            "and set it in the environment before starting in production."
        )
    # Development-only ephemeral key.
    return secrets.token_hex(32)


class Config:
    # --- Core ---
    SECRET_KEY = _resolve_secret_key()

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or sqlite_uri(DATABASE_PATH)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Session / cookie security ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Only send cookies over HTTPS in production.
    SESSION_COOKIE_SECURE = IS_PRODUCTION
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = IS_PRODUCTION
    PERMANENT_SESSION_LIFETIME = int(os.getenv("SESSION_LIFETIME_SECONDS", 60 * 60 * 24 * 7))

    # --- Uploads ---
    # Cap request bodies (OCR images / imports) to a sane size (default 16 MB).
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

    # --- Mail / OTP ---
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = _env_bool("MAIL_USE_TLS", True)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", os.getenv("MAIL_USERNAME"))

    OTP_EXPIRE_MINUTES = int(os.getenv("OTP_EXPIRE_MINUTES", 10))

    # Convenience flag for templates / app code.
    IS_PRODUCTION = IS_PRODUCTION
