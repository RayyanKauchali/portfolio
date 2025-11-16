import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# --- SECRET CONFIGURATION ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'your_local_default_secret_key')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'your_local_default_password')

# --- DATABASE CONFIGURATION (UPDATED) ---
# Check if a DATABASE_URL is set in the environment (for Render)
if os.environ.get('DATABASE_URL'):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
else:
    # Fallback to local SQLite database if no DATABASE_URL is found
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'portfolio.db')

SQLALCHEMY_TRACK_MODIFICATIONS = False