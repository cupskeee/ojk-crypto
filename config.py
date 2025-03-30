import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-dev-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join('instance', 'app.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')