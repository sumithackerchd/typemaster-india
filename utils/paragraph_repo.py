"""Read helpers for paragraph content.

Database is the primary source. If a query fails or returns nothing, we fall
back to the JSON mirror written by the seeder (``seed_paragraphs.json``).
"""

import random

from models.paragraph import Paragraph
from utils.seed_paragraphs import load_json_mirror

DIFFICULTIES = ["easy", "medium", "hard"]


def get_grouped(language, category):
    """Return {difficulty: [content, ...]} for a language + category.

    Falls back to the JSON mirror when the database has no rows.
    """
    grouped = {d: [] for d in DIFFICULTIES}

    try:
        rows = (
            Paragraph.query
            .filter_by(language=language, category=category)
            .all()
        )
        for row in rows:
            diff = row.difficulty if row.difficulty in grouped else "easy"
            grouped[diff].append(row.content)
    except Exception:
        rows = []

    if any(grouped[d] for d in DIFFICULTIES):
        return grouped

    # JSON fallback
    mirror = load_json_mirror()
    if mirror and language in mirror and category in mirror[language]:
        for d in DIFFICULTIES:
            grouped[d] = list(mirror[language][category].get(d, []))

    return grouped


def pick_random(language, category, difficulty):
    """Pick a single random paragraph for the given filters."""
    grouped = get_grouped(language, category)

    if difficulty in grouped and grouped[difficulty]:
        return random.choice(grouped[difficulty])

    # Fall back to any difficulty that has content
    for d in DIFFICULTIES:
        if grouped[d]:
            return random.choice(grouped[d])

    return ""
