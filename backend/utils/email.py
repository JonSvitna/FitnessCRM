"""
Email notification utilities for FitnessCRM
Handles sending email notifications for various events
"""

import os
from flask_mail import Mail, Message
from utils.logger import logger

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app"""
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME', ''))
    
    mail.init_app(app)
    return mail

def send_email(to, subject, body, html=None):
    """
    Send an email
    
    Args:
        to: Recipient email address or list of addresses
        subject: Email subject
        body: Plain text body
        html: HTML body (optional)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    # Check if email is enabled
    if not os.getenv('MAIL_USERNAME'):
        logger.warning('Email not configured. Skipping email send.')
        return False
    
    try:
        msg = Message(subject=subject,
                     recipients=[to] if isinstance(to, str) else to,
                     body=body,
                     html=html)
        mail.send(msg)
        logger.info(f'Email sent to {to}: {subject}')
        return True
    except Exception as e:
        logger.error(f'Error sending email to {to}: {str(e)}')
        return False

def send_welcome_email(client_name, client_email):
    """Send welcome email to new client"""
    subject = f'Welcome to FitnessCRM, {client_name}!'
    body = f"""
    Hi {client_name},

    Welcome to FitnessCRM! We're excited to have you join our fitness community.

    Your trainer will be in touch soon to discuss your fitness goals and create
    a personalized training plan just for you.

    If you have any questions, feel free to reach out to us.

    Best regards,
    The FitnessCRM Team
    """
    
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #ea580c;">Welcome to FitnessCRM, {client_name}!</h2>
          <p>We're excited to have you join our fitness community.</p>
          <p>Your trainer will be in touch soon to discuss your fitness goals and create
          a personalized training plan just for you.</p>
          <p>If you have any questions, feel free to reach out to us.</p>
          <p style="margin-top: 30px;">
            Best regards,<br>
            <strong>The FitnessCRM Team</strong>
          </p>
        </div>
      </body>
    </html>
    """
    
    return send_email(client_email, subject, body, html)

def send_assignment_notification(trainer_email, trainer_name, client_name):
    """Send notification when client is assigned to trainer"""
    subject = f'New Client Assignment: {client_name}'
    body = f"""
    Hi {trainer_name},

    You have been assigned a new client: {client_name}

    You can now view their profile and start planning their training program
    in your FitnessCRM dashboard.

    Best regards,
    The FitnessCRM Team
    """
    
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #ea580c;">New Client Assignment</h2>
          <p>Hi {trainer_name},</p>
          <p>You have been assigned a new client: <strong>{client_name}</strong></p>
          <p>You can now view their profile and start planning their training program
          in your FitnessCRM dashboard.</p>
          <p style="margin-top: 30px;">
            Best regards,<br>
            <strong>The FitnessCRM Team</strong>
          </p>
        </div>
      </body>
    </html>
    """
    
    return send_email(trainer_email, subject, body, html)

def send_client_assignment_notification(client_email, client_name, trainer_name):
    """Send notification to client when assigned to trainer"""
    subject = f'Meet Your Trainer: {trainer_name}'
    body = f"""
    Hi {client_name},

    Great news! You have been assigned to {trainer_name}.

    Your trainer will reach out to you soon to schedule your first session
    and discuss your fitness goals.

    Best regards,
    The FitnessCRM Team
    """
    
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #ea580c;">Meet Your Trainer</h2>
          <p>Hi {client_name},</p>
          <p>Great news! You have been assigned to <strong>{trainer_name}</strong>.</p>
          <p>Your trainer will reach out to you soon to schedule your first session
          and discuss your fitness goals.</p>
          <p style="margin-top: 30px;">
            Best regards,<br>
            <strong>The FitnessCRM Team</strong>
          </p>
        </div>
      </body>
    </html>
    """
    
    return send_email(client_email, subject, body, html)
