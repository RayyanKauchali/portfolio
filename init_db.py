import json
import os
from app import app, db
from models import Project, Skill, Todo # --- Import Todo ---

# --- IMPORTANT ---
# This script will DELETE your existing database and RECREATE it 
# from the .json files AND add default tasks.
# -----------------

PROJECTS_JSON_PATH = os.path.join(app.root_path, 'data', 'projects.json')
SKILLS_JSON_PATH = os.path.join(app.root_path, 'data', 'skills.json')

# --- NEW: DEFAULT 30-DAY TASK LIST ---
DEFAULT_TASKS = [
    {"task": "Review and update all project descriptions in the portfolio admin panel.", "category": "Portfolio"},
    {"task": "Start research for a new 'Deep Learning' project (e.g., StyleGAN or NLP Transformer).", "category": "Project"},
    {"task": "Learn one new MLOps concept (e.g., Kubeflow, MLflow).", "category": "Learning"},
    {"task": "Update 'About Me' page and check all links.", "category": "Portfolio"},
    {"task": "Write 500 words for a blog post about the 'Brain Tumor AI' project.", "category": "Project"},
    {"task": "Learn one new Data Engineering concept (e.g., dbt models, Airflow DAGs).", "category": "Learning"},
    {"task": "Add 2-3 new 'Beginner' projects to the portfolio.", "category": "Portfolio"},
    {"task": "Complete a tutorial on 'Microsoft Fabric'.", "category": "Learning"},
    {"task": "Refine the styling on the portfolio's 'Skills' page.", "category": "Portfolio"},
    {"task": "Begin coding the new 'Deep Learning' project.", "category": "Project"},
    {"task": "Learn advanced 'XAI' (Explainable AI) techniques (LIME/SHAP).", "category": "Learning"},
    {"task": "Add a new 'Certificate' to the admin panel.", "category": "Portfolio"},
    {"task": "Refactor the 'Emotion Detection' project's code for clarity.", "category": "Project"},
    {"task": "Find and add 3 new 'Data Analyst' projects.", "category": "Portfolio"},
    {"task": "Study one new cloud service on AWS (e.g., SageMaker).", "category": "Learning"},
    {"task": "Halfway check: Review all portfolio text for typos.", "category": "Portfolio"},
    {"task": "Implement a new feature on the 'AI Resume Analyzer' project.", "category": "Project"},
    {"task": "Learn one new 'Generative AI' concept (e.g., Diffusion models).", "category": "Learning"},
    {"task": "Add 2 new skills (with SVGs) to the admin panel.", "category": "Portfolio"},
    {"task": "Finalize and deploy the 'Deep Learning' project.", "category": "Project"},
    {"task": "Write the 'Project Detail' page for the new project.", "category": "Portfolio"},
    {"task": "Learn a new Python library (e.g., 'Polars' for dataframes).", "category": "Learning"},
    {"task": "Start research for the *next* new project (e.g., a 'Data Engineering' pipeline).", "category": "Project"},
    {"task": "Add a 'To-Do' list feature to the portfolio admin panel.", "category": "Portfolio"},
    {"task": "Learn Docker and containerize one of your Flask projects.", "category": "Learning"},
    {"task": "Begin coding the new 'Data Engineering' pipeline project.", "category": "Project"},
    {"task": "Learn how to write unit tests for a Flask app (pytest).", "category": "Learning"},
    {"task": "Update the 'Download Resume' PDF to the latest version.", "category": "Portfolio"},
    {"task": "Complete and deploy the 'Data Engineering' project.", "category": "Project"},
    {"task": "Plan the next 30 days of tasks.", "category": "Planning"}
]


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
            
        # --- NEW: Seed Default Tasks ---
        try:
            print(f"Seeding {len(DEFAULT_TASKS)} default tasks...")
            for i, task_data in enumerate(DEFAULT_TASKS):
                new_task = Todo(
                    task=task_data.get('task'),
                    category=task_data.get('category'),
                    # Set the very first task to "Active"
                    status="Active" if i == 0 else "Pending" 
                )
                db.session.add(new_task)
        except Exception as e:
            print(f"Could not seed default tasks: {e}")
        
        db.session.commit()
        print("Database has been initialized and seeded successfully!")
        print("You can now run 'python app.py' to start the server.")

if __name__ == '__main__':
    initialize_database()