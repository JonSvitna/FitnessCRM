from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Trainer(db.Model):
    """Trainer model"""
    __tablename__ = 'trainers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    specialization = db.Column(db.String(200))
    certification = db.Column(db.String(200))
    experience = db.Column(db.Integer)
    bio = db.Column(db.Text)
    hourly_rate = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='trainer', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('Session', backref='trainer', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'specialization': self.specialization,
            'certification': self.certification,
            'experience': self.experience,
            'bio': self.bio,
            'hourly_rate': self.hourly_rate,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Client(db.Model):
    """Client model"""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    age = db.Column(db.Integer)
    goals = db.Column(db.Text)
    medical_conditions = db.Column(db.Text)
    emergency_contact = db.Column(db.String(200))
    emergency_phone = db.Column(db.String(20))
    status = db.Column(db.String(50), default='active')  # active, inactive, pending
    membership_type = db.Column(db.String(50))  # monthly, quarterly, annual
    start_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('Assignment', backref='client', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('Session', backref='client', lazy=True, cascade='all, delete-orphan')
    progress_records = db.relationship('ProgressRecord', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'age': self.age,
            'goals': self.goals,
            'medical_conditions': self.medical_conditions,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'status': self.status,
            'membership_type': self.membership_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Assignment(db.Model):
    """Assignment model - links trainers and clients"""
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'client_id': self.client_id,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Session(db.Model):
    """Training session model"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    session_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    session_type = db.Column(db.String(100))  # personal, group, online, etc.
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled, no-show
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'client_id': self.client_id,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'duration': self.duration,
            'session_type': self.session_type,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class ProgressRecord(db.Model):
    """Client progress tracking model"""
    __tablename__ = 'progress_records'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    record_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    weight = db.Column(db.Float)
    body_fat_percentage = db.Column(db.Float)
    measurements = db.Column(db.JSON)  # Store multiple measurements as JSON
    notes = db.Column(db.Text)
    photos = db.Column(db.JSON)  # Store photo URLs as JSON array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'weight': self.weight,
            'body_fat_percentage': self.body_fat_percentage,
            'measurements': self.measurements,
            'notes': self.notes,
            'photos': self.photos,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class Payment(db.Model):
    """Payment tracking model"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))  # credit_card, cash, check, etc.
    payment_type = db.Column(db.String(50))  # membership, session, product, etc.
    status = db.Column(db.String(50), default='completed')  # pending, completed, refunded, failed
    transaction_id = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    client = db.relationship('Client', backref='payments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'payment_type': self.payment_type,
            'status': self.status,
            'transaction_id': self.transaction_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class WorkoutPlan(db.Model):
    """Workout plan template model"""
    __tablename__ = 'workout_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.String(50))  # beginner, intermediate, advanced
    duration_weeks = db.Column(db.Integer)
    exercises = db.Column(db.JSON)  # Store workout exercises as JSON
    public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    trainer = db.relationship('Trainer', backref='workout_plans')
    
    def to_dict(self):
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'name': self.name,
            'description': self.description,
            'difficulty_level': self.difficulty_level,
            'duration_weeks': self.duration_weeks,
            'exercises': self.exercises,
            'public': self.public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
