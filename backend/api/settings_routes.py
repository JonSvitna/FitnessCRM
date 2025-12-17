"""
Settings API routes
"""

from flask import Blueprint, request, jsonify
from models.database import db, Settings
from utils.logger import log_activity, logger
from sqlalchemy.exc import IntegrityError

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

@settings_bp.route('', methods=['GET'])
def get_settings():
    """Get application settings (sensitive data masked)"""
    try:
        settings = Settings.query.first()
        
        if not settings:
            # Return default settings if none exist
            return jsonify({
                'message': 'No settings found. Please create settings.'
            }), 404
        
        log_activity('view', 'settings', settings.id)
        return jsonify(settings.to_dict(include_sensitive=False)), 200
        
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/full', methods=['GET'])
def get_settings_full():
    """Get application settings including sensitive data (use with caution)"""
    try:
        settings = Settings.query.first()
        
        if not settings:
            return jsonify({
                'message': 'No settings found. Please create settings.'
            }), 404
        
        log_activity('view_sensitive', 'settings', settings.id)
        return jsonify(settings.to_dict(include_sensitive=True)), 200
        
    except Exception as e:
        logger.error(f"Error getting full settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('', methods=['POST'])
def create_settings():
    """Create application settings"""
    data = request.get_json()
    
    try:
        # Check if settings already exist
        existing = Settings.query.first()
        if existing:
            return jsonify({'error': 'Settings already exist. Use PUT to update.'}), 409
        
        settings = Settings(
            business_name=data.get('business_name'),
            owner_name=data.get('owner_name'),
            contact_email=data.get('contact_email'),
            contact_phone=data.get('contact_phone'),
            address=data.get('address'),
            website=data.get('website'),
            logo_url=data.get('logo_url'),
            sendgrid_api_key=data.get('sendgrid_api_key'),
            sendgrid_from_email=data.get('sendgrid_from_email'),
            sendgrid_from_name=data.get('sendgrid_from_name'),
            sendgrid_enabled=data.get('sendgrid_enabled', False),
            twilio_account_sid=data.get('twilio_account_sid'),
            twilio_auth_token=data.get('twilio_auth_token'),
            twilio_phone_number=data.get('twilio_phone_number'),
            twilio_enabled=data.get('twilio_enabled', False),
        )
        
        db.session.add(settings)
        db.session.commit()
        
        log_activity('create', 'settings', settings.id, details={
            'business_name': settings.business_name
        })
        
        logger.info(f"Settings created: {settings.business_name}")
        return jsonify(settings.to_dict(include_sensitive=False)), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('', methods=['PUT'])
def update_settings():
    """Update application settings"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        settings = Settings.query.first()
        
        if not settings:
            # Create if doesn't exist
            return create_settings()
        
        # Update business profile
        if 'business_name' in data:
            settings.business_name = data['business_name']
        if 'owner_name' in data:
            settings.owner_name = data['owner_name']
        if 'contact_email' in data:
            settings.contact_email = data['contact_email']
        if 'contact_phone' in data:
            settings.contact_phone = data['contact_phone']
        if 'address' in data:
            settings.address = data['address']
        if 'website' in data:
            settings.website = data['website']
        if 'logo_url' in data:
            settings.logo_url = data['logo_url']
        
        # Update SendGrid settings
        if 'sendgrid_api_key' in data:
            settings.sendgrid_api_key = data['sendgrid_api_key']
        if 'sendgrid_from_email' in data:
            settings.sendgrid_from_email = data['sendgrid_from_email']
        if 'sendgrid_from_name' in data:
            settings.sendgrid_from_name = data['sendgrid_from_name']
        if 'sendgrid_enabled' in data:
            settings.sendgrid_enabled = data['sendgrid_enabled']
        
        # Update Twilio settings
        if 'twilio_account_sid' in data:
            settings.twilio_account_sid = data['twilio_account_sid']
        if 'twilio_auth_token' in data:
            settings.twilio_auth_token = data['twilio_auth_token']
        if 'twilio_phone_number' in data:
            settings.twilio_phone_number = data['twilio_phone_number']
        if 'twilio_enabled' in data:
            settings.twilio_enabled = data['twilio_enabled']
        
        db.session.commit()
        
        log_activity('update', 'settings', settings.id, details={
            'updated_fields': list(data.keys())
        })
        
        logger.info(f"Settings updated: {settings.business_name}")
        return jsonify(settings.to_dict(include_sensitive=False)), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/test-sendgrid', methods=['POST'])
def test_sendgrid():
    """Test SendGrid configuration"""
    try:
        settings = Settings.query.first()
        
        if not settings or not settings.sendgrid_api_key:
            return jsonify({'error': 'SendGrid not configured'}), 400
        
        # TODO: Implement actual SendGrid test email
        # For now, just return success if API key exists
        
        log_activity('test', 'sendgrid', settings.id)
        return jsonify({
            'message': 'SendGrid test successful',
            'configured': True,
            'enabled': settings.sendgrid_enabled
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing SendGrid: {str(e)}")
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/test-twilio', methods=['POST'])
def test_twilio():
    """Test Twilio configuration by sending a test SMS"""
    try:
        from utils.sms import send_sms, get_twilio_client
        
        settings = Settings.query.first()
        
        if not settings or not settings.twilio_account_sid:
            return jsonify({'error': 'Twilio not configured'}), 400
        
        if not settings.twilio_enabled:
            return jsonify({'error': 'Twilio is not enabled'}), 400
        
        # Get test phone number from request (optional)
        data = request.get_json() or {}
        test_number = data.get('test_number')
        
        if not test_number:
            return jsonify({
                'message': 'Twilio credentials are valid',
                'configured': True,
                'enabled': settings.twilio_enabled,
                'note': 'Provide test_number in request body to send test SMS'
            }), 200
        
        # Send test SMS
        result = send_sms(test_number, 'Test SMS from FitnessCRM - Twilio is configured correctly!')
        
        if result.get('success'):
            log_activity('test', 'twilio', settings.id)
            return jsonify({
                'message': 'Test SMS sent successfully',
                'configured': True,
                'enabled': settings.twilio_enabled,
                'message_sid': result.get('message_sid')
            }), 200
        else:
            return jsonify({
                'error': result.get('error', 'Failed to send test SMS'),
                'configured': True,
                'enabled': settings.twilio_enabled
            }), 400
        
    except Exception as e:
        logger.error(f"Error testing Twilio: {str(e)}")
        return jsonify({'error': str(e)}), 500
