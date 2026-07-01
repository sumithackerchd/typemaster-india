"""Shared route decorators for TypeMaster India."""

from functools import wraps

from flask import redirect, url_for, flash, abort, request
from flask_login import current_user


def admin_required(view):
    """Require an authenticated user with ``is_admin == True``.

    Non-admin users receive HTTP 403 for API/JSON requests, or are redirected
    to the user dashboard with an authorization flash for HTML pages.
    """

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.path))

        if not getattr(current_user, "is_admin", False):
            wants_json = (
                request.is_json
                or request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or request.accept_mimetypes.best == "application/json"
            )
            if wants_json:
                abort(403)
            flash("You are not authorized.", "danger")
            return redirect(url_for("dashboard.dashboard_page"))

        return view(*args, **kwargs)

    return wrapped
