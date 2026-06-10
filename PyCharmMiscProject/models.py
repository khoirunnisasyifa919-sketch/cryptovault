from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Message(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    plain_text = db.Column(db.Text)

    encrypted_text = db.Column(db.Text)

    algorithm = db.Column(db.String(50))

    signature = db.Column(db.String(200))

    created_at = db.Column(db.DateTime)

    qr_path = db.Column(db.String(200))
