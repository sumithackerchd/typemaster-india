"""Download Center.

Public, dynamic download hub for Hindi fonts, typing software, keyboard-layout
images, practice PDFs and installation guides. Admins upload files (with a
version, description, category and optional preview image); users browse and
download them. Every download increments a counter. Nothing is hardcoded.
"""

import os
import re
import secrets
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    send_from_directory, abort,
)
from flask_login import login_required, current_user
from utils.decorators import admin_required
from werkzeug.utils import secure_filename

from models import db
from models.download import Download, CATEGORIES, CATEGORY_ORDER

downloads = Blueprint("downloads", __name__)

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads", "downloads")

ALLOWED_FILE_EXTS = {
    ".ttf", ".otf", ".zip", ".exe", ".msi", ".pdf", ".rar", ".7z",
    ".png", ".jpg", ".jpeg", ".webp", ".doc", ".docx",
}
ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _ext(filename):
    return os.path.splitext(filename or "")[1].lower()


def _save_upload(file_storage, allowed):
    """Persist an uploaded file to the download store; returns (stored, orig, ext, size)."""
    original = secure_filename(file_storage.filename or "")
    ext = _ext(original)
    if ext not in allowed:
        raise ValueError(f"File type {ext or 'unknown'} is not allowed.")

    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)
    if size > MAX_UPLOAD_BYTES:
        raise ValueError("File is too large (max 50 MB).")

    _ensure_upload_dir()
    stored = f"{secrets.token_hex(8)}{ext}"
    file_storage.save(os.path.join(UPLOAD_DIR, stored))
    return stored, original, ext, size


# ---------------------------------------------------------------------------
# Public Download Center
# ---------------------------------------------------------------------------

@downloads.route("/downloads")
def center():
    query = (request.args.get("q") or "").strip()
    active = (request.args.get("category") or "").strip()

    rows = Download.query.order_by(Download.created_at.desc())
    if query:
        like = f"%{query}%"
        rows = rows.filter(
            db.or_(Download.title.ilike(like), Download.description.ilike(like))
        )
    if active in CATEGORIES:
        rows = rows.filter(Download.category == active)
    rows = rows.all()

    grouped = {slug: [] for slug in CATEGORY_ORDER}
    for row in rows:
        grouped.setdefault(row.category, []).append(row)

    return render_template(
        "pages/downloads.html",
        grouped=grouped,
        categories=CATEGORIES,
        category_order=CATEGORY_ORDER,
        active=active,
        query=query,
        total=len(rows),
    )


@downloads.route("/downloads/file/<int:download_id>")
def get_file(download_id):
    row = db.session.get(Download, download_id)
    if not row:
        abort(404)

    path = os.path.join(UPLOAD_DIR, row.stored_name)
    if not os.path.exists(path):
        abort(404)

    row.download_count = (row.download_count or 0) + 1
    db.session.commit()

    return send_from_directory(
        UPLOAD_DIR,
        row.stored_name,
        as_attachment=True,
        download_name=row.filename,
    )


# ---------------------------------------------------------------------------
# Admin Upload Manager
# ---------------------------------------------------------------------------

@downloads.route("/admin/downloads")
@login_required
@admin_required
def manage():
    rows = Download.query.order_by(Download.created_at.desc()).all()
    return render_template(
        "admin/downloads.html",
        rows=rows,
        categories=CATEGORIES,
        category_order=CATEGORY_ORDER,
        active="downloads",
    )


@downloads.route("/admin/downloads/upload", methods=["POST"])
@login_required
@admin_required
def upload():
    title = (request.form.get("title") or "").strip()
    category = (request.form.get("category") or "").strip()
    description = (request.form.get("description") or "").strip()
    version = (request.form.get("version") or "").strip()

    if not title:
        flash("Please enter a title.", "danger")
        return redirect(url_for("downloads.manage"))
    if category not in CATEGORIES:
        flash("Please choose a valid category.", "danger")
        return redirect(url_for("downloads.manage"))

    file_storage = request.files.get("file")
    if not file_storage or not file_storage.filename:
        flash("Please choose a file to upload.", "danger")
        return redirect(url_for("downloads.manage"))

    try:
        stored, original, ext, size = _save_upload(file_storage, ALLOWED_FILE_EXTS)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("downloads.manage"))

    image_rel = ""
    image_storage = request.files.get("image")
    if image_storage and image_storage.filename:
        try:
            img_stored, _, _, _ = _save_upload(image_storage, ALLOWED_IMAGE_EXTS)
            image_rel = f"uploads/downloads/{img_stored}"
        except ValueError as exc:
            flash(f"Preview image skipped: {exc}", "info")

    row = Download(
        category=category,
        title=title[:160],
        description=description,
        version=version[:40],
        filename=original,
        stored_name=stored,
        file_ext=ext,
        size_bytes=size,
        image=image_rel,
    )
    db.session.add(row)
    db.session.commit()

    flash(f'"{title}" uploaded successfully.', "success")
    return redirect(url_for("downloads.manage"))


@downloads.route("/admin/downloads/delete/<int:download_id>", methods=["POST"])
@login_required
@admin_required
def delete(download_id):
    row = db.session.get(Download, download_id)
    if not row:
        abort(404)

    # Remove the stored file (and preview image) from disk.
    for rel in (row.stored_name, os.path.basename(row.image) if row.image else None):
        if not rel:
            continue
        path = os.path.join(UPLOAD_DIR, rel)
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

    db.session.delete(row)
    db.session.commit()
    flash("Download removed.", "success")
    return redirect(url_for("downloads.manage"))
