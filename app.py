import os
import json
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, g,
    send_from_directory
)
from models import db, Project, Certificate, Skill, Todo # --- IMPORT TODO ---
import config
from functools import wraps
from sqlalchemy import or_ # --- IMPORT OR_ ---

# --- App Initialization ---
app = Flask(__name__)
app.config.from_object(config)

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db.init_app(app)

# --- CREATE TABLES ON STARTUP ---
@app.before_request
def create_tables():
    if not getattr(g, 'db_initialized', False):
        with app.app_context():
            print("--- ENSURING DATABASE TABLES EXIST ---")
            db.create_all() 
            print("--- DATABASE TABLES CHECKED ---")
        g.db_initialized = True

# --- Admin Authentication Helper ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Context Processors ---
@app.context_processor
def inject_global_vars():
    try:
        project_count = db.session.query(Project).count()
        skill_count = db.session.query(Skill).count() 
    except Exception as e:
        project_count = 0
        skill_count = 0
        
    return dict(
        project_count=project_count,
        skill_count=skill_count
    )
    
# ---  DATABASE INIT FUNCTION ---
def initialize_database():
    try:
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()

        # --- Seed Projects ---
        PROJECTS_JSON_PATH = os.path.join(app.root_path, 'data', 'projects.json')
        try:
            with open(PROJECTS_JSON_PATH, 'r') as f:
                projects_seed = json.load(f)
            print(f"Seeding {len(projects_seed)} projects...")
            for p in projects_seed:
                new_project = Project(title=p.get('title'), role=p.get('role'), tech=p.get('tech'), description=p.get('description'), image=p.get('image'))
                db.session.add(new_project)
        except Exception as e:
            print(f"Could not seed projects: {e}")

        # --- Seed Skills ---
        SKILLS_JSON_PATH = os.path.join(app.root_path, 'data', 'skills.json')
        try:
            with open(SKILLS_JSON_PATH, 'r') as f:
                skills_seed = json.load(f)
            print(f"Seeding skills...")
            for category in skills_seed:
                cat_name = category.get('category')
                for skill in category.get('skills', []):
                    new_skill = Skill(category=cat_name, name=skill.get('name'), svg=skill.get('svg'))
                    db.session.add(new_skill)
        except Exception as e:
            print(f"Could not seed skills: {e}")
            
        # --- Seed Default Tasks ---
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
        try:
            print(f"Seeding {len(DEFAULT_TASKS)} default tasks...")
            for i, task_data in enumerate(DEFAULT_TASKS):
                new_task = Todo(
                    task=task_data.get('task'),
                    category=task_data.get('category'),
                    status="Active" if i == 0 else "Pending" 
                )
                db.session.add(new_task)
        except Exception as e:
            print(f"Could not seed default tasks: {e}")
        
        db.session.commit()
        print("Database has been initialized and seeded successfully!")
        return True
    except Exception as e:
        print(f"An error occurred during DB initialization: {e}")
        db.session.rollback()
        return False


# --- PUBLIC ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    all_projects = Project.query.order_by(Project.id.desc()).all()
    return render_template('projects.html', projects=all_projects)

@app.route('/skills')
def skills():
    skills_data_from_db = Skill.query.all()
    
    skills_data = {}
    for skill in skills_data_from_db:
        if skill.category not in skills_data:
            skills_data[skill.category] = []
        skills_data[skill.category].append({
            "name": skill.name,
            "svg": skill.svg
        })
    
    skills_list = []
    for category_name, skills_list_items in skills_data.items():
        skills_list.append({
            "category": category_name,
            "skills": skills_list_items
        })
        
    return render_template('skills.html', skills_data=skills_list)

@app.route('/certificates')
def certificates():
    all_certificates = Certificate.query.order_by(Certificate.id.desc()).all()
    return render_template('certificates.html', certificates=all_certificates)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/download-resume')
