from flask import Blueprint, request, jsonify
from models.database import db, Session, RecurringSession, Trainer, Client
from datetime import datetime, timedelta, time
from utils.email import send_session_confirmation

session_bp = Blueprint('sessions', __name__)

@session_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get all sessions with optional filtering"""
    try:
        # Get query parameters
        trainer_id = request.args.get('trainer_id', type=int)
        client_id = request.args.get('client_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        
        # Build query
        query = Session.query
        
        if trainer_id:
            query = query.filter_by(trainer_id=trainer_id)
        if client_id:
            query = query.filter_by(client_id=client_id)
        if status:
            query = query.filter_by(status=status)
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Session.session_date >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Session.session_date <= end_dt)
        
        # Order by session date
        sessions = query.order_by(Session.session_date.asc()).all()
        
        # Enrich with trainer and client names
        result = []
        for session in sessions:
            session_dict = session.to_dict()
            trainer = Trainer.query.get(session.trainer_id)
            client = Client.query.get(session.client_id)
            session_dict['trainer_name'] = trainer.name if trainer else None
            session_dict['client_name'] = client.name if client else None
            result.append(session_dict)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@session_bp.route('/sessions/<int:id>', methods=['GET'])
def get_session(id):
    """Get a specific session"""
    try:
        session = Session.query.get_or_404(id)
        session_dict = session.to_dict()
        
        # Enrich with trainer and client details
        trainer = Trainer.query.get(session.trainer_id)
        client = Client.query.get(session.client_id)
        session_dict['trainer'] = trainer.to_dict() if trainer else None
        session_dict['client'] = client.to_dict() if client else None
        
        return jsonify(session_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@session_bp.route('/sessions', methods=['POST'])
def create_session():
    """Create a new session"""
    try:
        data = request.json
        
        # Validate required fields
        if not all(k in data for k in ['trainer_id', 'client_id', 'session_date']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Parse session date
        session_date = datetime.fromisoformat(data['session_date'])
        duration = data.get('duration', 60)
        
        # Calculate end time
        end_time = session_date + timedelta(minutes=duration)
        
        # Check for conflicts
        conflict = Session.query.filter(
            Session.trainer_id == data['trainer_id'],
            Session.status != 'cancelled',
            Session.session_date < end_time,
            Session.end_time > session_date
        ).first()
        
        if conflict:
            return jsonify({'error': 'Session conflicts with existing booking', 'conflict': conflict.to_dict()}), 409
        
        # Create new session
        session = Session(
            trainer_id=data['trainer_id'],
            client_id=data['client_id'],
            session_date=session_date,
            end_time=end_time,
            duration=duration,
            session_type=data.get('session_type'),
            location=data.get('location'),
            notes=data.get('notes'),
            status=data.get('status', 'scheduled')
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Send confirmation email
        try:
            trainer = Trainer.query.get(session.trainer_id)
            client = Client.query.get(session.client_id)
            if client and client.email and trainer:
                send_session_confirmation(
                    client.email,
                    client.name,
                    trainer.name,
                    session.session_date.isoformat(),
                    session.duration,
                    session.location,
                    session.session_type or 'Training Session'
                )
        except Exception as email_error:
            # Log but don't fail the request if email fails
            print(f"Error sending confirmation email: {email_error}")
        
        return jsonify(session.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@session_bp.route('/sessions/<int:id>', methods=['PUT'])
def update_session(id):
    """Update a session"""
    try:
        session = Session.query.get_or_404(id)
        data = request.json
        
        # Update fields
        if 'session_date' in data:
            session.session_date = datetime.fromisoformat(data['session_date'])
        if 'duration' in data:
            session.duration = data['duration']
        if session.session_date and session.duration:
            session.end_time = session.session_date + timedelta(minutes=session.duration)
        if 'session_type' in data:
            session.session_type = data['session_type']
        if 'location' in data:
            session.location = data['location']
        if 'notes' in data:
            session.notes = data['notes']
        if 'status' in data:
            session.status = data['status']
        
        db.session.commit()
        
        return jsonify(session.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@session_bp.route('/sessions/<int:id>', methods=['DELETE'])
def delete_session(id):
    """Delete a session"""
    try:
        session = Session.query.get_or_404(id)
        
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({'message': 'Session deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@session_bp.route('/recurring-sessions', methods=['GET'])
def get_recurring_sessions():
    """Get all recurring sessions"""
    try:
        trainer_id = request.args.get('trainer_id', type=int)
        client_id = request.args.get('client_id', type=int)
        active_only = request.args.get('active', 'true').lower() == 'true'
        
        query = RecurringSession.query
        
        if trainer_id:
            query = query.filter_by(trainer_id=trainer_id)
        if client_id:
            query = query.filter_by(client_id=client_id)
        if active_only:
            query = query.filter_by(active=True)
        
        recurring_sessions = query.all()
        result = [rs.to_dict() for rs in recurring_sessions]
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@session_bp.route('/recurring-sessions', methods=['POST'])
def create_recurring_session():
    """Create a recurring session and generate future sessions"""
    try:
        data = request.json
        
        # Validate required fields
        if not all(k in data for k in ['trainer_id', 'client_id', 'start_date', 'start_time', 'recurrence_pattern']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Parse dates
        start_date = datetime.fromisoformat(data['start_date'])
        end_date = datetime.fromisoformat(data['end_date']) if data.get('end_date') else None
        start_time_obj = datetime.fromisoformat(data['start_time']).time()
        
        # Create recurring session template
        recurring_session = RecurringSession(
            trainer_id=data['trainer_id'],
            client_id=data['client_id'],
            start_date=start_date,
            end_date=end_date,
            start_time=start_time_obj,
            duration=data.get('duration', 60),
            session_type=data.get('session_type'),
            location=data.get('location'),
            recurrence_pattern=data['recurrence_pattern'],
            recurrence_days=data.get('recurrence_days'),
            notes=data.get('notes'),
            active=True
        )
        
        db.session.add(recurring_session)
        db.session.flush()  # Get the ID
        
        # Generate sessions for the next 3 months or until end_date
        max_date = end_date if end_date else start_date + timedelta(days=90)
        sessions_created = generate_recurring_sessions(recurring_session, start_date, max_date)
        
        db.session.commit()
        
        return jsonify({
            'recurring_session': recurring_session.to_dict(),
            'sessions_created': sessions_created
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def generate_recurring_sessions(recurring_session, start_date, end_date):
    """Generate individual sessions from a recurring session template"""
    sessions_created = 0
    current_date = start_date
    duration = recurring_session.duration
    
    while current_date <= end_date:
        should_create = False
        
        # Check if we should create a session on this date based on recurrence pattern
        if recurring_session.recurrence_pattern == 'daily':
            should_create = True
        elif recurring_session.recurrence_pattern == 'weekly':
            if recurring_session.recurrence_days and current_date.weekday() in recurring_session.recurrence_days:
                should_create = True
        elif recurring_session.recurrence_pattern == 'biweekly':
            weeks_diff = (current_date - start_date).days // 7
            if weeks_diff % 2 == 0 and recurring_session.recurrence_days and current_date.weekday() in recurring_session.recurrence_days:
                should_create = True
        elif recurring_session.recurrence_pattern == 'monthly':
            if current_date.day == start_date.day:
                should_create = True
        
        if should_create:
            session_datetime = datetime.combine(current_date.date(), recurring_session.start_time)
            end_time = session_datetime + timedelta(minutes=duration)
            
            # Check for conflicts before creating
            conflict = Session.query.filter(
                Session.trainer_id == recurring_session.trainer_id,
                Session.status != 'cancelled',
                Session.session_date < end_time,
                Session.end_time > session_datetime
            ).first()
            
            if not conflict:
                session = Session(
                    trainer_id=recurring_session.trainer_id,
                    client_id=recurring_session.client_id,
                    session_date=session_datetime,
                    end_time=end_time,
                    duration=duration,
                    session_type=recurring_session.session_type,
                    location=recurring_session.location,
                    notes=recurring_session.notes,
                    status='scheduled',
                    recurring_session_id=recurring_session.id
                )
                db.session.add(session)
                sessions_created += 1
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return sessions_created

@session_bp.route('/recurring-sessions/<int:id>', methods=['DELETE'])
def delete_recurring_session(id):
    """Delete a recurring session and optionally its future sessions"""
    try:
        recurring_session = RecurringSession.query.get_or_404(id)
        delete_future = request.args.get('delete_future', 'false').lower() == 'true'
        
        if delete_future:
            # Delete all future sessions
            Session.query.filter(
                Session.recurring_session_id == id,
                Session.session_date >= datetime.utcnow(),
                Session.status == 'scheduled'
            ).delete()
        
        db.session.delete(recurring_session)
        db.session.commit()
        
        return jsonify({'message': 'Recurring session deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@session_bp.route('/sessions/export/ical', methods=['GET'])
def export_sessions_ical():
    """Export sessions as iCal format"""
    try:
        # Get query parameters
        trainer_id = request.args.get('trainer_id', type=int)
        client_id = request.args.get('client_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Session.query
        
        if trainer_id:
            query = query.filter_by(trainer_id=trainer_id)
        if client_id:
            query = query.filter_by(client_id=client_id)
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Session.session_date >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Session.session_date <= end_dt)
        
        sessions = query.all()
        
        # Generate iCal content
        ical_lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//FitnessCRM//Session Calendar//EN',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
            'X-WR-CALNAME:FitnessCRM Sessions',
            'X-WR-TIMEZONE:UTC'
        ]
        
        for session in sessions:
            trainer = Trainer.query.get(session.trainer_id)
            client = Client.query.get(session.client_id)
            
            # Format dates for iCal (YYYYMMDDTHHMMSSZ)
            dtstart = session.session_date.strftime('%Y%m%dT%H%M%SZ')
            dtend = session.end_time.strftime('%Y%m%dT%H%M%SZ')
            dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
            
            # Create unique ID
            uid = f'session-{session.id}@fitnesscrm.com'
            
            # Build summary
            summary = f'{session.session_type or "Training"}: {trainer.name if trainer else "Trainer"} - {client.name if client else "Client"}'
            
            # Build description
            description_parts = []
            if session.notes:
                description_parts.append(f'Notes: {session.notes}')
            description_parts.append(f'Duration: {session.duration} minutes')
            description_parts.append(f'Status: {session.status}')
            description = '\\n'.join(description_parts)
            
            # Build location
            location = session.location or 'TBD'
            
            # Add event
            ical_lines.extend([
                'BEGIN:VEVENT',
                f'UID:{uid}',
                f'DTSTAMP:{dtstamp}',
                f'DTSTART:{dtstart}',
                f'DTEND:{dtend}',
                f'SUMMARY:{summary}',
                f'DESCRIPTION:{description}',
                f'LOCATION:{location}',
                f'STATUS:{session.status.upper()}',
                'END:VEVENT'
            ])
        
        ical_lines.append('END:VCALENDAR')
        
        ical_content = '\r\n'.join(ical_lines)
        
        # Return as downloadable file
        from flask import Response
        return Response(
            ical_content,
            mimetype='text/calendar',
            headers={
                'Content-Disposition': 'attachment; filename=fitnesscrm-sessions.ics'
            }
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
