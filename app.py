import os
import traceback

from flask import Flask, render_template, url_for
from sqlalchemy import inspect, text

from config import Config, DATABASE_DIR
from models import db
from models.user import User
from models.paragraph import Paragraph  # noqa: F401  (registers the table)
from models.custom_paragraph import CustomParagraph  # noqa: F401  (registers the table)
from models.download import Download  # noqa: F401  (registers the table)

from extensions import mail, login_manager
from flask_login import login_required
from routes.auth import auth
from routes.result import result
from routes.dashboard import dashboard
from routes.admin import admin
from routes.history import history
from routes.profile import profile
from routes.leaderboard import leaderboard
from routes.hindi import hindi
from routes.mocktest import mocktest
from routes.api import api
from routes.custom import custom
from routes.downloads import downloads
from routes.pages import pages


# -------------------------------------
# App Initialization
# -------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

mail.init_app(app)

login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.context_processor
def inject_site_globals():
    from utils.settings_store import load_settings, signature_abs_path

    sig_path = signature_abs_path()
    return {
        "site_settings": load_settings(),
        "has_signature": bool(sig_path),
        "signature_url": url_for("static", filename="images/signature.png") if sig_path else None,
    }


app.register_blueprint(auth)
app.register_blueprint(result)
app.register_blueprint(dashboard)
app.register_blueprint(admin)
app.register_blueprint(history)
app.register_blueprint(profile)
app.register_blueprint(leaderboard)
app.register_blueprint(hindi)
app.register_blueprint(mocktest)
app.register_blueprint(api)
app.register_blueprint(custom)
app.register_blueprint(downloads)
app.register_blueprint(pages)


def init_db():

    os.makedirs(DATABASE_DIR, exist_ok=True)
    with app.app_context():
        db.create_all()

    # ------------------------------------------------------------------
    # Lightweight auto-migration.
    #
    # Older databases were created before several columns existed
    # (is_admin, gamification fields, created_at, etc.). Rendering the
    # admin/dashboard pages then crashed with "no such column" errors.
    # Here we add any missing columns defined on the models so existing
    # databases keep working without a manual migration.
    # ------------------------------------------------------------------

    # column name -> SQL definition (with sensible default for existing rows)
    expected_columns = {
        "users": {
            "is_admin": "BOOLEAN DEFAULT 0 NOT NULL",
            "is_active": "BOOLEAN DEFAULT 1 NOT NULL",
            "last_login": "DATETIME",
            "xp": "INTEGER DEFAULT 0 NOT NULL",
            "level": "INTEGER DEFAULT 1 NOT NULL",
            "current_streak": "INTEGER DEFAULT 0 NOT NULL",
            "best_streak": "INTEGER DEFAULT 0 NOT NULL",
            "last_test_date": "DATE",
            "created_at": "DATETIME",
            "avatar": "VARCHAR(255)",
        },
        "results": {
            "language": "VARCHAR(20) DEFAULT 'English' NOT NULL",
            "difficulty": "VARCHAR(20) DEFAULT 'Easy' NOT NULL",
            "duration": "INTEGER DEFAULT 60 NOT NULL",
            "gross_wpm": "INTEGER DEFAULT 0",
            "net_wpm": "INTEGER DEFAULT 0",
            "cpm": "INTEGER DEFAULT 0",
            "accuracy": "FLOAT DEFAULT 0",
            "errors": "INTEGER DEFAULT 0",
            "created_at": "DATETIME",
            "certificate_id": "VARCHAR(40)",
            "verify_token": "VARCHAR(64)",
        },
    }

    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()

    with db.engine.connect() as conn:
        for table, columns in expected_columns.items():
            if table not in existing_tables:
                continue

            present = {col["name"] for col in inspector.get_columns(table)}

            for name, definition in columns.items():
                if name not in present:
                    conn.execute(
                        text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
                    )

        conn.commit()

    # Backfill created_at for any rows still missing a value.
    with db.engine.connect() as conn:
        try:
            conn.execute(
                text(
                    "UPDATE results SET created_at = CURRENT_TIMESTAMP "
                    "WHERE created_at IS NULL"
                )
            )
            conn.execute(
                text(
                    "UPDATE users SET created_at = CURRENT_TIMESTAMP "
                    "WHERE created_at IS NULL"
                )
            )
            conn.commit()
        except Exception:
            pass

    if User.query.filter_by(is_admin=True).count() == 0:
        first_user = User.query.order_by(User.id.asc()).first()
        if first_user:
            first_user.is_admin = True
            db.session.commit()

    # Seed the paragraph database (and refresh the JSON fallback mirror).
    try:
        from utils.seed_paragraphs import seed_paragraphs
        seed_paragraphs()
    except Exception:
        traceback.print_exc()


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/typing")

@login_required
def typing():

    return render_template("pages/typing.html")





from werkzeug.exceptions import HTTPException

_ERROR_COPY = {
    403: ("Access Denied", "You are not authorized."),
    404: ("Page Not Found", "The page you're looking for doesn't exist or has moved."),
    413: ("File Too Large", "The file you tried to upload is too big. Please upload a smaller file."),
    500: ("Something Went Wrong", "An unexpected error occurred. Please try again in a moment."),
}


def _render_error(code):
    title, message = _ERROR_COPY.get(code, ("Error", "Something went wrong."))
    try:
        return render_template("pages/error.html", code=code, title=title, message=message), code
    except Exception:  # noqa: BLE001 — never let the error page itself crash
        return f"{code} - {title}", code


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    # Preserve the real HTTP status code (404 stays 404, 403 stays 403, ...)
    return _render_error(e.code or 500)


@app.errorhandler(Exception)
def handle_exception(e):
    # Genuine unhandled server errors: log the traceback, show a friendly page.
    if isinstance(e, HTTPException):
        return _render_error(e.code or 500)
    traceback.print_exc()
    db.session.rollback()
    return _render_error(500)


# Render / Gunicorn startup
with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True, port=5007)
