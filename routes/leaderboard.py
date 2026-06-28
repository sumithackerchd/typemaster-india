from flask import Blueprint, render_template
from sqlalchemy import func, and_

from models import db
from models.user import User
from models.result import Result

leaderboard = Blueprint("leaderboard", __name__)


@leaderboard.route("/leaderboard")
def leaderboard_page():

    best_wpm_subq = (
        db.session.query(
            Result.user_id.label("user_id"),
            func.max(Result.net_wpm).label("best_wpm"),
        )
        .group_by(Result.user_id)
        .subquery()
    )

    best_accuracy_subq = (
        db.session.query(
            Result.user_id.label("user_id"),
            func.max(Result.accuracy).label("best_accuracy"),
        )
        .join(
            best_wpm_subq,
            and_(
                Result.user_id == best_wpm_subq.c.user_id,
                Result.net_wpm == best_wpm_subq.c.best_wpm,
            ),
        )
        .group_by(Result.user_id)
        .subquery()
    )

    total_tests_subq = (
        db.session.query(
            Result.user_id.label("user_id"),
            func.count(Result.id).label("total_tests"),
        )
        .group_by(Result.user_id)
        .subquery()
    )

    rows = (
        db.session.query(
            User.username.label("username"),
            best_wpm_subq.c.best_wpm.label("best_wpm"),
            best_accuracy_subq.c.best_accuracy.label("accuracy"),
            total_tests_subq.c.total_tests.label("total_tests"),
        )
        .join(best_wpm_subq, User.id == best_wpm_subq.c.user_id)
        .join(best_accuracy_subq, User.id == best_accuracy_subq.c.user_id)
        .join(total_tests_subq, User.id == total_tests_subq.c.user_id)
        .order_by(
            best_wpm_subq.c.best_wpm.desc(),
            best_accuracy_subq.c.best_accuracy.desc(),
            User.username.asc(),
        )
        .limit(100)
        .all()
    )

    return render_template(
        "pages/leaderboard.html",
        leaderboard=rows,
    )
