import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

SECRET_KEY = 'your_very_secret_key_change_this'
ADMIN_PASSWORD = 'Yanray@123'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'portfolio.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False