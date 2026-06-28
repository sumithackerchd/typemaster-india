from datetime import datetime
from models import db


class Result(db.Model):

    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    language = db.Column(db.String(20))

    difficulty = db.Column(db.String(20))

    duration = db.Column(db.Integer)

    gross_wpm = db.Column(db.Integer)

    net_wpm = db.Column(db.Integer)

    cpm = db.Column(db.Integer)

    accuracy = db.Column(db.Float)

    errors = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )