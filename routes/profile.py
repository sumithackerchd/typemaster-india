from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from models import db
from models.result import Result

profile = Blueprint("profile", __name__)


@profile.route("/profile")
@login_required
def profile_page():

    total_tests = Result.query.filter_by(
        user_id=current_user.id
    ).count()

    best_wpm = db.session.query(
        func.max(Result.net_wpm)
    ).filter_by(
        user_id=current_user.id
    ).scalar()

    if best_wpm is None:
        best_wpm = 0

    avg_accuracy = db.session.query(
        func.avg(Result.accuracy)
    ).filter_by(
        user_id=current_user.id
    ).scalar()

    if avg_accuracy is None:
        avg_accuracy = 0

    return render_template(
        "pages/profile.html",
        total_tests=total_tests,
        best_wpm=best_wpm,
        avg_accuracy=round(avg_accuracy,1)
    )