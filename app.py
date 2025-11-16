import os
import json
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, g,
    send_from_directory
)
from models import db, Project, Certificate, Skill # Import Skill
import config
from functools import wraps

# --- App Initialization ---
app = Flask(__name__)
app.config.from_object(config)

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db.init_app(app)

# --- NEW: CREATE TABLES ON STARTUP ---
# This function will run once when the app starts.
# It checks if the tables exist and creates them if they don't.
# This is a robust way to ensure your app doesn't crash on a new deploy.
@app.before_request
def create_tables():
    # The 'before_first_request' hook is deprecated, so we use a
    # global flag 'db_initialized' to ensure this only runs ONCE
    # per server process.
    if not getattr(g, 'db_initialized', False):
        with app.app_context():
            print("--- ENSURING DATABASE TABLES EXIST ---")
            db.create_all() # This creates tables if they don't exist
            print("--- DATABASE TABLES CHECKED ---")
        g.db_initialized = True
# --- END NEW CODE ---


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
        # This error is now fine, it just means tables are empty
        project_count = 0
        skill_count = 0
        
    return dict(
        project_count=project_count,
        skill_count=skill_count
    )
    
# ---  DATABASE INIT FUNCTION (MOVED FROM init_db.py) ---
def initialize_database():
    """
    Drops and recreates all tables, then seeds projects and skills
    from the JSON files. This is called by the secret setup route.
    """
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
        SKILLS_JSON_PATH = os.path.join(app.root_path, 'data', 'skills.json')
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
    
    # Check if DB is empty to show setup link
    db_is_empty = (len(projects) == 0 and len(skills) == 0)
    
    return render_template(
        'admin_dashboard.html',
        projects=projects,
        certificates=certificates,
        skills=skills,
        db_is_empty=db_is_empty
    )

# --- NEW: SECRET DATABASE SETUP ROUTE ---
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
    try:
        new_project = Project(
            title=request.form.get('title'),
            role=request.form.get('role'),
            tech=request.form.get('tech'),
            description=request.form.get('description'),
            image=request.form.get('image')
        )
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
    try:
        new_certificate = Certificate(
            title=request.form.get('title'),
            provider=request.form.get('provider'),
            icon=request.form.get('icon')
        )
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
    try:
        new_skill = Skill(
            category=request.form.get('category'),
            name=request.form.get('name'),
            svg=request.form.get('svg')
        )
        db.session.add(new_skill)
        db.session.commit()
        flash('Skill added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding skill: {e}', 'danger')
    return redirect(url_for('admin_dashboard') + '#skills') # Go to skills tab

# --- EDIT ITEMS ---

@app.route('/admin/edit/project/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
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

# --- DELETE ITEMS (Fixed: Methods set to POST) ---

@app.route('/admin/delete/project/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/certificate/<int:id>', methods=['POST'])
@login_required
def delete_certificate(id):
    certificate = Certificate.query.get_or_404(id)
    db.session.delete(certificate)
    db.session.commit()
    flash('Certificate deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#certificates')

@app.route('/admin/delete/skill/<int:id>', methods=['POST'])
@login_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#skills')

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)