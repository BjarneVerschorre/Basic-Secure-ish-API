from basic_api import db
from datetime import datetime

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(97))
    salt = db.Column(db.String(16))
    registerd_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    api_key_rel = db.relationship('ApiKey', backref='users', lazy=True)

    def __init__(self, username, password, salt, registerd_on = datetime.utcnow()):
        self.username = username
        self.password = password
        self.salt = salt
        registerd_on = registerd_on
