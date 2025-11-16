from app import app, initialize_database

if __name__ == '__main__':
    with app.app_context():
        initialize_database()