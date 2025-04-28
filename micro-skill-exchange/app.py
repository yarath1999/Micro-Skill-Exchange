from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Opportunity, Application
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('type', 'general')
        name = request.form.get('name')
        skill = request.form.get('skill')
        experience = request.form.get('experience')
        interest = request.form.get('interest')
        availability = request.form.get('availability')

        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please login or use another email.', 'error')
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password, role=role,
                        name=name, skill=skill, experience=experience,
                        interest=interest, availability=availability)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    opportunities = Opportunity.query.all()

    applied_opportunity_ids = []
    if user.role.lower() == 'seeker':
        applied_opportunity_ids = [app.opportunity_id for app in Application.query.filter_by(user_id=user.id).all()]

    return render_template('dashboard.html', user=user, opportunities=opportunities, applied_opportunity_ids=applied_opportunity_ids)

@app.route('/dashboard/add', methods=['GET', 'POST'])
def add_opportunity():
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.role.lower() != 'provider':
        flash('Only Providers can add opportunities.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']

        new_opportunity = Opportunity(
            title=title,
            description=description,
            location=location,
            created_by=user.id
        )
        db.session.add(new_opportunity)
        db.session.commit()

        flash('Opportunity added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_opportunity.html')

@app.route('/dashboard/edit/<int:id>', methods=['GET', 'POST'])
def edit_opportunity(id):
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    opportunity = Opportunity.query.get_or_404(id)

    if opportunity.created_by != user.id:
        flash('You are not allowed to edit this opportunity.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        opportunity.title = request.form['title']
        opportunity.description = request.form['description']
        opportunity.location = request.form.get('location', opportunity.location)
        db.session.commit()

        flash('Opportunity updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_opportunity.html', opportunity=opportunity)

@app.route('/dashboard/delete/<int:id>', methods=['POST'])
def delete_opportunity(id):
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    opportunity = Opportunity.query.get_or_404(id)

    if opportunity.created_by != user.id:
        flash('You are not allowed to delete this opportunity.', 'error')
        return redirect(url_for('dashboard'))

    db.session.delete(opportunity)
    db.session.commit()

    flash('Opportunity deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/apply/<int:opportunity_id>', methods=['POST'])
def apply_opportunity(opportunity_id):
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.role.lower() != 'seeker':
        flash('Only Seekers can apply for opportunities.', 'error')
        return redirect(url_for('dashboard'))

    existing_application = Application.query.filter_by(
        user_id=user.id,
        opportunity_id=opportunity_id
    ).first()

    if existing_application:
        flash('You have already applied for this opportunity.', 'info')
    else:
        application = Application(user_id=user.id, opportunity_id=opportunity_id)
        db.session.add(application)
        db.session.commit()
        flash('Application submitted successfully!', 'success')

    return redirect(url_for('dashboard'))

@app.route('/my_applications')
def my_applications():
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.role.lower() != 'seeker':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))

    applications = Application.query.filter_by(user_id=user.id).all()

    # 🛠️ Get related opportunities:
    opportunities = []
    for app in applications:
        opportunity = Opportunity.query.get(app.opportunity_id)
        if opportunity:
            opportunities.append({
                'application': app,
                'opportunity': opportunity
            })

    return render_template('my_applications.html', user=user, opportunities=opportunities)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
