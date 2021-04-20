import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "Sample Secret Key"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'postgresql://postgres:admin123@localhost/restaurant'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

