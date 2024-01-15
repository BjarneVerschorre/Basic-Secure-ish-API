from basic_api import db
from datetime import datetime

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    api_key = db.Column(db.String(36), unique=True)
    salt = db.Column(db.String(16))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, api_key, salt, user_id, created_at = datetime.utcnow()):
        self.name = name
        self.api_key = api_key
        self.salt = salt
        self.created_at = created_at
        self.user_id = user_id
        
    def revoke(self):
        ''' Revokes the API key'''
        db.session.delete(self)
        db.session.commit()