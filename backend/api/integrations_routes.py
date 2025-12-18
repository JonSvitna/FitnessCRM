"""
Third-party integrations routes
Phase 6: Mobile & Integrations - M6.4: Third-Party Integrations
"""

from flask import Blueprint, request, jsonify, redirect, url_for
from models.database import db, Client, Trainer, Session
from utils.logger import logger
from datetime import datetime, timedelta
import os
import json

integrations_bp = Blueprint('integrations', __name__, url_prefix='/api/integrations')

# Integration configuration storage (in production, use database)
_integration_configs = {}

# Google Calendar Integration
@integrations_bp.route('/google-calendar/auth', methods=['GET'])
def google_calendar_auth():
    """Initiate Google Calendar OAuth flow"""
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    redirect_uri = request.host_url.rstrip('/') + '/api/integrations/google-calendar/callback'
    
    if not client_id:
        return jsonify({'error': 'Google Calendar integration not configured'}), 503
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=https://www.googleapis.com/auth/calendar&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return jsonify({'auth_url': auth_url}), 200

@integrations_bp.route('/google-calendar/callback', methods=['GET'])
def google_calendar_callback():
    """Handle Google Calendar OAuth callback"""
    code = request.args.get('code')
    
    if not code:
        return jsonify({'error': 'Authorization code not provided'}), 400
    
    # In production, exchange code for tokens and store securely
    # For now, return success
    logger.info(f"Google Calendar OAuth callback received: {code[:20]}...")
    
    return jsonify({
        'message': 'Google Calendar connected successfully',
        'status': 'connected'
    }), 200

