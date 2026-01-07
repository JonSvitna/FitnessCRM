from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from core.entity import BaseEntity
from core.relationship import RelationType

db = SQLAlchemy()

# Import User model (defined separately for auth)
from models.user import User

class Trainer(db.Model, BaseEntity):
    """Trainer model with EspoCRM-inspired structure"""
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
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete support
    
    # Relationships
    assignments = db.relationship('Assignment', backref='trainer', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('Session', backref='trainer', lazy=True, cascade='all, delete-orphan')
    
    @classmethod
    def get_relationship_defs(cls):
        """Define relationships for this entity"""
        return {
            'assignments': {
                'type': RelationType.ONE_TO_MANY.value,
                'entity': 'Assignment',
                'foreign_key': 'trainer_id'
            },
            'sessions': {
                'type': RelationType.ONE_TO_MANY.value,
                'entity': 'Session',
                'foreign_key': 'trainer_id'
            }
        }
    
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
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }

class Client(db.Model, BaseEntity):
    """Client model with EspoCRM-inspired structure"""
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
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete support
    
    # Relationships
    assignments = db.relationship('Assignment', backref='client', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('Session', backref='client', lazy=True, cascade='all, delete-orphan')
    progress_records = db.relationship('ProgressRecord', backref='client', lazy=True, cascade='all, delete-orphan')
    
    @classmethod
    def get_relationship_defs(cls):
        """Define relationships for this entity"""
        return {
            'assignments': {
                'type': RelationType.ONE_TO_MANY.value,
                'entity': 'Assignment',
                'foreign_key': 'client_id'
            },
            'sessions': {
                'type': RelationType.ONE_TO_MANY.value,
                'entity': 'Session',
                'foreign_key': 'client_id'
            },
            'progress_records': {
                'type': RelationType.ONE_TO_MANY.value,
                'entity': 'ProgressRecord',
                'foreign_key': 'client_id'
            }
        }
    
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
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }

class Assignment(db.Model, BaseEntity):
    """Assignment model - links trainers and clients with EspoCRM-inspired structure"""
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete support
    
    @classmethod
    def get_relationship_defs(cls):
        """Define relationships for this entity"""
        return {
            'trainer': {
                'type': RelationType.MANY_TO_ONE.value,
                'entity': 'Trainer',
                'foreign_key': 'trainer_id'
            },
            'client': {
                'type': RelationType.MANY_TO_ONE.value,
                'entity': 'Client',
                'foreign_key': 'client_id'
            }
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'client_id': self.client_id,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }

