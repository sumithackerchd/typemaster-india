from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from forms import RegisterForm, LoginForm
from models import db
from sqlalchemy import or_
from models.user import User
from utils.otp import generate_otp
from utils.email_service import send_otp_email


from flask import session
from datetime import datetime, timedelta

from utils.otp import generate_otp
from utils.email_service import send_otp_email

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

        is_first_user = User.query.count() == 0

        user = User(
            full_name=form.full_name.data,
            username=form.username.data,
            email=form.email.data,
            mobile=form.mobile.data,
            password=hashed_password,
            is_admin=is_first_user
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

        login_value = form.email.data.strip()

        user = User.query.filter(
        or_(
        User.email == login_value,
        User.username == login_value,
        User.mobile == login_value
    )).first()

        if user and check_password_hash(user.password, form.password.data):

            login_user(user)

            

            return redirect(url_for("dashboard.dashboard_page"))

        flash("Invalid email or password.", "danger")

    return render_template("pages/login.html", form=form)


# -------------------- Logout --------------------

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "info")

    return redirect(url_for("auth.login"))





# 
@auth.route("/test-otp")
def test_otp():

    otp = generate_otp()

    send_otp_email(
        "sumitgiri.chandausi@gmail.com",
        otp
    )

    return f"OTP Sent : {otp}"

# -------------------- Forgot Password --------------------

@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email").strip().lower()

        user = User.query.filter_by(email=email).first()

        if not user:

            flash("No account found with this email.", "danger")
            return redirect(url_for("auth.forgot_password"))

        otp = generate_otp()

        session["reset_email"] = email
        session["reset_otp"] = otp
        session["otp_expiry"] = (
            datetime.utcnow() + timedelta(minutes=10)
        ).isoformat()

        send_otp_email(email, otp)

        flash("OTP has been sent to your email.", "success")

        return redirect(url_for("auth.verify_otp"))

    return render_template("pages/forgot_password.html")

@auth.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        user_otp = request.form.get("otp").strip()

        saved_otp = session.get("reset_otp")

        expiry = session.get("otp_expiry")

        if not saved_otp:

            flash("OTP expired. Please request a new one.", "danger")
            return redirect(url_for("auth.forgot_password"))

        if datetime.utcnow() > datetime.fromisoformat(expiry):

            session.clear()

            flash("OTP has expired.", "danger")

            return redirect(url_for("auth.forgot_password"))

        if user_otp != saved_otp:

            flash("Invalid OTP.", "danger")

            return redirect(url_for("auth.verify_otp"))

        flash("OTP Verified Successfully.", "success")

        return redirect(url_for("auth.reset_password"))

    return render_template("pages/verify_otp.html")

@auth.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    email = session.get("reset_email")

    if not email:

        flash("Session expired. Please try again.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":

        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:

            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.reset_password"))

        user = User.query.filter_by(email=email).first()

        if not user:

            flash("User not found.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user.password = generate_password_hash(password)

        db.session.commit()

        session.pop("reset_email", None)
        session.pop("reset_otp", None)
        session.pop("otp_expiry", None)

        flash("Password updated successfully. Please login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("pages/reset_password.html")