def download_resume():
    try:
        return send_from_directory(
            app.config['DATA_DIR'],
            'RayyanKauchali_Resume-1.pdf',
            as_attachment=True
        )
    except FileNotFoundError:
        flash("Resume file not found on server.", "danger")
        return redirect(request.referrer or url_for('index'))

# --- ADMIN ROUTES ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    projects = Project.query.order_by(Project.id).all()
    certificates = Certificate.query.order_by(Certificate.id).all()
    skills = Skill.query.order_by(Skill.category, Skill.id).all()
    
    # --- NEW: Fetch all Todo tasks, split by status ---
    todos_active = Todo.query.filter_by(status='Active').order_by(Todo.id.asc()).all()
    todos_pending = Todo.query.filter_by(status='Pending').order_by(Todo.id.asc()).all()
    todos_paused = Todo.query.filter_by(status='Paused').order_by(Todo.id.asc()).all()
    todos_done = Todo.query.filter_by(status='Done').order_by(Todo.completed_at.desc()).limit(10).all()

    # Check if DB is empty to show setup link
    db_is_empty = (len(projects) == 0 and len(skills) == 0 and len(todos_active) == 0)
    
    return render_template(
        'admin_dashboard.html',
        projects=projects,
        certificates=certificates,
        skills=skills,
        todos_active=todos_active,
        todos_pending=todos_pending,
        todos_paused=todos_paused,
        todos_done=todos_done,
        db_is_empty=db_is_empty
    )

@app.route('/admin/first-time-setup-run-once')
@login_required
def first_time_setup():
    with app.app_context():
        if initialize_database():
            flash('SUCCESS: Database has been initialized and seeded!', 'success')
        else:
            flash('ERROR: Database initialization failed. Check logs.', 'danger')
    return redirect(url_for('admin_dashboard'))

# --- ADD ITEMS ---
@app.route('/admin/add/project', methods=['POST'])
@login_required
def add_project():
    # ... (existing code, no changes)
    try:
        new_project = Project(title=request.form.get('title'), role=request.form.get('role'), tech=request.form.get('tech'), description=request.form.get('description'), image=request.form.get('image'))
        db.session.add(new_project)
        db.session.commit()
        flash('Project added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding project: {e}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add/certificate', methods=['POST'])
@login_required
def add_certificate():
    # ... (existing code, no changes)
    try:
        new_certificate = Certificate(title=request.form.get('title'), provider=request.form.get('provider'), icon=request.form.get('icon'))
        db.session.add(new_certificate)
        db.session.commit()
        flash('Certificate added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding certificate: {e}', 'danger')
    return redirect(url_for('admin_dashboard') + '#certificates')

@app.route('/admin/add/skill', methods=['POST'])
@login_required
def add_skill():
    # ... (existing code, no changes)
    try:
        new_skill = Skill(category=request.form.get('category'), name=request.form.get('name'), svg=request.form.get('svg'))
        db.session.add(new_skill)
        db.session.commit()
        flash('Skill added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding skill: {e}', 'danger')
    return redirect(url_for('admin_dashboard') + '#skills')

# --- NEW: ADD TODO ---
@app.route('/admin/add/todo', methods=['POST'])
@login_required
def add_todo():
    try:
        new_todo = Todo(
            task=request.form.get('task'),
            category=request.form.get('category'),
            status="Pending" # Always add new tasks as Pending
        )
        db.session.add(new_todo)
        db.session.commit()
        flash('To-Do task added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding task: {e}', 'danger')
    return redirect(url_for('admin_dashboard') + '#roadmap')

# --- EDIT ITEMS ---

