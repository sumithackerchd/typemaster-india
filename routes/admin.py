import json
import os
from datetime import datetime, date
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from models import db
from models.user import User
from models.result import Result

admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ENGLISH_JSON = os.path.join(BASE_DIR, "static", "data", "paragraphs.json")
HINDI_JSON = os.path.join(BASE_DIR, "static", "data", "hindi_mangal.json")
SETTINGS_JSON = os.path.join(BASE_DIR, "static", "data", "settings.json")


def admin_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        if not getattr(current_user, "is_admin", False):
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard.dashboard_page"))

        return view(*args, **kwargs)

    return wrapped


def load_json(path, default):

    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@admin.route("/")
@login_required
@admin_required
def dashboard():

    total_users = User.query.count()
    total_tests = Result.query.count()

    today_start = datetime.combine(date.today(), datetime.min.time())

    today_tests = Result.query.filter(
        Result.created_at >= today_start
    ).count()

    admin_count = User.query.filter_by(is_admin=True).count()

    recent_users = (
        User.query.order_by(User.id.desc()).limit(5).all()
    )

    recent_results = (
        Result.query.order_by(Result.created_at.desc()).limit(6).all()
    )

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_tests=total_tests,
        today_tests=today_tests,
        admin_count=admin_count,
        recent_users=recent_users,
        recent_results=recent_results,
    )


@admin.route("/users")
@login_required
@admin_required
def users():

    search = request.args.get("search", "")

    if search:
        users_list = User.query.filter(
            User.username.contains(search) |
            User.email.contains(search)
        ).all()
    else:
        users_list = User.query.order_by(User.id.desc()).all()

    return render_template(
        "admin/user.html",
        users=users_list,
        search=search
    )


@admin.route("/users/delete/<int:user_id>")
@login_required
@admin_required
def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully.", "success")
    return redirect(url_for("admin.users"))


@admin.route("/users/toggle-admin/<int:user_id>")
@login_required
@admin_required
def toggle_admin(user_id):

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot change your own admin role.", "danger")
        return redirect(url_for("admin.users"))

    user.is_admin = not user.is_admin
    db.session.commit()

    flash("Admin role updated.", "success")
    return redirect(url_for("admin.users"))


@admin.route("/results")
@login_required
@admin_required
def results():

    results_list = Result.query.order_by(
        Result.created_at.desc()
    ).all()

    return render_template(
        "admin/result.html",
        results=results_list
    )


@admin.route("/paragraphs/english")
@login_required
@admin_required
def english_paragraphs():

    data = load_json(ENGLISH_JSON, {"english": {"easy": [], "medium": [], "hard": []}})

    return render_template(
        "admin/english_paragraphs.html",
        paragraphs=data.get("english", {}),
        difficulties=["easy", "medium", "hard"]
    )


@admin.route("/paragraphs/hindi")
@login_required
@admin_required
def hindi_paragraphs():

    data = load_json(HINDI_JSON, {"hindi": {"easy": [], "medium": [], "hard": []}})

    return render_template(
        "admin/hindi_paragraphs.html",
        paragraphs=data.get("hindi", {}),
        difficulties=["easy", "medium", "hard"]
    )


@admin.route("/paragraphs/save", methods=["POST"])
@login_required
@admin_required
def save_paragraph():

    payload = request.get_json()

    if not payload:
        return jsonify({"success": False, "message": "No data received"}), 400

    language = payload.get("language")
    difficulty = payload.get("difficulty")
    content = (payload.get("content") or "").strip()
    action = payload.get("action", "add")
    index = payload.get("index")

    if language not in ("english", "hindi"):
        return jsonify({"success": False, "message": "Invalid language"}), 400

    if difficulty not in ("easy", "medium", "hard"):
        return jsonify({"success": False, "message": "Invalid difficulty"}), 400

    path = ENGLISH_JSON if language == "english" else HINDI_JSON
    default = {language: {"easy": [], "medium": [], "hard": []}}
    data = load_json(path, default)

    if language not in data:
        data[language] = {"easy": [], "medium": [], "hard": []}

    items = data[language].setdefault(difficulty, [])

    if action == "add":

        if not content:
            return jsonify({"success": False, "message": "Content required"}), 400

        items.append(content)

    elif action == "delete":

        if index is None or index < 0 or index >= len(items):
            return jsonify({"success": False, "message": "Invalid index"}), 400

        items.pop(index)

    elif action == "edit":

        if index is None or index < 0 or index >= len(items):
            return jsonify({"success": False, "message": "Invalid index"}), 400

        if not content:
            return jsonify({"success": False, "message": "Content required"}), 400

        items[index] = content

    else:
        return jsonify({"success": False, "message": "Invalid action"}), 400

    save_json(path, data)

    return jsonify({"success": True, "paragraphs": data[language]})


@admin.route("/settings", methods=["GET", "POST"])
@login_required
@admin_required
def settings():

    default_settings = {
        "site_name": "TypeMaster India",
        "default_timer": 60,
        "updated_at": str(datetime.utcnow())
    }

    if request.method == "POST":

        settings_data = {
            "site_name": request.form.get("site_name", "TypeMaster India"),
            "default_timer": int(request.form.get("default_timer", 60)),
            "updated_at": str(datetime.utcnow())
        }

        save_json(SETTINGS_JSON, settings_data)
        flash("Settings saved.", "success")
        return redirect(url_for("admin.settings"))

    settings_data = load_json(SETTINGS_JSON, default_settings)

    return render_template(
        "admin/settings.html",
        settings=settings_data
    )
