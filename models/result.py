from datetime import datetime
from . import db

class Result(db.Model):

    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    language = db.Column(db.String(20))

    gross_wpm = db.Column(db.Float)

    net_wpm = db.Column(db.Float)

    accuracy = db.Column(db.Float)

    errors = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)