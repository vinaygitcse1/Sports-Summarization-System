from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    summaries = db.relationship('Summary', backref='author', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    original_text = db.Column(db.Text)
    summary_text = db.Column(db.Text)
    summary_type = db.Column(db.String(50))  # 'text' or 'audio'
    language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    processing_time = db.Column(db.Float)  # in seconds
    word_count = db.Column(db.Integer)
    
    # Events extracted
    key_events = db.Column(db.JSON)  # Store as JSON

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))