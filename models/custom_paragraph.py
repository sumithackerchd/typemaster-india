from datetime import datetime

from . import db


# ---------------------------------------------------------------------------
# CustomParagraph
#
# User-owned typing content created via the "Custom Practice" feature.
# Only the owner (user_id) may view, edit, rename or delete their entries.
# ---------------------------------------------------------------------------


class CustomParagraph(db.Model):

    __tablename__ = "custom_paragraphs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title = db.Column(db.String(150), nullable=False, default="Untitled")

    content = db.Column(db.Text, nullable=False)

    language = db.Column(db.String(30), nullable=False, default="english")

    difficulty = db.Column(db.String(20), nullable=False, default="medium")

    category = db.Column(db.String(50), nullable=False, default="custom")

    word_count = db.Column(db.Integer, default=0)

    favorite = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "language": self.language,
            "difficulty": self.difficulty,
            "category": self.category,
            "word_count": self.word_count,
            "favorite": self.favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<CustomParagraph {self.id} u{self.user_id} {self.title!r}>"
