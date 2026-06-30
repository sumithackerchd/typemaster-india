import os
import re
import time

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import db
from models.user import User
from models.result import Result

profile = Blueprint("profile", __name__)

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
AVATAR_DIR = os.path.join(BASE_DIR, "static", "uploads", "avatars")
ALLOWED_AVATAR = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _stats():
    total_tests = Result.query.filter_by(user_id=current_user.id).count()

    best_wpm = (
        db.session.query(func.max(Result.net_wpm))
        .filter_by(user_id=current_user.id)
        .scalar()
    ) or 0

    avg_accuracy = (
        db.session.query(func.avg(Result.accuracy))
        .filter_by(user_id=current_user.id)
        .scalar()
    ) or 0

    return total_tests, best_wpm, round(avg_accuracy, 1)


@profile.route("/profile")
@login_required
def profile_page():
    total_tests, best_wpm, avg_accuracy = _stats()

    return render_template(
        "pages/profile.html",
        total_tests=total_tests,
        best_wpm=best_wpm,
        avg_accuracy=avg_accuracy,
    )


@profile.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    full_name = (request.form.get("full_name") or "").strip()
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    mobile = (request.form.get("mobile") or "").strip()

    if not full_name or not username or not email:
        flash("Name, username and email are required.", "danger")
        return redirect(url_for("profile.profile_page"))

    if not EMAIL_RE.match(email):
        flash("Please enter a valid email address.", "danger")
        return redirect(url_for("profile.profile_page"))

    if mobile and not re.match(r"^\d{7,15}$", mobile):
        flash("Mobile number must be 7-15 digits.", "danger")
        return redirect(url_for("profile.profile_page"))

    # Uniqueness checks (excluding the current user).
    clash = (
        User.query.filter(User.username == username, User.id != current_user.id)
        .first()
    )
    if clash:
        flash("That username is already taken.", "danger")
        return redirect(url_for("profile.profile_page"))

    clash = (
        User.query.filter(User.email == email, User.id != current_user.id).first()
    )
    if clash:
        flash("That email is already in use.", "danger")
        return redirect(url_for("profile.profile_page"))

    current_user.full_name = full_name
    current_user.username = username
    current_user.email = email
    current_user.mobile = mobile or current_user.mobile

    db.session.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile.profile_page"))


@profile.route("/profile/password", methods=["POST"])
@login_required
def change_password():
    current = request.form.get("current_password") or ""
    new = request.form.get("new_password") or ""
    confirm = request.form.get("confirm_password") or ""

    if not check_password_hash(current_user.password, current):
        flash("Your current password is incorrect.", "danger")
        return redirect(url_for("profile.profile_page"))

    if len(new) < 6:
        flash("New password must be at least 6 characters.", "danger")
        return redirect(url_for("profile.profile_page"))

    if new != confirm:
        flash("New passwords do not match.", "danger")
        return redirect(url_for("profile.profile_page"))

    current_user.password = generate_password_hash(new)
    db.session.commit()
    flash("Password changed successfully.", "success")
    return redirect(url_for("profile.profile_page"))


@profile.route("/profile/avatar", methods=["POST"])
@login_required
def upload_avatar():
    file = request.files.get("avatar")

    if not file or not file.filename:
        flash("Please choose an image to upload.", "danger")
        return redirect(url_for("profile.profile_page"))

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_AVATAR:
        flash("Unsupported image type. Use PNG, JPG, GIF or WEBP.", "danger")
        return redirect(url_for("profile.profile_page"))

    os.makedirs(AVATAR_DIR, exist_ok=True)
    filename = secure_filename(f"user_{current_user.id}_{int(time.time())}{ext}")
    file.save(os.path.join(AVATAR_DIR, filename))

    # Remove the previous avatar file if it exists.
    if current_user.avatar:
        old = os.path.join(AVATAR_DIR, os.path.basename(current_user.avatar))
        if os.path.exists(old):
            try:
                os.remove(old)
            except OSError:
                pass

    current_user.avatar = f"uploads/avatars/{filename}"
    db.session.commit()
    flash("Profile picture updated.", "success")
    return redirect(url_for("profile.profile_page"))


@profile.route("/profile/avatar/remove", methods=["POST"])
@login_required
def remove_avatar():
    if current_user.avatar:
        old = os.path.join(AVATAR_DIR, os.path.basename(current_user.avatar))
        if os.path.exists(old):
            try:
                os.remove(old)
            except OSError:
                pass
        current_user.avatar = None
        db.session.commit()
        flash("Profile picture removed.", "info")

    return redirect(url_for("profile.profile_page"))
