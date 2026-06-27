from . import db

class Paragraph(db.Model):

    __tablename__ = "paragraphs"

    id = db.Column(db.Integer, primary_key=True)

    language = db.Column(db.String(30))

    difficulty = db.Column(db.String(20))

    category = db.Column(db.String(50))

    content = db.Column(db.Text)