class Session(db.Model):
    """Training session model"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    session_date = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)  # Calculated from session_date + duration
    duration = db.Column(db.Integer, default=60)  # in minutes
    session_type = db.Column(db.String(100))  # personal, group, online, etc.
    location = db.Column(db.String(200))  # Gym, Online, Client's Home, etc.
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled, no-show
    recurring_session_id = db.Column(db.Integer, db.ForeignKey('recurring_sessions.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_end_time(self):
        """Calculate end_time from session_date + duration if not set"""
        if self.end_time:
            return self.end_time
        if self.session_date and self.duration:
            from datetime import timedelta
            return self.session_date + timedelta(minutes=self.duration)
        return None
    
    def to_dict(self):
        end_time = self.get_end_time()
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'client_id': self.client_id,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'end_time': end_time.isoformat() if end_time else None,
            'duration': self.duration,
            'session_type': self.session_type,
            'location': self.location,
            'notes': self.notes,
            'status': self.status,
            'recurring_session_id': self.recurring_session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class RecurringSession(db.Model):
    """Recurring session template"""
    __tablename__ = 'recurring_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)  # Optional end date
    start_time = db.Column(db.Time, nullable=False)  # Time of day
    duration = db.Column(db.Integer, default=60)  # in minutes
    session_type = db.Column(db.String(100))
    location = db.Column(db.String(200))
    recurrence_pattern = db.Column(db.String(50), nullable=False)  # daily, weekly, biweekly, monthly
    recurrence_days = db.Column(db.JSON)  # Days of week [0-6] for weekly patterns
    notes = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('Session', backref='recurring_template', lazy=True, foreign_keys='Session.recurring_session_id')
    trainer = db.relationship('Trainer', backref='recurring_sessions')
    client = db.relationship('Client', backref='recurring_sessions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'client_id': self.client_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'duration': self.duration,
            'session_type': self.session_type,
            'location': self.location,
            'recurrence_pattern': self.recurrence_pattern,
            'recurrence_days': self.recurrence_days,
            'notes': self.notes,
            'active': self.active,
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
    payment_method = db.Column(db.String(50))  # credit_card, cash, check, stripe, etc.
    payment_type = db.Column(db.String(50))  # membership, session, product, subscription, etc.
    status = db.Column(db.String(50), default='completed')  # pending, completed, refunded, failed
    transaction_id = db.Column(db.String(200))  # Stripe payment intent ID or charge ID
    stripe_payment_intent_id = db.Column(db.String(200))  # Stripe PaymentIntent ID
    stripe_charge_id = db.Column(db.String(200))  # Stripe Charge ID
    stripe_customer_id = db.Column(db.String(200))  # Stripe Customer ID
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

class Settings(db.Model):
    """Application settings and configuration"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    # Business profile
    business_name = db.Column(db.String(200))
    owner_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    website = db.Column(db.String(200))
    logo_url = db.Column(db.String(500))
    
    # SendGrid API Configuration
    sendgrid_api_key = db.Column(db.String(500))
    sendgrid_from_email = db.Column(db.String(120))
    sendgrid_from_name = db.Column(db.String(100))
    sendgrid_enabled = db.Column(db.Boolean, default=False)
    
    # Twilio API Configuration
    twilio_account_sid = db.Column(db.String(500))
    twilio_auth_token = db.Column(db.String(500))
    twilio_phone_number = db.Column(db.String(20))
    twilio_enabled = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary, optionally masking sensitive data"""
        data = {
            'id': self.id,
            'business_name': self.business_name,
            'owner_name': self.owner_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'address': self.address,
            'website': self.website,
            'logo_url': self.logo_url,
            'sendgrid_from_email': self.sendgrid_from_email,
            'sendgrid_from_name': self.sendgrid_from_name,
            'sendgrid_enabled': self.sendgrid_enabled,
            'twilio_phone_number': self.twilio_phone_number,
            'twilio_enabled': self.twilio_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Include sensitive data only if explicitly requested
        if include_sensitive:
            data['sendgrid_api_key'] = self.sendgrid_api_key
            data['twilio_account_sid'] = self.twilio_account_sid
            data['twilio_auth_token'] = self.twilio_auth_token
        else:
            # Mask sensitive data
            data['sendgrid_api_key'] = '***' if self.sendgrid_api_key else None
            data['twilio_account_sid'] = '***' if self.twilio_account_sid else None
            data['twilio_auth_token'] = '***' if self.twilio_auth_token else None
        
        return data

class ActivityLog(db.Model):
    """Activity logging for audit trail"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)  # create, update, delete, view
    entity_type = db.Column(db.String(50), nullable=False)  # trainer, client, assignment, etc.
    entity_id = db.Column(db.Integer)
    user_identifier = db.Column(db.String(200))  # email or ID of user who performed action
    details = db.Column(db.JSON)  # Additional details about the action
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Return activity log information with backward compatibility"""
        details = self.details or {}
        # Determine role from entity_type if not provided
        role = details.get('role') if details else (
            'Trainer' if self.entity_type == 'trainer' else (
                'Client' if self.entity_type == 'client' else (
                    self.entity_type.capitalize() if self.entity_type else None
                )
            )
        )
        return {
            'id': self.id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,  # Maintain backward compatibility
            'user_identifier': self.user_identifier,  # Maintain backward compatibility
            'name': details.get('name') if details else None,
            'email': details.get('email') or self.user_identifier,
            'contact': details.get('contact') if details else None,
            'role': role,
            'details': self.details,  # Maintain backward compatibility (contains simplified data)
            'ip_address': self.ip_address,  # Maintain backward compatibility (may be None)
            'user_agent': self.user_agent,  # Maintain backward compatibility (may be None)
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class Measurement(db.Model):
    """Client measurement tracking model"""
    __tablename__ = 'measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    measurement_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Body measurements
    weight = db.Column(db.Float)  # in kg or lbs
    weight_unit = db.Column(db.String(10), default='kg')  # kg or lbs
    body_fat_percentage = db.Column(db.Float)  # percentage
    muscle_mass = db.Column(db.Float)  # in kg or lbs
    bmi = db.Column(db.Float)  # Body Mass Index
    
    # Circumference measurements (in cm or inches)
    chest = db.Column(db.Float)
    waist = db.Column(db.Float)
    hips = db.Column(db.Float)
    thigh_left = db.Column(db.Float)
    thigh_right = db.Column(db.Float)
    arm_left = db.Column(db.Float)
    arm_right = db.Column(db.Float)
    calf_left = db.Column(db.Float)
    calf_right = db.Column(db.Float)
    measurement_unit = db.Column(db.String(10), default='cm')  # cm or inches
    
    # Additional metrics
    resting_heart_rate = db.Column(db.Integer)  # bpm
    blood_pressure_systolic = db.Column(db.Integer)  # mmHg
    blood_pressure_diastolic = db.Column(db.Integer)  # mmHg
    
    # Notes and context
    notes = db.Column(db.Text)
    recorded_by = db.Column(db.String(200))  # trainer name or 'self'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'measurement_date': self.measurement_date.isoformat() if self.measurement_date else None,
            'weight': self.weight,
            'weight_unit': self.weight_unit,
            'body_fat_percentage': self.body_fat_percentage,
            'muscle_mass': self.muscle_mass,
            'bmi': self.bmi,
            'chest': self.chest,
            'waist': self.waist,
            'hips': self.hips,
            'thigh_left': self.thigh_left,
            'thigh_right': self.thigh_right,
            'arm_left': self.arm_left,
            'arm_right': self.arm_right,
            'calf_left': self.calf_left,
            'calf_right': self.calf_right,
            'measurement_unit': self.measurement_unit,
            'resting_heart_rate': self.resting_heart_rate,
            'blood_pressure_systolic': self.blood_pressure_systolic,
            'blood_pressure_diastolic': self.blood_pressure_diastolic,
            'notes': self.notes,
            'recorded_by': self.recorded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class File(db.Model):
    """File storage model for documents, images, and attachments"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    file_type = db.Column(db.String(100))  # MIME type
    category = db.Column(db.String(50))  # workout_plan, waiver, assessment, progress_photo, document
    
    # Associations
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)
    
    # Metadata
    description = db.Column(db.Text)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', foreign_keys=[client_id], backref='files')
    trainer = db.relationship('Trainer', foreign_keys=[trainer_id], backref='trainer_files')
    session = db.relationship('Session', foreign_keys=[session_id], backref='files')
    uploader = db.relationship('Trainer', foreign_keys=[uploaded_by], backref='uploaded_files')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'category': self.category,
            'client_id': self.client_id,
            'trainer_id': self.trainer_id,
            'session_id': self.session_id,
            'description': self.description,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Exercise(db.Model):
    """Exercise library model"""
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # strength, cardio, flexibility, balance, sports
    muscle_group = db.Column(db.String(100))  # chest, back, legs, shoulders, arms, core, full_body
    equipment = db.Column(db.String(200))  # bodyweight, dumbbells, barbell, machine, bands, etc.
    difficulty = db.Column(db.String(50))  # beginner, intermediate, advanced
    
    # Exercise details
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    tips = db.Column(db.Text)
    
    # Media
    image_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    
    # Metadata
    is_custom = db.Column(db.Boolean, default=False)  # True if created by trainer
    created_by = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('Trainer', foreign_keys=[created_by], backref='created_exercises')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'muscle_group': self.muscle_group,
            'equipment': self.equipment,
            'difficulty': self.difficulty,
            'description': self.description,
            'instructions': self.instructions,
            'tips': self.tips,
            'image_url': self.image_url,
            'video_url': self.video_url,
            'is_custom': self.is_custom,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class WorkoutTemplate(db.Model):
    """Workout template model"""
    __tablename__ = 'workout_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # strength, cardio, hiit, circuit, flexibility
    difficulty = db.Column(db.String(50))  # beginner, intermediate, advanced
    duration_minutes = db.Column(db.Integer)  # Estimated duration
    
    # Ownership
    created_by = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)  # Can other trainers see/use it
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('Trainer', foreign_keys=[created_by], backref='workout_templates')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'duration_minutes': self.duration_minutes,
            'created_by': self.created_by,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class WorkoutExercise(db.Model):
    """Exercises within a workout template"""
    __tablename__ = 'workout_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    workout_template_id = db.Column(db.Integer, db.ForeignKey('workout_templates.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    
    # Exercise parameters
    order = db.Column(db.Integer, default=0)  # Order in workout
    sets = db.Column(db.Integer)
    reps = db.Column(db.String(50))  # Can be "12" or "8-12" or "AMRAP"
    duration_seconds = db.Column(db.Integer)  # For timed exercises
    rest_seconds = db.Column(db.Integer)  # Rest between sets
    weight = db.Column(db.String(50))  # Can be "bodyweight", "50 lbs", "RPE 8", etc.
    notes = db.Column(db.Text)
    
    workout_template = db.relationship('WorkoutTemplate', backref=db.backref('exercises', lazy='dynamic', cascade='all, delete-orphan'))
    exercise = db.relationship('Exercise', backref='workout_exercises')
    
    def to_dict(self):
        return {
            'id': self.id,
            'workout_template_id': self.workout_template_id,
            'exercise_id': self.exercise_id,
            'exercise': self.exercise.to_dict() if self.exercise else None,
            'order': self.order,
            'sets': self.sets,
            'reps': self.reps,
            'duration_seconds': self.duration_seconds,
            'rest_seconds': self.rest_seconds,
            'weight': self.weight,
            'notes': self.notes,
        }

