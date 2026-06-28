from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user

from models import db
from models.result import Result

result = Blueprint("result", __name__)


# ==========================================
# Save Result
# ==========================================

@result.route("/save-result", methods=["POST"])
@login_required
def save_result():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400

        new_result = Result(

            user_id=current_user.id,

            language=data.get("language", "English"),

            difficulty=data.get("difficulty", "Easy"),

            duration=data.get("duration", 60),

            gross_wpm=data.get("gross_wpm", 0),

            net_wpm=data.get("net_wpm", 0),

            cpm=data.get("cpm", 0),

            accuracy=float(data.get("accuracy", 0)),

            errors=data.get("errors", 0)

        )

        db.session.add(new_result)

        db.session.commit()

        return jsonify({

            "success": True,

            "message": "Result Saved Successfully",

            "result_id": new_result.id

        })

    except Exception as e:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# ==========================================
# Latest Result
# ==========================================

@result.route("/latest-result")
@login_required
def latest_result():

    latest = Result.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Result.id.desc()

    ).first()

    if latest is None:

        return jsonify({

            "success": False,

            "message": "No Result Found"

        })

    return jsonify({

        "success": True,

        "id": latest.id,

        "language": latest.language,

        "difficulty": latest.difficulty,

        "duration": latest.duration,

        "gross_wpm": latest.gross_wpm,

        "net_wpm": latest.net_wpm,

        "cpm": latest.cpm,

        "accuracy": latest.accuracy,

        "errors": latest.errors,

        "created_at": str(latest.created_at)

    })


# ==========================================
# Result History
# ==========================================

@result.route("/result-history")
@login_required
def result_history():

    results = Result.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Result.id.desc()

    ).all()

    history = []

    for row in results:

        history.append({

            "id": row.id,

            "language": row.language,

            "difficulty": row.difficulty,

            "gross_wpm": row.gross_wpm,

            "net_wpm": row.net_wpm,

            "accuracy": row.accuracy,

            "errors": row.errors,

            "created_at": str(row.created_at)

        })

    return jsonify({

        "success": True,

        "total": len(history),

        "results": history

    })
#==========================================
# Result Page
#==========================================

@result.route("/result")
@login_required
def result_page():

    latest = Result.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Result.id.desc()
    ).first()

    return render_template(
        "pages/result.html",
        result=latest
    )