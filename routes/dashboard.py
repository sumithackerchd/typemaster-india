from datetime import date

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from utils.achievements import get_achievements

from models import db
from models.result import Result

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
@login_required
def dashboard_page():

    # --------------------------
    # Basic Statistics
    # --------------------------

    total_tests = Result.query.filter_by(
        user_id=current_user.id
    ).count()

    best_wpm = (
        db.session.query(func.max(Result.net_wpm))
        .filter_by(user_id=current_user.id)
        .scalar()
    ) or 0

    average_accuracy = (
        db.session.query(func.avg(Result.accuracy))
        .filter_by(user_id=current_user.id)
        .scalar()
    ) or 0

    last_test = (
        Result.query.filter_by(user_id=current_user.id)
        .order_by(Result.created_at.desc())
        .first()
    )

    recent_tests = (
        Result.query.filter_by(user_id=current_user.id)
        .order_by(Result.created_at.desc())
        .limit(5)
        .all()
    )

    # --------------------------
    # Rank
    # --------------------------

    user_rank = None

    if total_tests:

        best_scores = (
            db.session.query(
                func.max(Result.net_wpm)
            )
            .group_by(Result.user_id)
            .all()
        )

        scores = sorted(
            [row[0] for row in best_scores],
            reverse=True
        )

        user_rank = (
            sum(score > best_wpm for score in scores)
            + 1
        )

    # --------------------------
    # Daily Goal
    # --------------------------

    daily_goal = 0

    if (
        last_test
        and last_test.created_at.date() == date.today()
    ):
        daily_goal = 100

    # --------------------------
    # Chart Data
    # --------------------------

    chart_results = (
        Result.query.filter_by(
            user_id=current_user.id
        )
        .order_by(Result.created_at.asc())
        .limit(10)
        .all()
    )

    chart_labels = [
        r.created_at.strftime("%d %b")
        for r in chart_results
    ]

    chart_wpm = [
        r.net_wpm
        for r in chart_results
    ]

    chart_accuracy = [
        round(r.accuracy, 1)
        for r in chart_results
    ]

    # --------------------------
    # Analytics Summary
    # --------------------------

    highest_accuracy = (
        max(chart_accuracy)
        if chart_accuracy else 0
    )

    average_wpm = (
        round(
            sum(chart_wpm) / len(chart_wpm),
            1
        )
        if chart_wpm else 0
    )

    last_wpm = (
        chart_wpm[-1]
        if chart_wpm else 0
    )

    improvement = round(
        last_wpm - average_wpm,
        1
    )

    # --------------------------
    # Performance Level
    # --------------------------

    if best_wpm >= 90:

        performance_level = "Expert"

    elif best_wpm >= 70:

        performance_level = "Advanced"

    elif best_wpm >= 50:

        performance_level = "Intermediate"

    elif best_wpm >= 30:

        performance_level = "Beginner"

    else:

        performance_level = "Starter"

    # --------------------------
    # Accuracy Status
    # --------------------------

    if average_accuracy >= 98:

        accuracy_status = "Excellent"

    elif average_accuracy >= 95:

        accuracy_status = "Very Good"

    elif average_accuracy >= 90:

        accuracy_status = "Good"

    else:

        accuracy_status = "Needs Improvement"

    # --------------------------
    # Achievements
    # --------------------------

    achievements = get_achievements(
        best_wpm,
        average_accuracy,
        total_tests
    )

    # --------------------------
    # Render
    # --------------------------

    return render_template(
        "pages/dashboard.html",

        total_tests=total_tests,
        best_wpm=best_wpm,
        average_accuracy=round(average_accuracy, 1),

        last_test=last_test,
        recent_tests=recent_tests,

        user_rank=user_rank,
        daily_goal=daily_goal,

        performance_level=performance_level,
        accuracy_status=accuracy_status,
        achievements=achievements,

        average_wpm=average_wpm,
        highest_accuracy=highest_accuracy,
        improvement=improvement,
        chart_labels=chart_labels,
        chart_wpm=chart_wpm,
        chart_accuracy=chart_accuracy,
    )
