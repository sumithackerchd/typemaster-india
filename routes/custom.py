"""Custom Practice.

Lets a signed-in user create their own typing content by:

  * pasting text,
  * uploading a TXT / DOCX / PDF / CSV / XLSX / JSON file, or
  * uploading an image and running OCR (when Tesseract is available).

Extracted text can be previewed, edited, saved (as a ``CustomParagraph``),
renamed, favourited and deleted. Saved (or ad-hoc) text can be practised with
the shared typing engine. Users only ever see their own paragraphs.
"""

import re

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
    abort,
)
from flask_login import login_required, current_user

from models import db
from models.custom_paragraph import CustomParagraph
from utils.extract import (
    extract_text,
    split_paragraphs,
    ocr_available,
    ExtractionError,
    OCRUnavailable,
    SUPPORTED_EXTS,
)

custom = Blueprint("custom", __name__, url_prefix="/custom")

MAX_CONTENT = 20000  # characters — plenty for a long passage
VALID_DIFFICULTIES = ("easy", "medium", "hard")
VALID_LANGUAGES = ("english", "hindi")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _word_count(text):
    return len((text or "").split())


def _clean(text):
    """Collapse excessive whitespace but keep paragraph breaks."""
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # collapse 3+ newlines to a double newline, trim trailing spaces per line
    lines = [re.sub(r"[ \t]+", " ", ln).rstrip() for ln in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _detect_language(text):
    """Very small heuristic: any Devanagari char -> hindi, else english."""
    if text and re.search(r"[\u0900-\u097F]", text):
        return "hindi"
    return "english"


def _owned(paragraph_id):
    row = db.session.get(CustomParagraph, paragraph_id)
    if not row or row.user_id != current_user.id:
        abort(404)
    return row


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

@custom.route("/")
@login_required
def page():
    return render_template(
        "pages/custom.html",
        ocr_ready=ocr_available(),
    )


# ---------------------------------------------------------------------------
# Extraction (paste passes through, files are parsed, images use OCR)
# ---------------------------------------------------------------------------

@custom.route("/extract", methods=["POST"])
@login_required
def extract():
    """Return extracted text for an uploaded file.

    Never raises to the client: OCR/parse problems come back as a friendly
    ``success: False`` payload so the UI can show a message and keep working.
    """
    uploaded = request.files.get("file")

    if not uploaded or not uploaded.filename:
        return jsonify({"success": False, "message": "No file was uploaded."}), 400

    filename = uploaded.filename
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""

    if ext not in SUPPORTED_EXTS:
        return jsonify({
            "success": False,
            "message": f"Unsupported file type ({ext or 'unknown'}). "
                       "Use TXT, DOCX, PDF, CSV, XLSX, JSON or an image.",
        }), 400

    data = uploaded.read()

    if not data:
        return jsonify({"success": False, "message": "The file is empty."}), 400

    lang_hint = request.form.get("language") or None

    try:
        text = extract_text(filename, data, lang=lang_hint)
    except OCRUnavailable as exc:
        return jsonify({
            "success": False,
            "ocr": True,
            "message": str(exc),
        }), 200
    except ExtractionError as exc:
        return jsonify({"success": False, "message": str(exc)}), 200
    except Exception as exc:  # noqa: BLE001 — never crash the request
        return jsonify({
            "success": False,
            "message": f"Could not read that file: {exc}",
        }), 200

    text = _clean(text)

    if not text:
        return jsonify({
            "success": False,
            "message": "No readable text was found in that file.",
        }), 200

    paragraphs = split_paragraphs(text)

    return jsonify({
        "success": True,
        "text": text[:MAX_CONTENT],
        "language": _detect_language(text),
        "paragraph_count": len(paragraphs),
        "word_count": _word_count(text),
    })


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@custom.route("/save", methods=["POST"])
@login_required
def save():
    payload = request.get_json(silent=True) or {}

    content = _clean(payload.get("content") or "")
    title = (payload.get("title") or "").strip() or "Untitled Paragraph"
    language = (payload.get("language") or "english").lower()
    difficulty = (payload.get("difficulty") or "medium").lower()

    if language not in VALID_LANGUAGES:
        language = _detect_language(content)
    if difficulty not in VALID_DIFFICULTIES:
        difficulty = "medium"

    if not content or _word_count(content) < 3:
        return jsonify({
            "success": False,
            "message": "Please enter at least a few words to save.",
        }), 400

    row = CustomParagraph(
        user_id=current_user.id,
        title=title[:150],
        content=content[:MAX_CONTENT],
        language=language,
        difficulty=difficulty,
        category="custom",
        word_count=_word_count(content),
    )
    db.session.add(row)
    db.session.commit()

    return jsonify({"success": True, "paragraph": row.to_dict()})


@custom.route("/rename/<int:paragraph_id>", methods=["POST"])
@login_required
def rename(paragraph_id):
    row = _owned(paragraph_id)
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()

    if not title:
        return jsonify({"success": False, "message": "Title cannot be empty."}), 400

    row.title = title[:150]
    db.session.commit()
    return jsonify({"success": True, "paragraph": row.to_dict()})


@custom.route("/edit/<int:paragraph_id>", methods=["POST"])
@login_required
def edit(paragraph_id):
    row = _owned(paragraph_id)
    payload = request.get_json(silent=True) or {}
    content = _clean(payload.get("content") or "")

    if not content or _word_count(content) < 3:
        return jsonify({
            "success": False,
            "message": "Please enter at least a few words.",
        }), 400

    row.content = content[:MAX_CONTENT]
    row.word_count = _word_count(content)
    if payload.get("difficulty") in VALID_DIFFICULTIES:
        row.difficulty = payload["difficulty"]
    db.session.commit()
    return jsonify({"success": True, "paragraph": row.to_dict()})


@custom.route("/delete/<int:paragraph_id>", methods=["POST"])
@login_required
def delete(paragraph_id):
    row = _owned(paragraph_id)
    db.session.delete(row)
    db.session.commit()
    return jsonify({"success": True})


@custom.route("/favorite/<int:paragraph_id>", methods=["POST"])
@login_required
def favorite(paragraph_id):
    row = _owned(paragraph_id)
    row.favorite = not row.favorite
    db.session.commit()
    return jsonify({"success": True, "favorite": row.favorite})


@custom.route("/list")
@login_required
def list_paragraphs():
    rows = (
        CustomParagraph.query
        .filter_by(user_id=current_user.id)
        .order_by(CustomParagraph.updated_at.desc())
        .all()
    )
    items = [r.to_dict() for r in rows]
    return jsonify({
        "success": True,
        "saved": items,
        "favorites": [i for i in items if i["favorite"]],
        "recent": items[:10],
    })


# ---------------------------------------------------------------------------
# Practice
# ---------------------------------------------------------------------------

def _feed_payload(content, language):
    """Engine-compatible feed: same content under every difficulty."""
    key = "custom"
    block = {"easy": [content], "medium": [content], "hard": [content]}
    return {key: block}


@custom.route("/practice/start", methods=["POST"])
@login_required
def practice_start():
    """Store ad-hoc (unsaved) text in the session and open the practice page."""
    payload = request.get_json(silent=True) or {}
    content = _clean(payload.get("content") or "")
    title = (payload.get("title") or "Custom Practice").strip()

    if not content or _word_count(content) < 3:
        return jsonify({
            "success": False,
            "message": "Please enter at least a few words to practice.",
        }), 400

    session["custom_practice"] = {
        "content": content[:MAX_CONTENT],
        "title": title[:150],
        "language": _detect_language(content),
    }
    return jsonify({
        "success": True,
        "redirect": url_for("custom.practice_session"),
    })


@custom.route("/practice/session")
@login_required
def practice_session():
    data = session.get("custom_practice")
    if not data:
        return redirect(url_for("custom.page"))
    return render_template(
        "pages/custom_practice.html",
        title=data["title"],
        language=data["language"],
        feed_url=url_for("custom.feed_session"),
    )


@custom.route("/practice/<int:paragraph_id>")
@login_required
def practice(paragraph_id):
    row = _owned(paragraph_id)
    # Touch updated_at so it surfaces under "Recent Practice".
    from datetime import datetime
    row.updated_at = datetime.utcnow()
    db.session.commit()
    return render_template(
        "pages/custom_practice.html",
        title=row.title,
        language=row.language,
        feed_url=url_for("custom.feed", paragraph_id=paragraph_id),
    )


@custom.route("/feed/<int:paragraph_id>")
@login_required
def feed(paragraph_id):
    row = _owned(paragraph_id)
    return jsonify(_feed_payload(row.content, row.language))


@custom.route("/feed/session")
@login_required
def feed_session():
    data = session.get("custom_practice")
    if not data:
        return jsonify(_feed_payload("", "english"))
    return jsonify(_feed_payload(data["content"], data["language"]))
