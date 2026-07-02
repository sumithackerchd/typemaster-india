"""Central site-settings store.

Settings are persisted to ``static/data/settings.json`` so they survive
application restarts even when the database lives on ephemeral storage.
Signature/logo image files are stored on disk and only their relative
``static/`` path is kept here.
"""

import json
import os
import time

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SETTINGS_JSON = os.path.join(BASE_DIR, "static", "data", "settings.json")

_paragraph_count_cache = {"value": None, "expires": 0.0}
_PARAGRAPH_CACHE_TTL = 120  # seconds


DEFAULT_SETTINGS = {
    # General
    "site_name": "TypeMaster India",
    "default_timer": 60,
    "site_tagline": "India's Premier Typing Practice Platform",
    "maintenance_mode": False,
    # Branding
    "org_name": "TypeMaster India",
    "founder_name": "Sumit Goswami",
    "founder_title": "Founder & CEO",
    "primary_color": "#6366f1",
    "accent_color": "#22d3ee",
    # Certificate
    "signature_path": "images/signature.png",
    "certificate_prefix": "TMI",
    "certificate_footer": "Digitally generated and verifiable online.",
    # Certificate designer
    "cert_title": "Certificate of Achievement",
    "cert_subtitle": "Official Typing Performance Record",
    "cert_ribbon_enabled": True,
    "cert_ribbon_text": "CERTIFICATE OF EXCELLENCE",
    "cert_watermark_enabled": True,
    "cert_watermark_text": "TYPEMASTER INDIA",
    "cert_seal_enabled": True,
    "cert_logo_enabled": True,
    "cert_border_color": "#0d3b8e",
    "cert_gold_color": "#c9a227",
    "cert_heading_font": "Cinzel",
    "cert_qr_position": "center",
    "cert_signature_position": "right",
    # Email (non-secret prefs; SMTP secrets stay in env)
    "mail_from_name": "TypeMaster India",
    "mail_from_email": "",
    "otp_enabled": True,
    # OCR
    "ocr_default_lang": "auto",
    "ocr_deskew": True,
    "ocr_denoise": True,
    # Downloads
    "downloads_enabled": True,
    "max_upload_mb": 50,
    # Security
    "require_email_verify": False,
    "session_timeout_minutes": 0,
    "updated_at": "",
}


def load_settings():
    """Return the merged settings dict (defaults + saved overrides)."""
    data = dict(DEFAULT_SETTINGS)

    if os.path.exists(SETTINGS_JSON):
        try:
            with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if isinstance(saved, dict):
                data.update({k: v for k, v in saved.items() if v is not None})
        except (OSError, ValueError):
            pass

    return data


def save_settings(new_values):
    """Merge ``new_values`` into the stored settings and persist to disk."""
    from datetime import datetime

    data = load_settings()
    data.update(new_values)
    data["updated_at"] = str(datetime.utcnow())

    os.makedirs(os.path.dirname(SETTINGS_JSON), exist_ok=True)
    with open(SETTINGS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data


def get_setting(key, default=None):
    return load_settings().get(key, default)


def signature_abs_path():
    """Absolute filesystem path to the current signature image, or None."""
    rel = get_setting("signature_path") or ""
    if not rel:
        return None
    abs_path = os.path.join(BASE_DIR, "static", rel.replace("/", os.sep))
    return abs_path if os.path.exists(abs_path) else None


def count_paragraphs(use_cache=True):
    """Count paragraphs across English + Hindi JSON stores (cached)."""
    global _paragraph_count_cache

    now = time.time()
    if use_cache and _paragraph_count_cache["value"] is not None and now < _paragraph_count_cache["expires"]:
        return _paragraph_count_cache["value"]

    total = 0
    for rel in ("data/paragraphs.json", "data/hindi_mangal.json"):
        path = os.path.join(BASE_DIR, "static", rel)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for lang_key in data:
                if isinstance(data[lang_key], dict):
                    for items in data[lang_key].values():
                        if isinstance(items, list):
                            total += len(items)
        except (OSError, ValueError):
            pass

    _paragraph_count_cache = {"value": total, "expires": now + _PARAGRAPH_CACHE_TTL}
    return total


def invalidate_paragraph_cache():
    _paragraph_count_cache["value"] = None
    _paragraph_count_cache["expires"] = 0.0
