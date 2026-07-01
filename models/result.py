from datetime import datetime
from models import db


class Result(db.Model):

    __tablename__ = "results"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    language = db.Column(
        db.String(20),
        nullable=False,
        default="English"
    )

    difficulty = db.Column(
        db.String(20),
        nullable=False,
        default="Easy"
    )

    duration = db.Column(
        db.Integer,
        nullable=False,
        default=60
    )

    gross_wpm = db.Column(
        db.Integer,
        default=0
    )

    net_wpm = db.Column(
        db.Integer,
        default=0
    )

    cpm = db.Column(
        db.Integer,
        default=0
    )

    accuracy = db.Column(
        db.Float,
        default=0
    )

    errors = db.Column(
        db.Integer,
        default=0
    )

    # -----------------------------
    # Certificate identity (unique per result)
    # -----------------------------

    certificate_id = db.Column(
        db.String(40),
        unique=True,
        nullable=True
    )

    verify_token = db.Column(
        db.String(64),
        unique=True,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Result {self.id}>"
