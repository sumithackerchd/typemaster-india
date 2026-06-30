from datetime import datetime

from . import db


# ---------------------------------------------------------------------------
# Paragraph
#
# Central store for all typing content used by the Mock Test System.
# Content is kept in the database (primary source) and mirrored to JSON
# files as a fallback (see utils/seed_paragraphs.py).
#
# language   : "english" | "hindi"
# category   : slug, e.g. "ssc", "railway", "random_words" ...
# difficulty : "easy" | "medium" | "hard"
# kind       : "paragraph" | "words"
# ---------------------------------------------------------------------------


class Paragraph(db.Model):

    __tablename__ = "paragraphs"

    id = db.Column(db.Integer, primary_key=True)

    language = db.Column(db.String(30), nullable=False, default="english", index=True)

    category = db.Column(db.String(50), nullable=False, default="random_paragraph", index=True)

    difficulty = db.Column(db.String(20), nullable=False, default="easy", index=True)

    kind = db.Column(db.String(20), nullable=False, default="paragraph", index=True)

    content = db.Column(db.Text, nullable=False)

    word_count = db.Column(db.Integer, default=0)

    source = db.Column(db.String(20), default="seed")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "language": self.language,
            "category": self.category,
            "difficulty": self.difficulty,
            "kind": self.kind,
            "content": self.content,
            "word_count": self.word_count,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Paragraph {self.id} {self.language}/{self.category}/{self.difficulty}>"
