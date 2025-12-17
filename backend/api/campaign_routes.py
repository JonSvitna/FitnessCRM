"""
Email Campaign API routes for Phase 5: Communication
Handles email campaigns, templates, segmentation, A/B testing, and analytics
"""

from flask import Blueprint, request, jsonify
from models.database import db, EmailCampaign, EmailTemplate, CampaignRecipient, Client, Trainer
from utils.email import send_email
from utils.logger import logger
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import random
import re

campaign_bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')

# ============================================================================
# TEMPLATE ROUTES
# ============================================================================

@campaign_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get all email templates"""
    try:
        category = request.args.get('category')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = EmailTemplate.query
        
        if category:
            query = query.filter_by(category=category)
        
        if active_only:
            query = query.filter_by(active=True)
        
        templates = query.order_by(EmailTemplate.name).all()
        
        return jsonify({
            'templates': [t.to_dict() for t in templates]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/templates', methods=['POST'])
def create_template():
    """Create a new email template"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        category = data.get('category', 'custom')
        subject = data.get('subject')
        html_body = data.get('html_body')
        text_body = data.get('text_body')
        variables = data.get('variables', [])
        
        if not name or not subject or not html_body:
            return jsonify({'error': 'name, subject, and html_body are required'}), 400
        
        template = EmailTemplate(
            name=name,
            category=category,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            variables=','.join(variables) if isinstance(variables, list) else variables,
            active=True
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({'template': template.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an email template"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        data = request.get_json()
        
        if 'name' in data:
            template.name = data['name']
        if 'category' in data:
            template.category = data['category']
        if 'subject' in data:
            template.subject = data['subject']
        if 'html_body' in data:
            template.html_body = data['html_body']
        if 'text_body' in data:
            template.text_body = data['text_body']
        if 'variables' in data:
            variables = data['variables']
            template.variables = ','.join(variables) if isinstance(variables, list) else variables
        if 'active' in data:
            template.active = data['active']
        
        db.session.commit()
        
        return jsonify({'template': template.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete an email template"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': 'Template deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting template: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CAMPAIGN ROUTES
# ============================================================================

@campaign_bp.route('', methods=['GET'])
def get_campaigns():
    """Get all email campaigns"""
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)
        
        query = EmailCampaign.query
        
        if status:
            query = query.filter_by(status=status)
        
        campaigns = query.order_by(EmailCampaign.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'campaigns': [c.to_dict() for c in campaigns.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': campaigns.total,
                'pages': campaigns.pages,
                'has_next': campaigns.has_next,
                'has_prev': campaigns.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting campaigns: {str(e)}")
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('', methods=['POST'])
def create_campaign():
    """Create a new email campaign"""
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description')
        template_id = data.get('template_id')
        subject = data.get('subject')
        html_body = data.get('html_body')
        text_body = data.get('text_body')
        segment_type = data.get('segment_type', 'all_clients')
        segment_filters = data.get('segment_filters', {})
        recipient_ids = data.get('recipient_ids', [])
        ab_test_enabled = data.get('ab_test_enabled', False)
        ab_test_subject_a = data.get('ab_test_subject_a')
        ab_test_subject_b = data.get('ab_test_subject_b')
        ab_test_split_percentage = data.get('ab_test_split_percentage', 50)
        scheduled_at = data.get('scheduled_at')
        send_immediately = data.get('send_immediately', False)
        
        if not name or not subject or not html_body:
            return jsonify({'error': 'name, subject, and html_body are required'}), 400
        
        # If using template, load template content
        if template_id:
            template = EmailTemplate.query.get(template_id)
            if template:
                if not subject:
                    subject = template.subject
                if not html_body:
                    html_body = template.html_body
                if not text_body:
                    text_body = template.text_body
        
        # Parse scheduled_at
        scheduled_datetime = None
        if scheduled_at:
            if isinstance(scheduled_at, str):
                scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
            else:
                scheduled_datetime = scheduled_at
        
        campaign = EmailCampaign(
            name=name,
            description=description,
            template_id=template_id,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            segment_type=segment_type,
            segment_filters=segment_filters,
            recipient_ids=recipient_ids,
            ab_test_enabled=ab_test_enabled,
            ab_test_subject_a=ab_test_subject_a,
            ab_test_subject_b=ab_test_subject_b,
            ab_test_split_percentage=ab_test_split_percentage,
            scheduled_at=scheduled_datetime,
            send_immediately=send_immediately,
            status='draft' if not send_immediately and not scheduled_datetime else 'scheduled'
        )
        
        db.session.add(campaign)
        db.session.flush()
        
        # Build recipient list
        recipients = _build_recipient_list(campaign)
        campaign.total_recipients = len(recipients)
        
        # Create recipient records
        for recipient in recipients:
            recipient_record = CampaignRecipient(
                campaign_id=campaign.id,
                email=recipient['email'],
                recipient_type=recipient.get('type'),
                recipient_id=recipient.get('id'),
                ab_variant=_assign_ab_variant(ab_test_enabled, ab_test_split_percentage) if ab_test_enabled else None
            )
            db.session.add(recipient_record)
        
        db.session.commit()
        
        # Send immediately if requested
        if send_immediately:
            _send_campaign(campaign.id)
        
        return jsonify({'campaign': campaign.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get a specific campaign"""
    try:
        campaign = EmailCampaign.query.get_or_404(campaign_id)
        return jsonify({'campaign': campaign.to_dict()}), 200
    except Exception as e:
        logger.error(f"Error getting campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/<int:campaign_id>', methods=['PUT'])
def update_campaign(campaign_id):
    """Update a campaign"""
    try:
        campaign = EmailCampaign.query.get_or_404(campaign_id)
        data = request.get_json()
        
        # Only allow updates if campaign is in draft or scheduled status
        if campaign.status not in ['draft', 'scheduled']:
            return jsonify({'error': 'Cannot update campaign that has already been sent'}), 400
        
        if 'name' in data:
            campaign.name = data['name']
        if 'description' in data:
            campaign.description = data['description']
        if 'subject' in data:
            campaign.subject = data['subject']
        if 'html_body' in data:
            campaign.html_body = data['html_body']
        if 'text_body' in data:
            campaign.text_body = data['text_body']
        if 'segment_type' in data:
            campaign.segment_type = data['segment_type']
        if 'segment_filters' in data:
            campaign.segment_filters = data['segment_filters']
        if 'recipient_ids' in data:
            campaign.recipient_ids = data['recipient_ids']
        if 'ab_test_enabled' in data:
            campaign.ab_test_enabled = data['ab_test_enabled']
        if 'ab_test_subject_a' in data:
            campaign.ab_test_subject_a = data['ab_test_subject_a']
        if 'ab_test_subject_b' in data:
            campaign.ab_test_subject_b = data['ab_test_subject_b']
        if 'scheduled_at' in data:
            scheduled_at = data['scheduled_at']
            if scheduled_at:
                campaign.scheduled_at = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00')) if isinstance(scheduled_at, str) else scheduled_at
        
        db.session.commit()
        
        return jsonify({'campaign': campaign.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/<int:campaign_id>/send', methods=['POST'])
def send_campaign(campaign_id):
    """Send an email campaign"""
    try:
        campaign = EmailCampaign.query.get_or_404(campaign_id)
        
        if campaign.status == 'sent':
            return jsonify({'error': 'Campaign has already been sent'}), 400
        
        _send_campaign(campaign_id)
        
        return jsonify({'message': 'Campaign sending started', 'campaign': campaign.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error sending campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/<int:campaign_id>/cancel', methods=['POST'])
def cancel_campaign(campaign_id):
    """Cancel a scheduled campaign"""
    try:
        campaign = EmailCampaign.query.get_or_404(campaign_id)
        
        if campaign.status not in ['draft', 'scheduled']:
            return jsonify({'error': 'Can only cancel draft or scheduled campaigns'}), 400
        
        campaign.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'message': 'Campaign cancelled', 'campaign': campaign.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cancelling campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/<int:campaign_id>/recipients', methods=['GET'])
def get_campaign_recipients(campaign_id):
    """Get recipients for a campaign"""
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        per_page = min(per_page, 100)
        
        query = CampaignRecipient.query.filter_by(campaign_id=campaign_id)
        
        if status:
            query = query.filter_by(status=status)
        
        recipients = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'recipients': [r.to_dict() for r in recipients.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': recipients.total,
                'pages': recipients.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recipients: {str(e)}")
        return jsonify({'error': str(e)}), 500

@campaign_bp.route('/<int:campaign_id>/analytics', methods=['GET'])
def get_campaign_analytics(campaign_id):
    """Get analytics for a campaign"""
    try:
        campaign = EmailCampaign.query.get_or_404(campaign_id)
        
        # Calculate rates
        delivery_rate = (campaign.emails_delivered / campaign.total_recipients * 100) if campaign.total_recipients > 0 else 0
        open_rate = (campaign.emails_opened / campaign.emails_delivered * 100) if campaign.emails_delivered > 0 else 0
        click_rate = (campaign.emails_clicked / campaign.emails_delivered * 100) if campaign.emails_delivered > 0 else 0
        bounce_rate = (campaign.emails_bounced / campaign.total_recipients * 100) if campaign.total_recipients > 0 else 0
        
        # A/B test comparison if enabled
        ab_results = None
        if campaign.ab_test_enabled:
            variant_a = CampaignRecipient.query.filter_by(
                campaign_id=campaign_id,
                ab_variant='A'
            ).all()
            variant_b = CampaignRecipient.query.filter_by(
                campaign_id=campaign_id,
                ab_variant='B'
            ).all()
            
            a_opened = sum(1 for r in variant_a if r.status == 'opened')
            b_opened = sum(1 for r in variant_b if r.status == 'opened')
            a_clicked = sum(1 for r in variant_a if r.status == 'clicked')
            b_clicked = sum(1 for r in variant_b if r.status == 'clicked')
            
            ab_results = {
                'variant_a': {
                    'recipients': len(variant_a),
                    'opened': a_opened,
                    'clicked': a_clicked,
                    'open_rate': (a_opened / len(variant_a) * 100) if variant_a else 0,
                    'click_rate': (a_clicked / len(variant_a) * 100) if variant_a else 0
                },
                'variant_b': {
                    'recipients': len(variant_b),
                    'opened': b_opened,
                    'clicked': b_clicked,
                    'open_rate': (b_opened / len(variant_b) * 100) if variant_b else 0,
                    'click_rate': (b_clicked / len(variant_b) * 100) if variant_b else 0
                }
            }
        
        return jsonify({
            'campaign_id': campaign_id,
            'total_recipients': campaign.total_recipients,
            'emails_sent': campaign.emails_sent,
            'emails_delivered': campaign.emails_delivered,
            'emails_opened': campaign.emails_opened,
            'emails_clicked': campaign.emails_clicked,
            'emails_bounced': campaign.emails_bounced,
            'emails_failed': campaign.emails_failed,
            'delivery_rate': round(delivery_rate, 2),
            'open_rate': round(open_rate, 2),
            'click_rate': round(click_rate, 2),
            'bounce_rate': round(bounce_rate, 2),
            'ab_test_results': ab_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _build_recipient_list(campaign):
    """Build list of recipients based on campaign segmentation"""
    recipients = []
    
    if campaign.segment_type == 'all_clients':
        clients = Client.query.filter_by(status='active').all()
        recipients = [{'email': c.email, 'type': 'client', 'id': c.id} for c in clients if c.email]
    
    elif campaign.segment_type == 'all_trainers':
        trainers = Trainer.query.filter_by(active=True).all()
        recipients = [{'email': t.email, 'type': 'trainer', 'id': t.id} for t in trainers if t.email]
    
    elif campaign.segment_type == 'specific_ids':
        if campaign.recipient_ids:
            # Get clients
            clients = Client.query.filter(Client.id.in_(campaign.recipient_ids)).all()
            recipients.extend([{'email': c.email, 'type': 'client', 'id': c.id} for c in clients if c.email])
            
            # Get trainers
            trainers = Trainer.query.filter(Trainer.id.in_(campaign.recipient_ids)).all()
            recipients.extend([{'email': t.email, 'type': 'trainer', 'id': t.id} for t in trainers if t.email])
    
    elif campaign.segment_type == 'custom':
        query = Client.query
        filters = campaign.segment_filters or {}
        
        if 'status' in filters:
            query = query.filter_by(status=filters['status'])
        if 'membership_type' in filters:
            query = query.filter_by(membership_type=filters['membership_type'])
        
        clients = query.all()
        recipients = [{'email': c.email, 'type': 'client', 'id': c.id} for c in clients if c.email]
    
    return recipients

def _assign_ab_variant(ab_enabled, split_percentage):
    """Assign A/B test variant based on split percentage"""
    if not ab_enabled:
        return None
    return 'A' if random.randint(1, 100) <= split_percentage else 'B'

def _send_campaign(campaign_id):
    """Send an email campaign"""
    campaign = EmailCampaign.query.get(campaign_id)
    if not campaign:
        return
    
    campaign.status = 'sending'
    campaign.sent_at = datetime.utcnow()
    db.session.commit()
    
    recipients = CampaignRecipient.query.filter_by(campaign_id=campaign_id, status='pending').all()
    
    for recipient in recipients:
        try:
            # Determine subject based on A/B test variant
            subject = campaign.subject
            if campaign.ab_test_enabled:
                if recipient.ab_variant == 'A' and campaign.ab_test_subject_a:
                    subject = campaign.ab_test_subject_a
                elif recipient.ab_variant == 'B' and campaign.ab_test_subject_b:
                    subject = campaign.ab_test_subject_b
            
            # Replace template variables in body
            html_body = campaign.html_body
            text_body = campaign.text_body or ''
            
            # Simple variable replacement (can be enhanced)
            if recipient.recipient_type == 'client' and recipient.recipient_id:
                client = Client.query.get(recipient.recipient_id)
                if client:
                    html_body = html_body.replace('{client_name}', client.name)
                    html_body = html_body.replace('{client_email}', client.email)
                    text_body = text_body.replace('{client_name}', client.name)
                    text_body = text_body.replace('{client_email}', client.email)
            
            # Send email
            success = send_email(recipient.email, subject, text_body, html_body)
            
            if success:
                recipient.status = 'sent'
                recipient.sent_at = datetime.utcnow()
                campaign.emails_sent += 1
                # Assume delivered if sent successfully (in production, use webhooks)
                recipient.status = 'delivered'
                recipient.delivered_at = datetime.utcnow()
                campaign.emails_delivered += 1
            else:
                recipient.status = 'failed'
                recipient.failed_at = datetime.utcnow()
                campaign.emails_failed += 1
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient.email}: {str(e)}")
            recipient.status = 'failed'
            recipient.error_message = str(e)
            recipient.failed_at = datetime.utcnow()
            campaign.emails_failed += 1
            db.session.commit()
    
    campaign.status = 'sent'
    campaign.completed_at = datetime.utcnow()
    db.session.commit()

