from flask import Blueprint, jsonify, request

from utils.paragraph_repo import get_grouped, pick_random
from utils.mock_constants import (
    is_valid_language,
    is_valid_category,
    is_valid_difficulty,
)

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/paragraphs")
def paragraphs():
    """Engine-compatible paragraph feed.

    Returns ``{ "<language>": { "easy": [...], "medium": [...], "hard": [...] } }``
    for a single language + category so the existing typing engine can consume
    it directly via TYPING_CONFIG.languages[...].dataUrl.
    """
    language = (request.args.get("language") or "english").lower()
    category = (request.args.get("category") or "random_paragraph").lower()

    if not is_valid_language(language):
        language = "english"
    if not is_valid_category(category):
        category = "random_paragraph"

    grouped = get_grouped(language, category)

    return jsonify({language: grouped})


@api.route("/paragraph")
def single_paragraph():
    """Return a single random paragraph for the given filters."""
    language = (request.args.get("language") or "english").lower()
    category = (request.args.get("category") or "random_paragraph").lower()
    difficulty = (request.args.get("difficulty") or "easy").lower()

    if not is_valid_language(language):
        language = "english"
    if not is_valid_category(category):
        category = "random_paragraph"
    if not is_valid_difficulty(difficulty):
        difficulty = "easy"

    content = pick_random(language, category, difficulty)

    return jsonify({
        "success": bool(content),
        "language": language,
        "category": category,
        "difficulty": difficulty,
        "content": content,
    })
