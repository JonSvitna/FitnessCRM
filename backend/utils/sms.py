"""
SMS notification utilities for FitnessCRM
Handles sending SMS notifications via Twilio
"""

import os
from models.database import Settings
from utils.logger import logger

# Twilio client (lazy initialization)
_twilio_client = None

def get_twilio_client():
    """Get or initialize Twilio client"""
    global _twilio_client
    
    if _twilio_client is not None:
        return _twilio_client
    
    try:
        from twilio.rest import Client
        
        # Get settings from database
        settings = Settings.query.first()
        if not settings or not settings.twilio_enabled:
            logger.warning('Twilio is not enabled in settings')
            return None
        
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
            logger.warning('Twilio credentials not configured')
            return None
        
        _twilio_client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        return _twilio_client
    except ImportError:
        logger.warning('Twilio library not installed')
        return None
    except Exception as e:
        logger.error(f'Error initializing Twilio client: {str(e)}')
        return None

def send_sms(to, message, from_number=None):
    """
    Send an SMS message via Twilio
    
    Args:
        to: Recipient phone number (E.164 format: +1234567890)
        message: Message content (max 1600 characters)
        from_number: Sender phone number (optional, uses settings default)
    
    Returns:
        dict: {'success': bool, 'message_sid': str, 'error': str}
    """
    client = get_twilio_client()
    if not client:
        return {
            'success': False,
            'error': 'Twilio is not configured or enabled'
        }
    
    try:
        # Get settings for default from number
        settings = Settings.query.first()
        if not settings or not settings.twilio_phone_number:
            return {
                'success': False,
                'error': 'Twilio phone number not configured'
            }
        
        from_number = from_number or settings.twilio_phone_number
        
        # Validate phone number format (basic check)
        if not to.startswith('+'):
            # Try to format if missing country code
            logger.warning(f'Phone number {to} missing country code. Should be in E.164 format (+1234567890)')
        
        # Send SMS
        message_obj = client.messages.create(
            body=message,
            from_=from_number,
            to=to
        )
        
        logger.info(f'SMS sent to {to}: {message_obj.sid}')
        
        return {
            'success': True,
            'message_sid': message_obj.sid,
            'status': message_obj.status,
            'to': to,
            'from': from_number
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error sending SMS to {to}: {error_msg}')
        return {
            'success': False,
            'error': error_msg
        }

def send_session_reminder_sms(client_phone, client_name, trainer_name, session_date, location):
    """Send session reminder SMS to client"""
    message = f"Hi {client_name}, reminder: Your session with {trainer_name} is scheduled for {session_date.strftime('%B %d, %Y at %I:%M %p')} at {location}. See you there!"
    return send_sms(client_phone, message)

def send_payment_reminder_sms(client_phone, client_name, amount, due_date):
    """Send payment reminder SMS to client"""
    message = f"Hi {client_name}, friendly reminder: Your payment of ${amount:.2f} is due on {due_date.strftime('%B %d, %Y')}. Thank you!"
    return send_sms(client_phone, message)

def send_birthday_sms(client_phone, client_name):
    """Send birthday message SMS to client"""
    message = f"Happy Birthday {client_name}! 🎉 Wishing you a fantastic day filled with health and happiness!"
    return send_sms(client_phone, message)

def send_welcome_sms(client_phone, client_name, trainer_name):
    """Send welcome SMS to new client"""
    message = f"Welcome {client_name}! You've been assigned to {trainer_name}. We're excited to help you reach your fitness goals!"
    return send_sms(client_phone, message)

def format_phone_number(phone):
    """
    Format phone number to E.164 format
    Basic implementation - assumes US numbers if no country code
    
    Args:
        phone: Phone number in various formats
    
    Returns:
        str: Formatted phone number in E.164 format
    """
    if not phone:
        return None
    
    # Remove all non-digit characters except +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # If starts with +, assume already formatted
    if cleaned.startswith('+'):
        return cleaned
    
    # If 10 digits, assume US number and add +1
    if len(cleaned) == 10:
        return f'+1{cleaned}'
    
    # If 11 digits and starts with 1, add +
    if len(cleaned) == 11 and cleaned.startswith('1'):
        return f'+{cleaned}'
    
    # Return as-is if can't determine format
    return cleaned

