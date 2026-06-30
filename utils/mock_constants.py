"""Shared definitions for the Mock Test System and Paragraph Database.

Keeping these in one place ensures the setup page, the paragraph API, the
admin manager and the seeder all agree on the same slugs and labels.
"""

# Languages -----------------------------------------------------------------

LANGUAGES = [
    {"slug": "english", "label": "English"},
    {"slug": "hindi", "label": "Hindi Mangal"},
]

LANGUAGE_SLUGS = [lang["slug"] for lang in LANGUAGES]

LANGUAGE_LABELS = {lang["slug"]: lang["label"] for lang in LANGUAGES}


# Modes ---------------------------------------------------------------------

MODES = [
    {"slug": "practice", "label": "Practice Mode", "desc": "Relaxed practice. Results are saved."},
    {"slug": "exam", "label": "Exam Mode", "desc": "Strict, timed exam simulation."},
]

MODE_SLUGS = [m["slug"] for m in MODES]


# Difficulty ----------------------------------------------------------------

DIFFICULTIES = [
    {"slug": "easy", "label": "Easy"},
    {"slug": "medium", "label": "Medium"},
    {"slug": "hard", "label": "Hard"},
]

DIFFICULTY_SLUGS = [d["slug"] for d in DIFFICULTIES]


# Categories ----------------------------------------------------------------
# kind = "paragraph" (sentences) or "words" (space separated random words)

CATEGORIES = [
    {"slug": "random_paragraph", "label": "Random Paragraph", "kind": "paragraph", "icon": "fa-shuffle"},
    {"slug": "random_words", "label": "Random Words", "kind": "words", "icon": "fa-font"},
    {"slug": "ssc", "label": "SSC", "kind": "paragraph", "icon": "fa-building-columns"},
    {"slug": "railway", "label": "Railway", "kind": "paragraph", "icon": "fa-train"},
    {"slug": "up_police", "label": "UP Police", "kind": "paragraph", "icon": "fa-shield-halved"},
    {"slug": "cpct", "label": "CPCT", "kind": "paragraph", "icon": "fa-laptop-code"},
    {"slug": "government", "label": "Government Exams", "kind": "paragraph", "icon": "fa-landmark"},
    {"slug": "programming", "label": "Programming", "kind": "paragraph", "icon": "fa-code"},
    {"slug": "general_knowledge", "label": "General Knowledge", "kind": "paragraph", "icon": "fa-book-open"},
    {"slug": "typing_practice", "label": "Typing Practice", "kind": "paragraph", "icon": "fa-keyboard"},
]

CATEGORY_SLUGS = [c["slug"] for c in CATEGORIES]

CATEGORY_LABELS = {c["slug"]: c["label"] for c in CATEGORIES}

CATEGORY_KIND = {c["slug"]: c["kind"] for c in CATEGORIES}


# Durations (seconds) -------------------------------------------------------

DURATIONS = [
    {"seconds": 30, "label": "30 Seconds"},
    {"seconds": 60, "label": "1 Minute"},
    {"seconds": 120, "label": "2 Minutes"},
    {"seconds": 300, "label": "5 Minutes"},
    {"seconds": 600, "label": "10 Minutes"},
]

DURATION_VALUES = [d["seconds"] for d in DURATIONS]

# Custom duration bounds (seconds)
CUSTOM_DURATION_MIN = 10
CUSTOM_DURATION_MAX = 3600


def is_valid_language(value):
    return value in LANGUAGE_SLUGS


def is_valid_category(value):
    return value in CATEGORY_SLUGS


def is_valid_difficulty(value):
    return value in DIFFICULTY_SLUGS


def is_valid_mode(value):
    return value in MODE_SLUGS


def normalize_duration(value):
    """Clamp an arbitrary duration into the allowed range."""
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return 60
    if seconds < CUSTOM_DURATION_MIN:
        return CUSTOM_DURATION_MIN
    if seconds > CUSTOM_DURATION_MAX:
        return CUSTOM_DURATION_MAX
    return seconds
