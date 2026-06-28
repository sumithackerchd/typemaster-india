from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User
from flask_login import LoginManager, login_required

# Blueprints
from routes.auth import auth

app = Flask(__name__)
app.config.from_object(Config)

# Database
db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Register Blueprints
app.register_blueprint(auth)

# Routes
@app.route("/")
def home():
    return render_template("index.html")

# typing route
@app.route("/typing")
def typing():
    return render_template("pages/typing.html")




#dashboard route
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("pages/dashboard.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5009)