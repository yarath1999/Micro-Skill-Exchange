from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'provider' or 'seeker'
    name = db.Column(db.String(100))
    password = db.Column(db.String(200), nullable=False)

    # Common Profile Fields
    description = db.Column(db.Text)
    profile_picture = db.Column(db.String(300))

    # Seeker-specific Fields
    skill = db.Column(db.String(200))
    experience = db.Column(db.String(500))
    qualification = db.Column(db.String(200))
    total_income = db.Column(db.Integer, default=0)

    # Provider-specific Fields
    work = db.Column(db.Text)
    jobs = db.Column(db.String(300))
    skills_needed = db.Column(db.String(300))
    contact_details = db.Column(db.String(300))

    # Other Optional Fields
    interest = db.Column(db.String(300))
    availability = db.Column(db.String(100))

    # Relationships
    applications = db.relationship('Application', backref='user', lazy=True)

class Opportunity(db.Model):
    __tablename__ = 'opportunity'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='opportunity', lazy=True)

class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunity.id'), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    income_awarded = db.Column(db.Boolean, default=False)
