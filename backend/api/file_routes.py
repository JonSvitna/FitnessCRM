"""
File management API routes
Handles file uploads, downloads, and management
"""
from flask import Blueprint, request, jsonify, send_file
from models.database import db, File, Client
from functools import wraps
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

file_bp = Blueprint('files', __name__, url_prefix='/api/files')

# File upload configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/fitnesscrm_uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_category(file_type):
    """Determine file category based on MIME type"""
    if file_type.startswith('image/'):
        return 'progress_photo'
    elif file_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        return 'document'
    elif file_type.startswith('video/'):
        return 'video'
    else:
        return 'other'

@file_bp.route('', methods=['GET'])
def get_files():
    """Get all files with optional filters"""
    try:
        query = File.query
        
        # Filter by client
        client_id = request.args.get('client_id', type=int)
        if client_id:
            query = query.filter_by(client_id=client_id)
        
        # Filter by trainer
        trainer_id = request.args.get('trainer_id', type=int)
        if trainer_id:
            query = query.filter_by(trainer_id=trainer_id)
        
        # Filter by session
        session_id = request.args.get('session_id', type=int)
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        # Filter by category
        category = request.args.get('category')
        if category:
            query = query.filter_by(category=category)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        files_paginated = query.order_by(File.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'files': [f.to_dict() for f in files_paginated.items],
            'total': files_paginated.total,
            'pages': files_paginated.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('', methods=['POST'])
def upload_file():
    """Upload a new file"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File size exceeds {MAX_FILE_SIZE / (1024*1024)}MB limit'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Get metadata from form
        client_id = request.form.get('client_id', type=int)
        trainer_id = request.form.get('trainer_id', type=int)
        session_id = request.form.get('session_id', type=int)
        category = request.form.get('category')
        description = request.form.get('description')
        uploaded_by = request.form.get('uploaded_by', type=int)
        
        if not uploaded_by:
            return jsonify({'error': 'uploaded_by is required'}), 400
        
        # Determine category if not provided
        if not category:
            category = get_file_category(file.content_type or 'application/octet-stream')
        
        # Create file record
        new_file = File(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file.content_type or 'application/octet-stream',
            category=category,
            client_id=client_id,
            trainer_id=trainer_id,
            session_id=session_id,
            description=description,
            uploaded_by=uploaded_by
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': new_file.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@file_bp.route('/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """Get file metadata"""
    try:
        file = File.query.get_or_404(file_id)
        return jsonify(file.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """Download a file"""
    try:
        file = File.query.get_or_404(file_id)
        
        if not os.path.exists(file.file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        return send_file(
            file.file_path,
            as_attachment=True,
            download_name=file.original_filename,
            mimetype=file.file_type
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_bp.route('/<int:file_id>', methods=['PUT'])
def update_file(file_id):
    """Update file metadata"""
    try:
        file = File.query.get_or_404(file_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'category' in data:
            file.category = data['category']
        if 'description' in data:
            file.description = data['description']
        if 'client_id' in data:
            file.client_id = data['client_id']
        if 'trainer_id' in data:
            file.trainer_id = data['trainer_id']
        if 'session_id' in data:
            file.session_id = data['session_id']
        
        db.session.commit()
        
        return jsonify({
            'message': 'File updated successfully',
            'file': file.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@file_bp.route('/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file"""
    try:
        file = File.query.get_or_404(file_id)
        
        # Delete physical file
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
        
        # Delete database record
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({'message': 'File deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@file_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get list of file categories"""
    categories = [
        {'value': 'workout_plan', 'label': 'Workout Plan'},
        {'value': 'waiver', 'label': 'Waiver/Contract'},
        {'value': 'assessment', 'label': 'Assessment'},
        {'value': 'progress_photo', 'label': 'Progress Photo'},
        {'value': 'document', 'label': 'Document'},
        {'value': 'video', 'label': 'Video'},
        {'value': 'other', 'label': 'Other'}
    ]
    return jsonify({'categories': categories})

@file_bp.route('/stats', methods=['GET'])
def get_file_stats():
    """Get file statistics"""
    try:
        client_id = request.args.get('client_id', type=int)
        
        query = File.query
        if client_id:
            query = query.filter_by(client_id=client_id)
        
        total_files = query.count()
        total_size = db.session.query(db.func.sum(File.file_size)).filter_by(client_id=client_id).scalar() or 0
        
        # Count by category
        categories = db.session.query(
            File.category,
            db.func.count(File.id)
        ).filter_by(client_id=client_id).group_by(File.category).all() if client_id else \
        db.session.query(
            File.category,
            db.func.count(File.id)
        ).group_by(File.category).all()
        
        return jsonify({
            'total_files': total_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_category': {cat: count for cat, count in categories}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
