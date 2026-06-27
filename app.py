from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("pages/login.html")


@app.route("/register")
def register():
    return render_template("pages/register.html")


@app.route("/dashboard")
def dashboard():
    return render_template("pages/dashboard.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5009)