class ClientWorkout(db.Model):
    """Assigned workouts to clients"""
    __tablename__ = 'client_workouts'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    workout_template_id = db.Column(db.Integer, db.ForeignKey('workout_templates.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    
    # Assignment details
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    frequency_per_week = db.Column(db.Integer)  # Recommended frequency
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='active')  # active, completed, paused
    
    client = db.relationship('Client', backref='workouts')
    workout_template = db.relationship('WorkoutTemplate', backref='client_assignments')
    assigner = db.relationship('Trainer', foreign_keys=[assigned_by], backref='assigned_workouts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'workout_template_id': self.workout_template_id,
            'workout_template': self.workout_template.to_dict() if self.workout_template else None,
            'assigned_by': self.assigned_by,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'frequency_per_week': self.frequency_per_week,
            'notes': self.notes,
            'status': self.status,
        }

class WorkoutLog(db.Model):
    """Client workout completion logs"""
    __tablename__ = 'workout_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    client_workout_id = db.Column(db.Integer, db.ForeignKey('client_workouts.id'), nullable=True)
    workout_template_id = db.Column(db.Integer, db.ForeignKey('workout_templates.id'), nullable=True)
    
    # Log details
    completed_date = db.Column(db.DateTime, default=datetime.utcnow)
    duration_minutes = db.Column(db.Integer)
    difficulty_rating = db.Column(db.Integer)  # 1-10 scale
    notes = db.Column(db.Text)
    
    client = db.relationship('Client', backref='workout_logs')
    client_workout = db.relationship('ClientWorkout', backref='logs')
    workout_template = db.relationship('WorkoutTemplate', backref='logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_workout_id': self.client_workout_id,
            'workout_template_id': self.workout_template_id,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'duration_minutes': self.duration_minutes,
            'difficulty_rating': self.difficulty_rating,
            'notes': self.notes,
        }

class ProgressPhoto(db.Model):
    """Progress photos for clients"""
    __tablename__ = 'progress_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    measurement_id = db.Column(db.Integer, db.ForeignKey('measurements.id'), nullable=True)
    
    # Photo details
    file_path = db.Column(db.String(500), nullable=False)  # Path to stored image
    photo_type = db.Column(db.String(50))  # front, side, back, other
    caption = db.Column(db.String(500))
    taken_date = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    client = db.relationship('Client', backref='progress_photos')
    measurement = db.relationship('Measurement', backref='photos')
    uploader = db.relationship('Trainer', foreign_keys=[uploaded_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'measurement_id': self.measurement_id,
            'file_path': self.file_path,
            'photo_type': self.photo_type,
            'caption': self.caption,
            'taken_date': self.taken_date.isoformat() if self.taken_date else None,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class Goal(db.Model):
    """Client goals and milestones"""
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Goal details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # weight_loss, muscle_gain, strength, endurance, flexibility, other
    
    # Target values
    target_value = db.Column(db.Float)  # e.g., target weight
    target_unit = db.Column(db.String(50))  # e.g., lbs, kg, %
    current_value = db.Column(db.Float)
    
    # Dates
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    target_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(50), default='active')  # active, completed, abandoned, on_hold
    priority = db.Column(db.String(50), default='medium')  # low, medium, high
    
    # Tracking
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    client = db.relationship('Client', backref='goal_records')
    creator = db.relationship('Trainer', foreign_keys=[created_by])
    milestones = db.relationship('GoalMilestone', backref='goal', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        progress = 0
        if self.target_value and self.current_value:
            progress = min(100, (self.current_value / self.target_value) * 100)
        
        return {
            'id': self.id,
            'client_id': self.client_id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'target_value': self.target_value,
            'target_unit': self.target_unit,
            'current_value': self.current_value,
            'progress': round(progress, 1),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'status': self.status,
            'priority': self.priority,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'milestones': [m.to_dict() for m in self.milestones] if hasattr(self, 'milestones') else []
        }

class GoalMilestone(db.Model):
    """Milestones for tracking goal progress"""
    __tablename__ = 'goal_milestones'
    
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=False)
    
    # Milestone details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Float)
    target_date = db.Column(db.DateTime)
    
    # Status
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'goal_id': self.goal_id,
            'title': self.title,
            'description': self.description,
            'target_value': self.target_value,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'completed': self.completed,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class MessageThread(db.Model):
    """Message thread/conversation between trainer and client"""
    __tablename__ = 'message_threads'
    
    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Thread metadata
    subject = db.Column(db.String(200))
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_by = db.Column(db.String(50))  # 'trainer' or 'client'
    
    # Status
    trainer_unread_count = db.Column(db.Integer, default=0)
    client_unread_count = db.Column(db.Integer, default=0)
    archived_by_trainer = db.Column(db.Boolean, default=False)
    archived_by_client = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trainer = db.relationship('Trainer', foreign_keys=[trainer_id], backref='message_threads')
    client = db.relationship('Client', foreign_keys=[client_id], backref='message_threads')
    messages = db.relationship('Message', backref='thread', lazy='dynamic', cascade='all, delete-orphan', order_by='Message.created_at')
    
    def to_dict(self, include_messages=False):
        data = {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'client_id': self.client_id,
            'trainer': self.trainer.to_dict() if self.trainer else None,
            'client': self.client.to_dict() if self.client else None,
            'subject': self.subject,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'last_message_by': self.last_message_by,
            'trainer_unread_count': self.trainer_unread_count,
            'client_unread_count': self.client_unread_count,
            'archived_by_trainer': self.archived_by_trainer,
            'archived_by_client': self.archived_by_client,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_messages:
            data['messages'] = [msg.to_dict() for msg in self.messages]
        
        return data

class Message(db.Model):
    """Individual message in a thread"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('message_threads.id'), nullable=False)
    
    # Sender information
    sender_type = db.Column(db.String(20), nullable=False)  # 'trainer' or 'client'
    sender_id = db.Column(db.Integer, nullable=False)  # trainer_id or client_id
    
    # Message content
    content = db.Column(db.Text, nullable=False)
    
    # Status
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    deleted_by_sender = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    attachments = db.relationship('MessageAttachment', backref='message', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'sender': self._get_sender_dict(),
            'content': self.content,
            'read': self.read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'deleted_by_sender': self.deleted_by_sender,
            'attachments': [att.to_dict() for att in self.attachments],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def _get_sender_dict(self):
        """Get sender information based on sender_type"""
        if self.sender_type == 'trainer':
            trainer = Trainer.query.get(self.sender_id)
            return trainer.to_dict() if trainer else None
        elif self.sender_type == 'client':
            client = Client.query.get(self.sender_id)
            return client.to_dict() if client else None
        return None

class MessageAttachment(db.Model):
    """File attachments in messages"""
    __tablename__ = 'message_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    file = db.relationship('File', foreign_keys=[file_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'file_id': self.file_id,
            'file': self.file.to_dict() if self.file else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class SMSTemplate(db.Model):
    """SMS message templates"""
    __tablename__ = 'sms_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # reminder, notification, marketing, custom
    message = db.Column(db.Text, nullable=False)
    
    # Template variables (comma-separated)
    variables = db.Column(db.String(500))  # e.g., "client_name,trainer_name,session_date"
    
    # Status
    active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'message': self.message,
            'variables': self.variables.split(',') if self.variables else [],
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class SMSLog(db.Model):
    """SMS message log for tracking and analytics"""
    __tablename__ = 'sms_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Message details
    to_number = db.Column(db.String(20), nullable=False)
    from_number = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    message_sid = db.Column(db.String(100))  # Twilio message SID
    
    # Associations
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)
    template_id = db.Column(db.Integer, db.ForeignKey('sms_templates.id'), nullable=True)
    
    # Status
    status = db.Column(db.String(50), default='queued')  # queued, sent, delivered, failed, undelivered
    error_message = db.Column(db.Text)
    
    # Twilio details
    twilio_status = db.Column(db.String(50))
    price = db.Column(db.Float)  # Cost in USD
    price_unit = db.Column(db.String(10))  # USD
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    delivered_at = db.Column(db.DateTime)
    
    # Relationships
    client = db.relationship('Client', foreign_keys=[client_id], backref='sms_logs')
    trainer = db.relationship('Trainer', foreign_keys=[trainer_id], backref='sms_logs')
    session = db.relationship('Session', foreign_keys=[session_id], backref='sms_logs')
    template = db.relationship('SMSTemplate', foreign_keys=[template_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'to_number': self.to_number,
            'from_number': self.from_number,
            'message': self.message,
            'message_sid': self.message_sid,
            'client_id': self.client_id,
            'trainer_id': self.trainer_id,
            'session_id': self.session_id,
            'template_id': self.template_id,
            'status': self.status,
            'error_message': self.error_message,
            'twilio_status': self.twilio_status,
            'price': self.price,
            'price_unit': self.price_unit,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
        }

class SMSSchedule(db.Model):
    """Scheduled SMS messages"""
    __tablename__ = 'sms_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Schedule details
    name = db.Column(db.String(200))
    template_id = db.Column(db.Integer, db.ForeignKey('sms_templates.id'), nullable=True)
    message = db.Column(db.Text)  # Custom message if no template
    
    # Recipients
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainers.id'), nullable=True)
    to_number = db.Column(db.String(20), nullable=False)
    
    # Scheduling
    schedule_type = db.Column(db.String(50), nullable=False)  # once, daily, weekly, monthly, custom
    scheduled_time = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Recurrence (for recurring schedules)
    recurrence_end_date = db.Column(db.DateTime)
    recurrence_days = db.Column(db.JSON)  # For weekly: [0,2,4] = Mon, Wed, Fri
    
    # Status
    status = db.Column(db.String(50), default='scheduled')  # scheduled, sent, cancelled, failed
    last_sent_at = db.Column(db.DateTime)
    next_send_at = db.Column(db.DateTime)
    
    # Template variables (JSON)
    template_variables = db.Column(db.JSON)  # {"client_name": "John", "trainer_name": "Jane"}
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template = db.relationship('SMSTemplate', foreign_keys=[template_id])
    client = db.relationship('Client', foreign_keys=[client_id])
    trainer = db.relationship('Trainer', foreign_keys=[trainer_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'template_id': self.template_id,
            'message': self.message,
            'client_id': self.client_id,
            'trainer_id': self.trainer_id,
            'to_number': self.to_number,
            'schedule_type': self.schedule_type,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'timezone': self.timezone,
            'recurrence_end_date': self.recurrence_end_date.isoformat() if self.recurrence_end_date else None,
            'recurrence_days': self.recurrence_days,
            'status': self.status,
            'last_sent_at': self.last_sent_at.isoformat() if self.last_sent_at else None,
            'next_send_at': self.next_send_at.isoformat() if self.next_send_at else None,
            'template_variables': self.template_variables,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class EmailTemplate(db.Model):
    """Email campaign templates"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # newsletter, promotion, announcement, custom
    subject = db.Column(db.String(200), nullable=False)
    html_body = db.Column(db.Text, nullable=False)
    text_body = db.Column(db.Text)  # Plain text version
    
    # Template variables (comma-separated)
    variables = db.Column(db.String(500))  # e.g., "client_name,trainer_name,date"
    
    # Status
    active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'subject': self.subject,
            'html_body': self.html_body,
            'text_body': self.text_body,
            'variables': self.variables.split(',') if self.variables else [],
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class EmailCampaign(db.Model):
    """Email campaign"""
    __tablename__ = 'email_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Campaign content
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id'), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    html_body = db.Column(db.Text, nullable=False)
    text_body = db.Column(db.Text)
    
    # Recipient segmentation
    segment_type = db.Column(db.String(50), nullable=False)  # all_clients, all_trainers, custom, specific_ids
    segment_filters = db.Column(db.JSON)  # {"status": "active", "membership_type": "monthly"}
    recipient_ids = db.Column(db.JSON)  # [1, 2, 3] for specific_ids
    
    # A/B Testing
    ab_test_enabled = db.Column(db.Boolean, default=False)
    ab_test_subject_a = db.Column(db.String(200))
    ab_test_subject_b = db.Column(db.String(200))
    ab_test_split_percentage = db.Column(db.Integer, default=50)  # Percentage for variant A
    
    # Scheduling
    scheduled_at = db.Column(db.DateTime)
    send_immediately = db.Column(db.Boolean, default=False)
    
    # Status
    status = db.Column(db.String(50), default='draft')  # draft, scheduled, sending, sent, cancelled, failed
    sent_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Statistics
    total_recipients = db.Column(db.Integer, default=0)
    emails_sent = db.Column(db.Integer, default=0)
    emails_delivered = db.Column(db.Integer, default=0)
    emails_opened = db.Column(db.Integer, default=0)
    emails_clicked = db.Column(db.Integer, default=0)
    emails_bounced = db.Column(db.Integer, default=0)
    emails_failed = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template = db.relationship('EmailTemplate', foreign_keys=[template_id])
    recipients = db.relationship('CampaignRecipient', backref='campaign', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template_id': self.template_id,
            'subject': self.subject,
            'html_body': self.html_body,
            'text_body': self.text_body,
            'segment_type': self.segment_type,
            'segment_filters': self.segment_filters,
            'recipient_ids': self.recipient_ids,
            'ab_test_enabled': self.ab_test_enabled,
            'ab_test_subject_a': self.ab_test_subject_a,
            'ab_test_subject_b': self.ab_test_subject_b,
            'ab_test_split_percentage': self.ab_test_split_percentage,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'send_immediately': self.send_immediately,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_recipients': self.total_recipients,
            'emails_sent': self.emails_sent,
            'emails_delivered': self.emails_delivered,
            'emails_opened': self.emails_opened,
            'emails_clicked': self.emails_clicked,
            'emails_bounced': self.emails_bounced,
            'emails_failed': self.emails_failed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class CampaignRecipient(db.Model):
    """Individual recipient in an email campaign"""
    __tablename__ = 'campaign_recipients'
    
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('email_campaigns.id'), nullable=False)
    
    # Recipient info
    email = db.Column(db.String(120), nullable=False)
    recipient_type = db.Column(db.String(20))  # 'client' or 'trainer'
    recipient_id = db.Column(db.Integer)  # client_id or trainer_id
    
    # A/B Test variant
    ab_variant = db.Column(db.String(1))  # 'A' or 'B'
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, sent, delivered, opened, clicked, bounced, failed
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    opened_at = db.Column(db.DateTime)
    clicked_at = db.Column(db.DateTime)
    bounced_at = db.Column(db.DateTime)
    failed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Tracking
    open_count = db.Column(db.Integer, default=0)
    click_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'email': self.email,
            'recipient_type': self.recipient_type,
            'recipient_id': self.recipient_id,
            'ab_variant': self.ab_variant,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'bounced_at': self.bounced_at.isoformat() if self.bounced_at else None,
            'failed_at': self.failed_at.isoformat() if self.failed_at else None,
            'error_message': self.error_message,
            'open_count': self.open_count,
            'click_count': self.click_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class AutomationRule(db.Model):
    """Automated reminder and notification rules"""
    __tablename__ = 'automation_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Rule type and trigger
    rule_type = db.Column(db.String(50), nullable=False)  # session_reminder, payment_reminder, birthday, re_engagement, custom
    trigger_event = db.Column(db.String(50))  # session_created, payment_due, birthday, inactivity
    trigger_conditions = db.Column(db.JSON)  # {"hours_before": 24, "status": "scheduled"}
    
    # Action
    action_type = db.Column(db.String(50), nullable=False)  # email, sms, both
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.id'), nullable=True)
    sms_template_id = db.Column(db.Integer, db.ForeignKey('sms_templates.id'), nullable=True)
    custom_message = db.Column(db.Text)
    
    # Targeting
    target_audience = db.Column(db.String(50), default='all')  # all, clients, trainers, specific
    target_filters = db.Column(db.JSON)  # {"status": "active", "membership_type": "monthly"}
    target_ids = db.Column(db.JSON)  # [1, 2, 3] for specific targets
    
    # Scheduling
    enabled = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Status
    last_run_at = db.Column(db.DateTime)
    next_run_at = db.Column(db.DateTime)
    run_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    failure_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    email_template = db.relationship('EmailTemplate', foreign_keys=[template_id])
    sms_template = db.relationship('SMSTemplate', foreign_keys=[sms_template_id])
    logs = db.relationship('AutomationLog', backref='rule', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rule_type': self.rule_type,
            'trigger_event': self.trigger_event,
            'trigger_conditions': self.trigger_conditions,
            'action_type': self.action_type,
            'template_id': self.template_id,
            'sms_template_id': self.sms_template_id,
            'custom_message': self.custom_message,
            'target_audience': self.target_audience,
            'target_filters': self.target_filters,
            'target_ids': self.target_ids,
            'enabled': self.enabled,
            'timezone': self.timezone,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'next_run_at': self.next_run_at.isoformat() if self.next_run_at else None,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class AutomationLog(db.Model):
    """Log of automation rule executions"""
    __tablename__ = 'automation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('automation_rules.id'), nullable=False)
    
    # Execution details
    executed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), default='success')  # success, failed, skipped
    error_message = db.Column(db.Text)
    
    # Action details
    action_type = db.Column(db.String(50))  # email, sms, both
    recipients_count = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    
    # Context
    trigger_context = db.Column(db.JSON)  # {"session_id": 123, "client_id": 456}
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'rule_id': self.rule_id,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'status': self.status,
            'error_message': self.error_message,
            'action_type': self.action_type,
            'recipients_count': self.recipients_count,
            'sent_count': self.sent_count,
            'failed_count': self.failed_count,
            'trigger_context': self.trigger_context,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }