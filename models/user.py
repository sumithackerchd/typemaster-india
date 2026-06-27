from datetime import datetime
from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    username = db.Column(db.String(50), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    mobile = db.Column(db.String(15), nullable=False)

    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)