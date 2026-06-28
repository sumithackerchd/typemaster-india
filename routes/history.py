from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.result import Result

history = Blueprint("history", __name__)


@history.route("/history")
@login_required
def history_page():

    results = Result.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Result.created_at.desc()
    ).all()

    return render_template(
        "pages/history.html",
        results=results
    )