from flask import Blueprint, request, jsonify
from models.database import db, Measurement, Client
from datetime import datetime

measurement_bp = Blueprint('measurements', __name__)

@measurement_bp.route('/measurements', methods=['GET'])
def get_measurements():
    """Get all measurements with optional filtering"""
    try:
        # Get query parameters
        client_id = request.args.get('client_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', type=int)
        
        # Build query
        query = Measurement.query
        
        if client_id:
            query = query.filter_by(client_id=client_id)
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Measurement.measurement_date >= start_dt)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Measurement.measurement_date <= end_dt)
        
        # Order by date descending
        query = query.order_by(Measurement.measurement_date.desc())
        
        if limit:
            query = query.limit(limit)
        
        measurements = query.all()
        
        # Add client info to each measurement
        result = []
        for measurement in measurements:
            measurement_dict = measurement.to_dict()
            client = Client.query.get(measurement.client_id)
            if client:
                measurement_dict['client_name'] = client.name
            result.append(measurement_dict)
        
        return jsonify({'data': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@measurement_bp.route('/measurements/<int:id>', methods=['GET'])
def get_measurement(id):
    """Get a specific measurement"""
    try:
        measurement = Measurement.query.get_or_404(id)
        measurement_dict = measurement.to_dict()
        
        # Add client info
        client = Client.query.get(measurement.client_id)
        if client:
            measurement_dict['client_name'] = client.name
        
        return jsonify({'data': measurement_dict}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@measurement_bp.route('/measurements', methods=['POST'])
def create_measurement():
    """Create a new measurement"""
    try:
        data = request.json
        
        # Validate required fields
        if 'client_id' not in data:
            return jsonify({'error': 'Missing required field: client_id'}), 400
        
        # Verify client exists
        client = Client.query.get(data['client_id'])
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Parse measurement date if provided
        measurement_date = datetime.utcnow()
        if 'measurement_date' in data:
            measurement_date = datetime.fromisoformat(data['measurement_date'])
        
        # Create new measurement
        measurement = Measurement(
            client_id=data['client_id'],
            measurement_date=measurement_date,
            weight=data.get('weight'),
            weight_unit=data.get('weight_unit', 'kg'),
            body_fat_percentage=data.get('body_fat_percentage'),
            muscle_mass=data.get('muscle_mass'),
            bmi=data.get('bmi'),
            chest=data.get('chest'),
            waist=data.get('waist'),
            hips=data.get('hips'),
            thigh_left=data.get('thigh_left'),
            thigh_right=data.get('thigh_right'),
            arm_left=data.get('arm_left'),
            arm_right=data.get('arm_right'),
            calf_left=data.get('calf_left'),
            calf_right=data.get('calf_right'),
            measurement_unit=data.get('measurement_unit', 'cm'),
            resting_heart_rate=data.get('resting_heart_rate'),
            blood_pressure_systolic=data.get('blood_pressure_systolic'),
            blood_pressure_diastolic=data.get('blood_pressure_diastolic'),
            notes=data.get('notes'),
            recorded_by=data.get('recorded_by')
        )
        
        db.session.add(measurement)
        db.session.commit()
        
        return jsonify(measurement.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@measurement_bp.route('/measurements/<int:id>', methods=['PUT'])
def update_measurement(id):
    """Update a measurement"""
    try:
        measurement = Measurement.query.get_or_404(id)
        data = request.json
        
        # Update fields
        if 'measurement_date' in data:
            measurement.measurement_date = datetime.fromisoformat(data['measurement_date'])
        if 'weight' in data:
            measurement.weight = data['weight']
        if 'weight_unit' in data:
            measurement.weight_unit = data['weight_unit']
        if 'body_fat_percentage' in data:
            measurement.body_fat_percentage = data['body_fat_percentage']
        if 'muscle_mass' in data:
            measurement.muscle_mass = data['muscle_mass']
        if 'bmi' in data:
            measurement.bmi = data['bmi']
        if 'chest' in data:
            measurement.chest = data['chest']
        if 'waist' in data:
            measurement.waist = data['waist']
        if 'hips' in data:
            measurement.hips = data['hips']
        if 'thigh_left' in data:
            measurement.thigh_left = data['thigh_left']
        if 'thigh_right' in data:
            measurement.thigh_right = data['thigh_right']
        if 'arm_left' in data:
            measurement.arm_left = data['arm_left']
        if 'arm_right' in data:
            measurement.arm_right = data['arm_right']
        if 'calf_left' in data:
            measurement.calf_left = data['calf_left']
        if 'calf_right' in data:
            measurement.calf_right = data['calf_right']
        if 'measurement_unit' in data:
            measurement.measurement_unit = data['measurement_unit']
        if 'resting_heart_rate' in data:
            measurement.resting_heart_rate = data['resting_heart_rate']
        if 'blood_pressure_systolic' in data:
            measurement.blood_pressure_systolic = data['blood_pressure_systolic']
        if 'blood_pressure_diastolic' in data:
            measurement.blood_pressure_diastolic = data['blood_pressure_diastolic']
        if 'notes' in data:
            measurement.notes = data['notes']
        if 'recorded_by' in data:
            measurement.recorded_by = data['recorded_by']
        
        db.session.commit()
        
        return jsonify(measurement.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@measurement_bp.route('/measurements/<int:id>', methods=['DELETE'])
def delete_measurement(id):
    """Delete a measurement"""
    try:
        measurement = Measurement.query.get_or_404(id)
        
        db.session.delete(measurement)
        db.session.commit()
        
        return jsonify({'message': 'Measurement deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@measurement_bp.route('/measurements/client/<int:client_id>/latest', methods=['GET'])
def get_latest_measurement(client_id):
    """Get the most recent measurement for a client"""
    try:
        measurement = Measurement.query.filter_by(client_id=client_id).order_by(Measurement.measurement_date.desc()).first()
        
        if not measurement:
            return jsonify({'data': None}), 200
        
        measurement_dict = measurement.to_dict()
        
        # Add client info
        client = Client.query.get(client_id)
        if client:
            measurement_dict['client_name'] = client.name
        
        return jsonify({'data': measurement_dict}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@measurement_bp.route('/measurements/client/<int:client_id>/progress', methods=['GET'])
def get_progress_data(client_id):
    """Get measurement progress data for charts"""
    try:
        # Get all measurements for the client ordered by date
        measurements = Measurement.query.filter_by(client_id=client_id).order_by(Measurement.measurement_date.asc()).all()
        
        if not measurements:
            return jsonify({'data': []}), 200
        
        # Format data for charts
        progress_data = {
            'dates': [],
            'weight': [],
            'body_fat': [],
            'muscle_mass': [],
            'bmi': [],
            'waist': [],
            'chest': [],
            'hips': []
        }
        
        for measurement in measurements:
            progress_data['dates'].append(measurement.measurement_date.isoformat())
            progress_data['weight'].append(measurement.weight)
            progress_data['body_fat'].append(measurement.body_fat_percentage)
            progress_data['muscle_mass'].append(measurement.muscle_mass)
            progress_data['bmi'].append(measurement.bmi)
            progress_data['waist'].append(measurement.waist)
            progress_data['chest'].append(measurement.chest)
            progress_data['hips'].append(measurement.hips)
        
        return jsonify({'data': progress_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
