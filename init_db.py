import json
import os
from app import app, db
from models import Project, Skill # Import Skill model

# --- IMPORTANT ---
# This script will DELETE your existing database and RECREATE it 
# from the .json files.
# -----------------

PROJECTS_JSON_PATH = os.path.join(app.root_path, 'data', 'projects.json')
SKILLS_JSON_PATH = os.path.join(app.root_path, 'data', 'skills.json')

def initialize_database():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()

        # --- Seed Projects ---
        try:
            with open(PROJECTS_JSON_PATH, 'r') as f:
                projects_seed = json.load(f)
            print(f"Seeding {len(projects_seed)} projects...")
            for p in projects_seed:
                new_project = Project(
                    title=p.get('title'),
                    role=p.get('role'),
                    tech=p.get('tech'),
                    description=p.get('description'),
                    image=p.get('image')
                )
                db.session.add(new_project)
        except Exception as e:
            print(f"Could not seed projects: {e}")

        # --- Seed Skills ---
        try:
            with open(SKILLS_JSON_PATH, 'r') as f:
                skills_seed = json.load(f)
            print(f"Seeding skills...")
            for category in skills_seed:
                cat_name = category.get('category')
                for skill in category.get('skills', []):
                    new_skill = Skill(
                        category=cat_name,
                        name=skill.get('name'),
                        svg=skill.get('svg')
                    )
                    db.session.add(new_skill)
        except Exception as e:
            print(f"Could not seed skills: {e}")
        
        # Certificates start blank.

        db.session.commit()
        print("Database has been initialized and seeded successfully!")
        print("You can now run 'python app.py' to start the server.")

if __name__ == '__main__':
    initialize_database()