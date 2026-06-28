import os

from flask import Flask, render_template
from flask_login import LoginManager, login_required
from sqlalchemy import inspect, text

from config import Config, DATABASE_DIR
from models import db
from models.user import User

from routes.auth import auth
from routes.result import result
from routes.dashboard import dashboard
from routes.admin import admin
from routes.history import history
from routes.profile import profile
from routes.leaderboard import leaderboard
from routes.hindi import hindi

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(User, int(user_id))


app.register_blueprint(auth)
app.register_blueprint(result)
app.register_blueprint(dashboard)
app.register_blueprint(admin)
app.register_blueprint(history)
app.register_blueprint(profile)
app.register_blueprint(leaderboard)
app.register_blueprint(hindi)


def init_db():

    os.makedirs(DATABASE_DIR, exist_ok=True)
    with app.app_context():
        db.create_all()

    inspector = inspect(db.engine)
    columns = [col["name"] for col in inspector.get_columns("users")]

    if "is_admin" not in columns:
        with db.engine.connect() as conn:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
            )
            conn.commit()

    if User.query.filter_by(is_admin=True).count() == 0:
        first_user = User.query.order_by(User.id.asc()).first()
        if first_user:
            first_user.is_admin = True
            db.session.commit()


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/typing")
@login_required
def typing():

    return render_template("pages/typing.html")


if __name__ == "__main__":

    with app.app_context():
        init_db()

    app.run(debug=True, port=5009)
