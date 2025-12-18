"""
Automation utility functions for triggering automation rules
"""

from models.database import db, AutomationRule, AutomationLog, Client, Trainer, Session, Payment
from utils.email import send_email
from utils.sms import send_sms
from utils.logger import logger
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, extract


def trigger_automation_rules(trigger_event, context=None):
    """
    Trigger automation rules based on an event
    
    Args:
        trigger_event: The event that occurred (e.g., 'session_created', 'payment_due')
        context: Optional context dictionary with event-specific data
                 (e.g., {'session_id': 1, 'client_id': 2})
    """
    try:
        # Find all enabled rules that match this trigger event
        rules = AutomationRule.query.filter_by(
            enabled=True,
            trigger_event=trigger_event
        ).all()
        
        if not rules:
            return
        
        for rule in rules:
            try:
                # Check if rule conditions are met
                if not _check_rule_conditions(rule, trigger_event, context):
                    continue
                
                # Execute the rule
                _execute_automation_rule(rule, context)
                
            except Exception as e:
                logger.error(f"Error executing automation rule {rule.id} for event {trigger_event}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error triggering automation rules for event {trigger_event}: {str(e)}")


def _check_rule_conditions(rule, trigger_event, context):
    """Check if rule conditions are met"""
    conditions = rule.trigger_conditions or {}
    
    if trigger_event == 'session_created' or trigger_event == 'session_scheduled':
        # Check if session matches conditions
        if context and 'session_id' in context:
            session = Session.query.get(context['session_id'])
            if not session:
                return False
            
            # Check hours_before condition for reminders
            if 'hours_before' in conditions:
                hours_before = conditions['hours_before']
                session_time = session.session_date
                reminder_time = session_time - timedelta(hours=hours_before)
                
                # Only trigger if we're within 1 hour of the reminder time
                now = datetime.utcnow()
                if abs((reminder_time - now).total_seconds()) > 3600:
                    return False
            
            # Check status condition
            if 'status' in conditions and session.status != conditions['status']:
                return False
                
        return True
    
    elif trigger_event == 'payment_due' or trigger_event == 'payment_overdue':
        # Check if payment matches conditions
        if context and 'payment_id' in context:
            payment = Payment.query.get(context['payment_id'])
            if not payment:
                return False
            
            # Check amount threshold if specified
            if 'min_amount' in conditions:
                if payment.amount < conditions['min_amount']:
                    return False
            
        return True
    
    elif trigger_event == 'birthday':
        # Birthday triggers are handled by the background worker
        return True
    
    return True


def _execute_automation_rule(rule, context=None):
    """Execute an automation rule"""
    log = AutomationLog(
        rule_id=rule.id,
        action_type=rule.action_type,
        status='success',
        trigger_context=context or {}
    )
    
    try:
        # Get recipients based on target audience and context
        recipients = _get_rule_recipients(rule, context)
        log.recipients_count = len(recipients)
        
        sent_count = 0
        failed_count = 0
        
        for recipient in recipients:
            try:
                # Prepare message based on rule type and context
                subject, message, html_message = _prepare_automation_message(rule, recipient, context)
                
                # Send based on action type
                if rule.action_type in ['email', 'both']:
                    if recipient.get('email'):
                        success = send_email(recipient['email'], subject, message, html_message)
                        if success:
                            sent_count += 1
                        else:
                            failed_count += 1
                
                if rule.action_type in ['sms', 'both']:
                    if recipient.get('phone'):
                        result = send_sms(recipient['phone'], message)
                        if result.get('success'):
                            sent_count += 1
                        else:
                            failed_count += 1
                
            except Exception as e:
                logger.error(f"Error sending to {recipient.get('email', recipient.get('phone'))}: {str(e)}")
                failed_count += 1
        
        log.sent_count = sent_count
        log.failed_count = failed_count
        log.status = 'success' if failed_count == 0 else 'partial'
        
        # Update rule statistics
        rule.run_count += 1
        rule.success_count += (1 if failed_count == 0 else 0)
        rule.failure_count += (1 if failed_count > 0 else 0)
        rule.last_run_at = datetime.utcnow()
        
    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)
        rule.failure_count += 1
        logger.error(f"Error executing rule {rule.id}: {str(e)}")
    
    db.session.add(log)
    db.session.commit()
    
    return {
        'recipients': log.recipients_count,
        'sent': log.sent_count,
        'failed': log.failed_count,
        'status': log.status
    }


