from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    # ... (existing code, no changes)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    tech = db.Column(db.String(300), nullable=True) # Comma-separated string
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f'<Project {self.title}>'

class Certificate(db.Model):
    # ... (existing code, no changes)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(100), nullable=True) # e.g., "fa-solid fa-award"

    def __repr__(self):
        return f'<Certificate {self.title}>'

class Skill(db.Model):
    # ... (existing code, no changes)
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    svg = db.Column(db.Text, nullable=True) # Storing the full SVG string

    def __repr__(self):
        return f'<Skill {self.name}>'

# --- NEW MODEL ---
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True, default="General")
    # Statuses: "Active", "Pending", "Paused", "Done"
    status = db.Column(db.String(50), nullable=False, default='Pending') 
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Todo {self.task[:30]}>'