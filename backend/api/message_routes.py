"""
Message API routes for Phase 5: Communication
Handles in-app messaging between trainers and clients
"""

from flask import Blueprint, request, jsonify
from models.database import db, MessageThread, Message, MessageAttachment, Trainer, Client, File
from sqlalchemy import func
from utils.logger import logger
from datetime import datetime

message_bp = Blueprint('messages', __name__, url_prefix='/api/messages')

@message_bp.route('/threads', methods=['GET'])
def get_threads():
    """Get all message threads for a user"""
    try:
        user_type = request.args.get('user_type')  # 'trainer' or 'client'
        user_id = request.args.get('user_id', type=int)
        archived = request.args.get('archived', 'false').lower() == 'true'
        
        if not user_type or not user_id:
            return jsonify({'error': 'user_type and user_id are required'}), 400
        
        query = MessageThread.query
        
        if user_type == 'trainer':
            query = query.filter_by(trainer_id=user_id)
            if archived:
                query = query.filter_by(archived_by_trainer=True)
            else:
                query = query.filter_by(archived_by_trainer=False)
        elif user_type == 'client':
            query = query.filter_by(client_id=user_id)
            if archived:
                query = query.filter_by(archived_by_client=True)
            else:
                query = query.filter_by(archived_by_client=False)
        else:
            return jsonify({'error': 'user_type must be "trainer" or "client"'}), 400
        
        threads = query.order_by(MessageThread.last_message_at.desc()).all()
        
        return jsonify({
            'threads': [thread.to_dict() for thread in threads]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting threads: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/threads', methods=['POST'])
def create_thread():
    """Create a new message thread"""
    try:
        data = request.get_json()
        
        trainer_id = data.get('trainer_id')
        client_id = data.get('client_id')
        subject = data.get('subject', '')
        initial_message = data.get('initial_message', '')
        
        if not trainer_id or not client_id:
            return jsonify({'error': 'trainer_id and client_id are required'}), 400
        
        # Check if thread already exists
        existing_thread = MessageThread.query.filter_by(
            trainer_id=trainer_id,
            client_id=client_id
        ).first()
        
        if existing_thread:
            return jsonify({
                'thread': existing_thread.to_dict(),
                'message': 'Thread already exists'
            }), 200
        
        # Create new thread
        thread = MessageThread(
            trainer_id=trainer_id,
            client_id=client_id,
            subject=subject
        )
        db.session.add(thread)
        db.session.flush()  # Get thread ID
        
        # Add initial message if provided
        if initial_message:
            sender_type = data.get('sender_type', 'trainer')  # Default to trainer
            sender_id = trainer_id if sender_type == 'trainer' else client_id
            
            message = Message(
                thread_id=thread.id,
                sender_type=sender_type,
                sender_id=sender_id,
                content=initial_message
            )
            db.session.add(message)
            
            # Update thread metadata
            thread.last_message_at = datetime.utcnow()
            thread.last_message_by = sender_type
            
            # Update unread count
            if sender_type == 'trainer':
                thread.client_unread_count += 1
            else:
                thread.trainer_unread_count += 1
        
        db.session.commit()
        
        return jsonify({
            'thread': thread.to_dict(include_messages=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating thread: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/threads/<int:thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Get a specific thread with messages"""
    try:
        thread = MessageThread.query.get_or_404(thread_id)
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        per_page = min(per_page, 100)  # Max 100 messages per page
        
        # Get messages with pagination
        messages = thread.messages.filter_by(deleted_by_sender=False)\
            .order_by(Message.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        thread_dict = thread.to_dict()
        thread_dict['messages'] = [msg.to_dict() for msg in reversed(messages.items)]
        thread_dict['pagination'] = {
            'page': page,
            'per_page': per_page,
            'total': messages.total,
            'pages': messages.pages,
            'has_next': messages.has_next,
            'has_prev': messages.has_prev
        }
        
        return jsonify({'thread': thread_dict}), 200
        
    except Exception as e:
        logger.error(f"Error getting thread: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/threads/<int:thread_id>/archive', methods=['PUT'])
def archive_thread(thread_id):
    """Archive or unarchive a thread"""
    try:
        data = request.get_json()
        user_type = data.get('user_type')  # 'trainer' or 'client'
        archived = data.get('archived', True)
        
        if not user_type:
            return jsonify({'error': 'user_type is required'}), 400
        
        thread = MessageThread.query.get_or_404(thread_id)
        
        if user_type == 'trainer':
            thread.archived_by_trainer = archived
        elif user_type == 'client':
            thread.archived_by_client = archived
        else:
            return jsonify({'error': 'user_type must be "trainer" or "client"'}), 400
        
        db.session.commit()
        
        return jsonify({'thread': thread.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error archiving thread: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/threads/<int:thread_id>/messages', methods=['POST'])
def create_message(thread_id):
    """Create a new message in a thread"""
    try:
        thread = MessageThread.query.get_or_404(thread_id)
        data = request.get_json()
        
        sender_type = data.get('sender_type')  # 'trainer' or 'client'
        sender_id = data.get('sender_id', type=int)
        content = data.get('content', '').strip()
        attachment_ids = data.get('attachment_ids', [])
        
        if not sender_type or not sender_id:
            return jsonify({'error': 'sender_type and sender_id are required'}), 400
        
        if not content and not attachment_ids:
            return jsonify({'error': 'content or attachments are required'}), 400
        
        # Validate sender
        if sender_type == 'trainer' and sender_id != thread.trainer_id:
            return jsonify({'error': 'Invalid trainer_id for this thread'}), 403
        elif sender_type == 'client' and sender_id != thread.client_id:
            return jsonify({'error': 'Invalid client_id for this thread'}), 403
        
        # Create message
        message = Message(
            thread_id=thread_id,
            sender_type=sender_type,
            sender_id=sender_id,
            content=content
        )
        db.session.add(message)
        db.session.flush()  # Get message ID
        
        # Add attachments
        if attachment_ids:
            for file_id in attachment_ids:
                # Verify file exists
                file = File.query.get(file_id)
                if file:
                    attachment = MessageAttachment(
                        message_id=message.id,
                        file_id=file_id
                    )
                    db.session.add(attachment)
        
        # Update thread metadata
        thread.last_message_at = datetime.utcnow()
        thread.last_message_by = sender_type
        
        # Update unread counts
        if sender_type == 'trainer':
            thread.client_unread_count += 1
            thread.trainer_unread_count = 0  # Reset trainer unread count
        else:
            thread.trainer_unread_count += 1
            thread.client_unread_count = 0  # Reset client unread count
        
        db.session.commit()
        
        return jsonify({'message': message.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/messages/<int:message_id>/read', methods=['PUT'])
def mark_message_read(message_id):
    """Mark a message as read"""
    try:
        message = Message.query.get_or_404(message_id)
        thread = message.thread
        
        data = request.get_json()
        user_type = data.get('user_type')  # 'trainer' or 'client'
        
        if not user_type:
            return jsonify({'error': 'user_type is required'}), 400
        
        # Only mark as read if the user is the recipient
        if user_type == 'trainer' and message.sender_type == 'client':
            if not message.read:
                message.read = True
                message.read_at = datetime.utcnow()
                thread.trainer_unread_count = max(0, thread.trainer_unread_count - 1)
        elif user_type == 'client' and message.sender_type == 'trainer':
            if not message.read:
                message.read = True
                message.read_at = datetime.utcnow()
                thread.client_unread_count = max(0, thread.client_unread_count - 1)
        
        db.session.commit()
        
        return jsonify({'message': message.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error marking message as read: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/threads/<int:thread_id>/read', methods=['PUT'])
def mark_thread_read(thread_id):
    """Mark all messages in a thread as read"""
    try:
        thread = MessageThread.query.get_or_404(thread_id)
        data = request.get_json()
        user_type = data.get('user_type')  # 'trainer' or 'client'
        
        if not user_type:
            return jsonify({'error': 'user_type is required'}), 400
        
        # Mark all unread messages from the other user as read
        if user_type == 'trainer':
            unread_messages = Message.query.filter_by(
                thread_id=thread_id,
                sender_type='client',
                read=False
            ).all()
            for msg in unread_messages:
                msg.read = True
                msg.read_at = datetime.utcnow()
            thread.trainer_unread_count = 0
        elif user_type == 'client':
            unread_messages = Message.query.filter_by(
                thread_id=thread_id,
                sender_type='trainer',
                read=False
            ).all()
            for msg in unread_messages:
                msg.read = True
                msg.read_at = datetime.utcnow()
            thread.client_unread_count = 0
        
        db.session.commit()
        
        return jsonify({'thread': thread.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error marking thread as read: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message (soft delete)"""
    try:
        message = Message.query.get_or_404(message_id)
        data = request.get_json()
        user_type = data.get('user_type')  # 'trainer' or 'client'
        sender_id = data.get('sender_id', type=int)
        
        if not user_type or not sender_id:
            return jsonify({'error': 'user_type and sender_id are required'}), 400
        
        # Only allow sender to delete their own message
        if message.sender_type != user_type or message.sender_id != sender_id:
            return jsonify({'error': 'Unauthorized to delete this message'}), 403
        
        message.deleted_by_sender = True
        db.session.commit()
        
        return jsonify({'message': 'Message deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/search', methods=['GET'])
def search_messages():
    """Search messages by content"""
    try:
        query = request.args.get('q', '').strip()
        user_type = request.args.get('user_type')
        user_id = request.args.get('user_id', type=int)
        thread_id = request.args.get('thread_id', type=int)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        if not user_type or not user_id:
            return jsonify({'error': 'user_type and user_id are required'}), 400
        
        # Build query
        message_query = Message.query.join(MessageThread).filter(
            Message.content.ilike(f'%{query}%'),
            Message.deleted_by_sender == False
        )
        
        # Filter by user
        if user_type == 'trainer':
            message_query = message_query.filter(MessageThread.trainer_id == user_id)
        elif user_type == 'client':
            message_query = message_query.filter(MessageThread.client_id == user_id)
        
        # Filter by thread if specified
        if thread_id:
            message_query = message_query.filter(Message.thread_id == thread_id)
        
        # Get results
        messages = message_query.order_by(Message.created_at.desc()).limit(50).all()
        
        return jsonify({
            'messages': [msg.to_dict() for msg in messages],
            'count': len(messages)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching messages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """Get unread message count for a user"""
    try:
        user_type = request.args.get('user_type')
        user_id = request.args.get('user_id', type=int)
        
        if not user_type or not user_id:
            return jsonify({'error': 'user_type and user_id are required'}), 400
        
        if user_type == 'trainer':
            count = db.session.query(func.sum(MessageThread.trainer_unread_count))\
                .filter_by(trainer_id=user_id, archived_by_trainer=False)\
                .scalar() or 0
        elif user_type == 'client':
            count = db.session.query(func.sum(MessageThread.client_unread_count))\
                .filter_by(client_id=user_id, archived_by_client=False)\
                .scalar() or 0
        else:
            return jsonify({'error': 'user_type must be "trainer" or "client"'}), 400
        
        return jsonify({'unread_count': int(count)}), 200
        
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        return jsonify({'error': str(e)}), 500

