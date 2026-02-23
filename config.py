import os
from datetime import timedelta

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Database - Using SQLite for local, PostgreSQL for cloud
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg'}
    ALLOWED_TEXT_EXTENSIONS = {'txt', 'csv', 'json'}
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # NLP Model Configuration
    NLP_MODEL_NAME = "facebook/bart-large-cnn"
    SUMMARIZATION_MAX_LENGTH = 150
    SUMMARIZATION_MIN_LENGTH = 30
    
    # Cloud Storage (Example with AWS S3 - Optional)
    USE_CLOUD_STORAGE = False
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    S3_BUCKET = os.environ.get('S3_BUCKET')