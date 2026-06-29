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