from flask import Blueprint, request, jsonify, send_from_directory
from models.database import db, ProgressPhoto, Client, Trainer
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

progress_photo_bp = Blueprint('progress_photos', __name__)

# Configure upload settings
UPLOAD_FOLDER = 'uploads/progress_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@progress_photo_bp.route('/progress-photos', methods=['GET'])
def get_progress_photos():
    """Get all progress photos with optional filtering"""
    try:
        query = ProgressPhoto.query
        
        # Filter by client_id
        client_id = request.args.get('client_id', type=int)
        if client_id:
            query = query.filter_by(client_id=client_id)
        
        # Filter by photo_type
        photo_type = request.args.get('photo_type')
        if photo_type:
            query = query.filter_by(photo_type=photo_type)
        
        # Filter by date range
        date_from = request.args.get('date_from')
        if date_from:
            query = query.filter(ProgressPhoto.taken_date >= datetime.fromisoformat(date_from))
        
        date_to = request.args.get('date_to')
        if date_to:
            query = query.filter(ProgressPhoto.taken_date <= datetime.fromisoformat(date_to))
        
        # Order by date descending
        query = query.order_by(ProgressPhoto.taken_date.desc())
        
        photos = query.all()
        
        return jsonify({
            'success': True,
            'data': [photo.to_dict() for photo in photos],
            'count': len(photos)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@progress_photo_bp.route('/progress-photos/<int:id>', methods=['GET'])
def get_progress_photo(id):
    """Get a specific progress photo"""
    try:
        photo = ProgressPhoto.query.get_or_404(id)
        return jsonify({
            'success': True,
            'data': photo.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@progress_photo_bp.route('/progress-photos', methods=['POST'])
def create_progress_photo():
    """Upload a new progress photo"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Get form data
        client_id = request.form.get('client_id', type=int)
        if not client_id:
            return jsonify({'success': False, 'error': 'client_id is required'}), 400
        
        # Verify client exists
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'success': False, 'error': 'Client not found'}), 404
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Create database record
        photo = ProgressPhoto(
            client_id=client_id,
            measurement_id=request.form.get('measurement_id', type=int),
            file_path=file_path,
            photo_type=request.form.get('photo_type', 'other'),
            caption=request.form.get('caption'),
            taken_date=datetime.fromisoformat(request.form.get('taken_date')) if request.form.get('taken_date') else datetime.utcnow(),
            uploaded_by=request.form.get('uploaded_by', type=int)
        )
        
        db.session.add(photo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress photo uploaded successfully',
            'data': photo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@progress_photo_bp.route('/progress-photos/<int:id>', methods=['PUT'])
def update_progress_photo(id):
    """Update a progress photo's metadata"""
    try:
        photo = ProgressPhoto.query.get_or_404(id)
        data = request.get_json()
        
        # Update allowed fields
        if 'photo_type' in data:
            photo.photo_type = data['photo_type']
        if 'caption' in data:
            photo.caption = data['caption']
        if 'taken_date' in data:
            photo.taken_date = datetime.fromisoformat(data['taken_date'])
        if 'measurement_id' in data:
            photo.measurement_id = data['measurement_id']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress photo updated successfully',
            'data': photo.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@progress_photo_bp.route('/progress-photos/<int:id>', methods=['DELETE'])
def delete_progress_photo(id):
    """Delete a progress photo"""
    try:
        photo = ProgressPhoto.query.get_or_404(id)
        
        # Delete file from filesystem
        if os.path.exists(photo.file_path):
            os.remove(photo.file_path)
        
        db.session.delete(photo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress photo deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@progress_photo_bp.route('/progress-photos/<int:id>/file', methods=['GET'])
def get_progress_photo_file(id):
    """Serve the actual photo file"""
    try:
        photo = ProgressPhoto.query.get_or_404(id)
        directory = os.path.dirname(photo.file_path)
        filename = os.path.basename(photo.file_path)
        return send_from_directory(directory, filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@progress_photo_bp.route('/progress-photos/client/<int:client_id>/comparison', methods=['GET'])
def get_comparison_photos(client_id):
    """Get photos for before/after comparison"""
    try:
        # Get earliest and latest photos for each photo type
        photo_types = ['front', 'side', 'back']
        comparison_data = {}
        
        for photo_type in photo_types:
            photos = ProgressPhoto.query.filter_by(
                client_id=client_id,
                photo_type=photo_type
            ).order_by(ProgressPhoto.taken_date).all()
            
            if len(photos) >= 2:
                comparison_data[photo_type] = {
                    'before': photos[0].to_dict(),
                    'after': photos[-1].to_dict(),
                    'total_photos': len(photos)
                }
            elif len(photos) == 1:
                comparison_data[photo_type] = {
                    'before': photos[0].to_dict(),
                    'after': None,
                    'total_photos': 1
                }
        
        return jsonify({
            'success': True,
            'data': comparison_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
