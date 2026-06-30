from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from utils.mock_constants import (
    LANGUAGES,
    MODES,
    DIFFICULTIES,
    CATEGORIES,
    DURATIONS,
    LANGUAGE_LABELS,
    CATEGORY_LABELS,
    CATEGORY_KIND,
    is_valid_language,
    is_valid_category,
    is_valid_difficulty,
    is_valid_mode,
    normalize_duration,
)

mocktest = Blueprint("mocktest", __name__)


@mocktest.route("/mock-test")
@login_required
def setup():
    """Mock test configuration screen."""
    return render_template(
        "pages/mocktest_setup.html",
        languages=LANGUAGES,
        modes=MODES,
        difficulties=DIFFICULTIES,
        categories=CATEGORIES,
        durations=DURATIONS,
    )


@mocktest.route("/mock-test/run")
@login_required
def run():
    """Run a configured mock test using the typing engine."""
    language = (request.args.get("language") or "english").lower()
    category = (request.args.get("category") or "random_paragraph").lower()
    difficulty = (request.args.get("difficulty") or "easy").lower()
    mode = (request.args.get("mode") or "practice").lower()
    duration = normalize_duration(request.args.get("duration", 60))

    # Validate everything; fall back to safe defaults.
    if not is_valid_language(language):
        language = "english"
    if not is_valid_category(category):
        category = "random_paragraph"
    if not is_valid_difficulty(difficulty):
        difficulty = "easy"
    if not is_valid_mode(mode):
        mode = "practice"

    return render_template(
        "pages/mocktest_run.html",
        language=language,
        category=category,
        difficulty=difficulty,
        mode=mode,
        duration=duration,
        language_label=LANGUAGE_LABELS.get(language, "English"),
        save_language="Hindi" if language == "hindi" else "English",
        category_label=CATEGORY_LABELS.get(category, "Random Paragraph"),
        kind=CATEGORY_KIND.get(category, "paragraph"),
    )
