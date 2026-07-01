from datetime import datetime

from . import db


# ---------------------------------------------------------------------------
# Download
#
# A file made available in the public Download Center (fonts, typing software,
# keyboard-layout images, practice PDFs, installation guides, ...). Everything
# is dynamic: admins upload files and set the metadata; nothing is hardcoded.
# ---------------------------------------------------------------------------


# category slug -> human label (used by the UI and admin upload form)
CATEGORIES = {
    "hindi_fonts": "Hindi Fonts",
    "typing_software": "Hindi Typing Software",
    "keyboard_layout": "Keyboard Layout",
    "practice_pdf": "Practice PDFs",
    "installation_guide": "Installation Guides",
}

CATEGORY_ORDER = [
    "hindi_fonts",
    "typing_software",
    "keyboard_layout",
    "practice_pdf",
    "installation_guide",
]


class Download(db.Model):

    __tablename__ = "downloads"

    id = db.Column(db.Integer, primary_key=True)

    category = db.Column(db.String(40), nullable=False, index=True, default="hindi_fonts")

    title = db.Column(db.String(160), nullable=False)

    description = db.Column(db.Text, default="")

    version = db.Column(db.String(40), default="")

    # Stored file (relative path under static/uploads/downloads/).
    filename = db.Column(db.String(255), nullable=False)

    stored_name = db.Column(db.String(255), nullable=False)

    file_ext = db.Column(db.String(20), default="")

    size_bytes = db.Column(db.Integer, default=0)

    # Optional preview image (relative path under static/uploads/downloads/).
    image = db.Column(db.String(255), default="")

    download_count = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def category_label(self):
        return CATEGORIES.get(self.category, "Downloads")

    @property
    def size_human(self):
        size = self.size_bytes or 0
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "category_label": self.category_label,
            "title": self.title,
            "description": self.description,
            "version": self.version,
            "filename": self.filename,
            "file_ext": self.file_ext,
            "size_human": self.size_human,
            "image": self.image,
            "download_count": self.download_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Download {self.id} {self.category} {self.title!r}>"
