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
    end_time = db.Column(db.DateTime)  # Calculated from session_date + duration
    duration = db.Column(db.Integer, default=60)  # in minutes
    session_type = db.Column(db.String(100))  # personal, group, online, etc.
    location = db.Column(db.String(200))  # Gym, Online, Client's Home, etc.
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, completed, cancelled, no-show
    recurring_session_id = db.Column(db.Integer, db.ForeignKey('recurring_sessions.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'trainer_id': self.trainer_id,
            'client_id': self.client_id,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
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
    sessions = db.relationship('Session', backref='recurring_template', lazy=True, foreign_keys=[Session.recurring_session_id])
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
        return {
            'id': self.id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'user_identifier': self.user_identifier,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
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
    
    client = db.relationship('Client', backref='goals')
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