def _get_rule_recipients(rule, context=None):
    """Get recipients for an automation rule"""
    recipients = []
    
    # If context has specific client_id, use that
    if context and 'client_id' in context:
        client = Client.query.get(context['client_id'])
        if client and client.email:
            recipients.append({
                'email': client.email,
                'phone': client.phone,
                'name': client.name,
                'type': 'client',
                'id': client.id
            })
            return recipients
    
    if rule.target_audience == 'all':
        clients = Client.query.filter_by(status='active').all()
        recipients.extend([{
            'email': c.email,
            'phone': c.phone,
            'name': c.name,
            'type': 'client',
            'id': c.id
        } for c in clients if c.email])
        
        trainers = Trainer.query.filter_by(active=True).all()
        recipients.extend([{
            'email': t.email,
            'phone': t.phone,
            'name': t.name,
            'type': 'trainer',
            'id': t.id
        } for t in trainers if t.email])
    
    elif rule.target_audience == 'clients':
        query = Client.query
        filters = rule.target_filters or {}
        
        if 'status' in filters:
            query = query.filter_by(status=filters['status'])
        if 'membership_type' in filters:
            query = query.filter_by(membership_type=filters['membership_type'])
        
        clients = query.all()
        recipients = [{
            'email': c.email,
            'phone': c.phone,
            'name': c.name,
            'type': 'client',
            'id': c.id
        } for c in clients if c.email]
    
    elif rule.target_audience == 'trainers':
        trainers = Trainer.query.filter_by(active=True).all()
        recipients = [{
            'email': t.email,
            'phone': t.phone,
            'name': t.name,
            'type': 'trainer',
            'id': t.id
        } for t in trainers if t.email]
    
    elif rule.target_audience == 'specific' and rule.target_ids:
        clients = Client.query.filter(Client.id.in_(rule.target_ids)).all()
        recipients.extend([{
            'email': c.email,
            'phone': c.phone,
            'name': c.name,
            'type': 'client',
            'id': c.id
        } for c in clients if c.email])
        
        trainers = Trainer.query.filter(Trainer.id.in_(rule.target_ids)).all()
        recipients.extend([{
            'email': t.email,
            'phone': t.phone,
            'name': t.name,
            'type': 'trainer',
            'id': t.id
        } for t in trainers if t.email])
    
    return recipients


def _prepare_automation_message(rule, recipient, context=None):
    """Prepare message content for automation rule"""
    # Use custom message if provided
    if rule.custom_message:
        message = rule.custom_message
        html_message = None
    else:
        # Default messages based on rule type
        if rule.rule_type == 'session_reminder':
            session_info = ""
            if context and 'session_id' in context:
                session = Session.query.get(context['session_id'])
                if session:
                    session_info = f" on {session.session_date.strftime('%B %d, %Y at %I:%M %p')}"
            message = f"Reminder: You have a training session{session_info}!"
            html_message = f"<p>Reminder: You have a training session{session_info}!</p>"
        elif rule.rule_type == 'payment_reminder':
            payment_info = ""
            if context and 'payment_id' in context:
                payment = Payment.query.get(context['payment_id'])
                if payment:
                    payment_info = f" of ${payment.amount:.2f}"
            message = f"Friendly reminder: Your payment{payment_info} is due soon."
            html_message = f"<p>Friendly reminder: Your payment{payment_info} is due soon.</p>"
        elif rule.rule_type == 'birthday':
            name = recipient.get('name', 'there')
            message = f"Happy Birthday {name}! 🎉"
            html_message = f"<p>Happy Birthday {name}! 🎉</p>"
        else:
            message = rule.custom_message or "Notification from FitnessCRM"
            html_message = None
    
    # Replace variables
    name = recipient.get('name', '')
    if name:
        message = message.replace('{name}', name)
        if html_message:
            html_message = html_message.replace('{name}', name)
    
    subject = f"FitnessCRM: {rule.name}"
    
    return subject, message, html_message


