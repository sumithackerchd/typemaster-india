import os
import tempfile

from flask import send_file

from utils.pdf_generator import create_certificate

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from utils.certificate import (
    ensure_certificate_identity,
    verification_url,
    build_qr_svg_data_uri,
)
from flask import Blueprint, render_template, abort

from models.user import User

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

#=================
# certi
#

@result.route("/certificate/<int:result_id>")
@login_required
def certificate(result_id):

    result_data = Result.query.filter_by(
        id=result_id,
        user_id=current_user.id
    ).first()

    if not result_data:
        abort(404)

    certificate_id, _token = ensure_certificate_identity(result_data)

    verify_url = verification_url(request.host_url, certificate_id)
    qr_code = build_qr_svg_data_uri(verify_url)

    return render_template(

        "pages/certificate.html",

        result=result_data,

        certificate_id=certificate_id,

        qr_code=qr_code,

        verify_url=verify_url
    )


# ==========================================
# Public Certificate Verification
# ==========================================

@result.route("/verify/<certificate_id>")
def verify_certificate(certificate_id):

    result_data = Result.query.filter_by(
        certificate_id=certificate_id
    ).first()

    holder = None
    if result_data:
        holder = db.session.get(User, result_data.user_id)

    return render_template(
        "pages/verify.html",
        result=result_data,
        holder=holder,
        certificate_id=certificate_id,
        verified=bool(result_data),
    )

# ccccc
@result.route("/certificate/download/<int:result_id>")
@login_required
def download_certificate(result_id):

    result_data = Result.query.filter_by(
        id=result_id,
        user_id=current_user.id
    ).first_or_404()

    certificate_id, _token = ensure_certificate_identity(result_data)

    verify_url = verification_url(request.host_url, certificate_id)

    pdf_path = os.path.join(
        tempfile.gettempdir(),
        f"certificate_{result_data.id}.pdf"
    )

    create_certificate(
        pdf_path,
        result_data,
        certificate_id,
        current_user,
        verify_url=verify_url
    )

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"{certificate_id}.pdf",
        mimetype="application/pdf"
    )