@integrations_bp.route('/google-calendar/sync', methods=['POST'])
def google_calendar_sync():
    """Sync sessions to Google Calendar"""
    data = request.get_json()
    session_ids = data.get('session_ids', [])
    
    if not session_ids:
        return jsonify({'error': 'No session IDs provided'}), 400
    
    try:
        sessions = Session.query.filter(Session.id.in_(session_ids)).all()
        synced_count = 0
        
        for session in sessions:
            # In production, create Google Calendar event
            # For now, just log
            logger.info(f"Syncing session {session.id} to Google Calendar")
            synced_count += 1
        
        return jsonify({
            'message': f'{synced_count} sessions synced to Google Calendar',
            'synced_count': synced_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error syncing to Google Calendar: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Calendly Integration
@integrations_bp.route('/calendly/webhook', methods=['POST'])
def calendly_webhook():
    """Handle Calendly webhook events"""
    data = request.get_json()
    event_type = data.get('event')
    
    if event_type == 'invitee.created':
        # Create session from Calendly event
        invitee = data.get('payload', {}).get('invitee', {})
        event = data.get('payload', {}).get('event', {})
        
        # Extract information
        client_email = invitee.get('email')
        event_start = event.get('start_time')
        event_end = event.get('end_time')
        
        # Find or create client
        client = Client.query.filter_by(email=client_email).first()
        
        if client and event_start:
            try:
                session = Session(
                    client_id=client.id,
                    session_date=datetime.fromisoformat(event_start.replace('Z', '+00:00')),
                    duration_minutes=int((datetime.fromisoformat(event_end.replace('Z', '+00:00')) - 
                                         datetime.fromisoformat(event_start.replace('Z', '+00:00'))).total_seconds() / 60),
                    status='scheduled',
                    notes=f"Created from Calendly: {event.get('name', 'Session')}"
                )
                db.session.add(session)
                db.session.commit()
                
                logger.info(f"Session created from Calendly webhook: {session.id}")
                
                return jsonify({'message': 'Session created successfully'}), 200
            except Exception as e:
                logger.error(f"Error creating session from Calendly: {str(e)}")
                return jsonify({'error': str(e)}), 500
    
    return jsonify({'message': 'Webhook received'}), 200

# Zoom Integration
@integrations_bp.route('/zoom/generate-link', methods=['POST'])
def zoom_generate_link():
    """Generate Zoom meeting link for a session"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400
    
    session = Session.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # In production, use Zoom API to create meeting
    # For now, return placeholder
    zoom_link = f"https://zoom.us/j/{session_id}123456"
    
    # Update session notes with Zoom link
    if session.notes:
        session.notes += f"\nZoom Link: {zoom_link}"
    else:
        session.notes = f"Zoom Link: {zoom_link}"
    
    db.session.commit()
    
    return jsonify({
        'zoom_link': zoom_link,
        'meeting_id': f"{session_id}123456"
    }), 200

# MyFitnessPal Integration (placeholder - would require API access)
@integrations_bp.route('/myfitnesspal/connect', methods=['POST'])
def myfitnesspal_connect():
    """Connect MyFitnessPal account"""
    data = request.get_json()
    client_id = data.get('client_id')
    username = data.get('username')
    
    if not client_id or not username:
        return jsonify({'error': 'client_id and username are required'}), 400
    
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    # Store connection (in production, use database)
    _integration_configs[f'myfitnesspal_{client_id}'] = {
        'username': username,
        'connected_at': datetime.utcnow().isoformat()
    }
    
    logger.info(f"MyFitnessPal connected for client {client_id}: {username}")
    
    return jsonify({
        'message': 'MyFitnessPal connected successfully',
        'status': 'connected'
    }), 200

# Zapier Integration - Webhook endpoint
@integrations_bp.route('/zapier/webhook', methods=['POST'])
def zapier_webhook():
    """Handle Zapier webhook events"""
    data = request.get_json()
    event_type = data.get('event_type')
    
    # Log webhook for debugging
    logger.info(f"Zapier webhook received: {event_type}")
    
    # Process different event types
    if event_type == 'client.created':
        # Forward client creation to Zapier
        client_data = data.get('data', {})
        # In production, send to Zapier webhook URL
        return jsonify({'message': 'Webhook processed'}), 200
    
    elif event_type == 'session.created':
        # Forward session creation to Zapier
        session_data = data.get('data', {})
        return jsonify({'message': 'Webhook processed'}), 200
    
    return jsonify({'message': 'Webhook received'}), 200

# Generic Webhook System
@integrations_bp.route('/webhooks', methods=['GET'])
def list_webhooks():
    """List configured webhooks"""
    # In production, fetch from database
    webhooks = []
    
    return jsonify({'webhooks': webhooks}), 200

@integrations_bp.route('/webhooks', methods=['POST'])
def create_webhook():
    """Create a custom webhook"""
    data = request.get_json()
    
    if not data or not data.get('url') or not data.get('events'):
        return jsonify({'error': 'url and events are required'}), 400
    
    webhook = {
        'id': len(_integration_configs) + 1,
        'url': data['url'],
        'events': data['events'],
        'active': data.get('active', True),
        'created_at': datetime.utcnow().isoformat()
    }
    
    # In production, save to database
    _integration_configs[f"webhook_{webhook['id']}"] = webhook
    
    logger.info(f"Webhook created: {webhook['id']}")
    
    return jsonify(webhook), 201

@integrations_bp.route('/webhooks/<int:webhook_id>', methods=['DELETE'])
def delete_webhook(webhook_id):
    """Delete a webhook"""
    webhook_key = f"webhook_{webhook_id}"
    
    if webhook_key not in _integration_configs:
        return jsonify({'error': 'Webhook not found'}), 404
    
    del _integration_configs[webhook_key]
    
    logger.info(f"Webhook deleted: {webhook_id}")
    
    return jsonify({'message': 'Webhook deleted successfully'}), 200

# Integration status
@integrations_bp.route('/status', methods=['GET'])
def get_integration_status():
    """Get status of all integrations"""
    status = {
        'google_calendar': {
            'configured': bool(os.getenv('GOOGLE_CLIENT_ID')),
            'connected': False  # Check from database in production
        },
        'calendly': {
            'configured': True,
            'connected': True
        },
        'zoom': {
            'configured': bool(os.getenv('ZOOM_API_KEY')),
            'connected': False
        },
        'myfitnesspal': {
            'configured': False,
            'connected': False
        },
        'zapier': {
            'configured': True,
            'connected': True
        }
    }
    
    return jsonify(status), 200

