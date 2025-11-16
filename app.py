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
    """
    Injects project and SKILL counts into all templates
    for the home page stats.
    """
    try:
        project_count = db.session.query(Project).count()
        # --- MODIFIED THIS LINE ---
        skill_count = db.session.query(Skill).count() 
    except Exception as e:
        project_count = 0
        skill_count = 0 # <-- MODIFIED
        
    return dict(
        project_count=project_count,
        skill_count=skill_count # <-- MODIFIED
    )

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
    
    # Re-structure data for the template
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
    return render_template('admin_dashboard.html', projects=projects, certificates=certificates, skills=skills)

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
    return redirect(url_for('admin_dashboard'))

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

# --- EDIT ITEMS (NEW) ---

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

# --- DELETE ITEMS (Updated to POST for safety) ---

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
    with app.app_context():
        try:
            db.create_all() 
        except Exception as e:
            print(f"Database tables might already exist. Error: {e}")
    app.run(debug=True)