from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from forms import RegisterForm, LoginForm
from models import db
from models.user import User

auth = Blueprint("auth", __name__)


# -------------------- Register --------------------

@auth.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken!", "danger")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(form.password.data)

        user = User(
            full_name=form.full_name.data,
            username=form.username.data,
            email=form.email.data,
            mobile=form.mobile.data,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("pages/register.html", form=form)


# -------------------- Login --------------------

@auth.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):

            login_user(user)

            flash("Welcome Back!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("pages/login.html", form=form)


# -------------------- Logout --------------------

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "success")

    return redirect(url_for("auth.login"))