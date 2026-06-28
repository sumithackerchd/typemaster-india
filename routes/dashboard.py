from datetime import date

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from models import db
from models.result import Result

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
@login_required
def dashboard_page():

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

    average_accuracy = db.session.query(
        func.avg(Result.accuracy)
    ).filter_by(
        user_id=current_user.id
    ).scalar()

    if average_accuracy is None:
        average_accuracy = 0

    last_test = Result.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Result.created_at.desc()
    ).first()

    recent_tests = Result.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Result.created_at.desc()
    ).limit(5).all()

    user_rank = None

    if total_tests > 0:

        best_scores = (
            db.session.query(func.max(Result.net_wpm))
            .group_by(Result.user_id)
            .all()
        )

        scores = sorted([row[0] for row in best_scores], reverse=True)
        users_ahead = sum(1 for score in scores if score > best_wpm)
        user_rank = users_ahead + 1

    daily_goal = 0

    if last_test and last_test.created_at.date() == date.today():
        daily_goal = 100

    return render_template(
        "pages/dashboard.html",
        total_tests=total_tests,
        best_wpm=best_wpm,
        average_accuracy=round(average_accuracy, 1),
        last_test=last_test,
        recent_tests=recent_tests,
        user_rank=user_rank,
        daily_goal=daily_goal
    )