def process_time_based_triggers():
    """
    Process time-based automation triggers (birthdays, payment due dates, session reminders)
    This should be called periodically (e.g., via cron job or scheduled task)
    """
    now = datetime.utcnow()
    results = {
        'birthdays': 0,
        'payment_reminders': 0,
        'session_reminders': 0,
        'errors': []
    }
    
    try:
        # Check for birthday triggers
        today = now.date()
        birthday_clients = Client.query.filter(
            extract('month', Client.date_of_birth) == today.month,
            extract('day', Client.date_of_birth) == today.day
        ).all()
        
        if birthday_clients:
            birthday_rules = AutomationRule.query.filter_by(
                enabled=True,
                trigger_event='birthday'
            ).all()
            
            for rule in birthday_rules:
                for client in birthday_clients:
                    if client.email or client.phone:
                        context = {'client_id': client.id}
                        try:
                            _execute_automation_rule(rule, context)
                            results['birthdays'] += 1
                        except Exception as e:
                            results['errors'].append(f"Birthday rule {rule.id} for client {client.id}: {str(e)}")
        
        # Check for payment due reminders (payments with pending status)
        # Note: Payment model doesn't have due_date, so we check by status
        pending_payments = Payment.query.filter(
            Payment.status == 'pending'
        ).all()
        
        if pending_payments:
            payment_rules = AutomationRule.query.filter_by(
                enabled=True,
                trigger_event='payment_due'
            ).all()
            
            for rule in payment_rules:
                for payment in pending_payments:
                    context = {'payment_id': payment.id, 'client_id': payment.client_id}
                    try:
                        _execute_automation_rule(rule, context)
                        results['payment_reminders'] += 1
                    except Exception as e:
                        results['errors'].append(f"Payment reminder rule {rule.id} for payment {payment.id}: {str(e)}")
        
        # Check for overdue payments
        overdue_payments = Payment.query.filter(
            Payment.status == 'overdue'
        ).all()
        
        if overdue_payments:
            overdue_rules = AutomationRule.query.filter_by(
                enabled=True,
                trigger_event='payment_overdue'
            ).all()
            
            for rule in overdue_rules:
                for payment in overdue_payments:
                    context = {'payment_id': payment.id, 'client_id': payment.client_id}
                    try:
                        _execute_automation_rule(rule, context)
                        results['payment_reminders'] += 1
                    except Exception as e:
                        results['errors'].append(f"Overdue payment rule {rule.id} for payment {payment.id}: {str(e)}")
        
        # Check for session reminders (sessions happening in X hours)
        session_reminder_rules = AutomationRule.query.filter_by(
            enabled=True,
            trigger_event='session_scheduled'
        ).all()
        
        for rule in session_reminder_rules:
            hours_before = rule.trigger_conditions.get('hours_before', 24) if rule.trigger_conditions else 24
            reminder_time_start = now + timedelta(hours=hours_before - 1)
            reminder_time_end = now + timedelta(hours=hours_before + 1)
            
            upcoming_sessions = Session.query.filter(
                Session.session_date >= reminder_time_start,
                Session.session_date <= reminder_time_end,
                Session.status == 'scheduled'
            ).all()
            
            for session in upcoming_sessions:
                context = {'session_id': session.id, 'client_id': session.client_id}
                try:
                    _execute_automation_rule(rule, context)
                    results['session_reminders'] += 1
                except Exception as e:
                    results['errors'].append(f"Session reminder rule {rule.id} for session {session.id}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error processing time-based triggers: {str(e)}")
        results['errors'].append(str(e))
    
    return results