@app.route('/admin/edit/project/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    # ... (existing code, no changes)
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        try:
            project.title = request.form.get('title')
            project.role = request.form.get('role')
            project.tech = request.form.get('tech')
            project.description = request.form.get('description')
            project.image = request.form.get('image')
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {e}', 'danger')
    return render_template('edit_project.html', project=project)

@app.route('/admin/edit/certificate/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_certificate(id):
    # ... (existing code, no changes)
    certificate = Certificate.query.get_or_404(id)
    if request.method == 'POST':
        try:
            certificate.title = request.form.get('title')
            certificate.provider = request.form.get('provider')
            certificate.icon = request.form.get('icon')
            db.session.commit()
            flash('Certificate updated successfully!', 'success')
            return redirect(url_for('admin_dashboard') + '#certificates')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating certificate: {e}', 'danger')
    return render_template('edit_certificate.html', certificate=certificate)

@app.route('/admin/edit/skill/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_skill(id):
    # ... (existing code, no changes)
    skill = Skill.query.get_or_404(id)
    if request.method == 'POST':
        try:
            skill.category = request.form.get('category')
            skill.name = request.form.get('name')
            skill.svg = request.form.get('svg')
            db.session.commit()
            flash('Skill updated successfully!', 'success')
            return redirect(url_for('admin_dashboard') + '#skills')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating skill: {e}', 'danger')
    return render_template('edit_skill.html', skill=skill)

# --- NEW: EDIT TODO ---
@app.route('/admin/edit/todo/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_todo(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        try:
            task.task = request.form.get('task')
            task.category = request.form.get('category')
            task.status = request.form.get('status')
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('admin_dashboard') + '#roadmap')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating task: {e}', 'danger')
    return render_template('edit_todo.html', task=task)

# --- DELETE ITEMS ---

@app.route('/admin/delete/project/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    # ... (existing code, no changes)
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/certificate/<int:id>', methods=['POST'])
@login_required
def delete_certificate(id):
    # ... (existing code, no changes)
    certificate = Certificate.query.get_or_404(id)
    db.session.delete(certificate)
    db.session.commit()
    flash('Certificate deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#certificates')

@app.route('/admin/delete/skill/<int:id>', methods=['POST'])
@login_required
def delete_skill(id):
    # ... (existing code, no changes)
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#skills')

# --- NEW: DELETE TODO ---
@app.route('/admin/delete/todo/<int:id>', methods=['POST'])
@login_required
def delete_todo(id):
    task = Todo.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#roadmap')

# --- NEW: UPDATE TODO STATUS ---

def _set_active_task(task_to_activate):
    # Find any other active/paused task and set it to pending
    other_task = Todo.query.filter(or_(Todo.status == 'Active', Todo.status == 'Paused')).first()
    if other_task:
        other_task.status = 'Pending'
    # Set the new task to active
    task_to_activate.status = 'Active'

@app.route('/admin/todo/set_active/<int:id>', methods=['POST'])
@login_required
def set_active_task(id):
    task = Todo.query.get_or_404(id)
    _set_active_task(task)
    db.session.commit()
    flash(f"Task '{task.task[:30]}...' set to Active.", 'success')
    return redirect(url_for('admin_dashboard') + '#roadmap')

@app.route('/admin/todo/set_pause/<int:id>', methods=['POST'])
@login_required
def set_pause_task(id):
    task = Todo.query.get_or_404(id)
    task.status = 'Paused'
    db.session.commit()
    flash(f"Task '{task.task[:30]}...' has been paused.", 'info')
    return redirect(url_for('admin_dashboard') + '#roadmap')

@app.route('/admin/todo/set_complete/<int:id>', methods=['POST'])
@login_required
def set_complete_task(id):
    task = Todo.query.get_or_404(id)
    task.status = 'Done'
    task.completed_at = db.func.now()
    
    # Find the next task in the "Pending" list
    next_task = Todo.query.filter_by(status='Pending').order_by(Todo.id.asc()).first()
    if next_task:
        _set_active_task(next_task)
        flash(f"Task completed! Next task: '{next_task.task[:30]}...'", 'success')
    else:
        flash("Task completed! No more pending tasks.", 'success')
        
    db.session.commit()
    return redirect(url_for('admin_dashboard') + '#roadmap')


# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)