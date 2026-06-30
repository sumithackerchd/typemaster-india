from datetime import datetime

from flask_login import UserMixin

from models import db


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    mobile = db.Column(
        db.String(15),
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    is_admin = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )


    # -----------------------------
# Gamification
# -----------------------------

xp = db.Column(
    db.Integer,
    default=0
)

level = db.Column(
    db.Integer,
    default=1
)

current_streak = db.Column(
    db.Integer,
    default=0
)

best_streak = db.Column(
    db.Integer,
    default=0
)

last_test_date = db.Column(
    db.Date,
    nullable=True
)

created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # One User -> Many Results
results = db.relationship(
        "Result",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

def __repr__(self):

        return f"<User {self.username}>"