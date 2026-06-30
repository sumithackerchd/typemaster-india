import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

import tempfile

DATABASE_DIR = tempfile.gettempdir()

os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATABASE_DIR, "database.db")


def sqlite_uri(path):
    return "sqlite:///" + os.path.abspath(path).replace("\\", "/")


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "typemaster")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        sqlite_uri(DATABASE_PATH)
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv("MAIL_SERVER")

    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))

    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")

    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    OTP_EXPIRE_MINUTES = int(
        os.getenv("OTP_EXPIRE_MINUTES", 10)
    )