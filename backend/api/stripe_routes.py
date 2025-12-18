"""
Stripe payment integration routes
Phase 6: Mobile & Integrations - M6.3: Payment Integration
"""

from flask import Blueprint, request, jsonify, current_app
from models.database import db, Payment, Client
from utils.stripe_helper import (
    get_stripe_client, create_payment_intent, create_customer,
    create_subscription, cancel_subscription, create_refund,
    get_payment_methods, verify_webhook_signature, is_stripe_configured
)
from utils.logger import logger
from datetime import datetime
import os

stripe_bp = Blueprint('stripe', __name__, url_prefix='/api/stripe')

@stripe_bp.route('/config', methods=['GET'])
def get_stripe_config():
    """Get Stripe public configuration"""
    stripe_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    
    return jsonify({
        'configured': is_stripe_configured(),
        'publishable_key': stripe_key if stripe_key else None
    }), 200

@stripe_bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent_route():
    """Create a Stripe PaymentIntent"""
    if not is_stripe_configured():
        return jsonify({'error': 'Stripe is not configured'}), 503
    
    data = request.get_json()
    
    if not data or not data.get('amount') or not data.get('client_id'):
        return jsonify({'error': 'Amount and client_id are required'}), 400
    
    try:
        # Get or create Stripe customer
        client = Client.query.get(data['client_id'])
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        stripe_customer_id = None
        if client.email:
            # Check if client already has Stripe customer ID
            existing_payment = Payment.query.filter_by(
                client_id=client.id,
                stripe_customer_id=Payment.stripe_customer_id.isnot(None)
            ).first()
            
            if existing_payment and existing_payment.stripe_customer_id:
                stripe_customer_id = existing_payment.stripe_customer_id
            else:
                # Create new Stripe customer
                stripe_customer = create_customer(
                    email=client.email,
                    name=client.name,
                    phone=client.phone,
                    metadata={'client_id': str(client.id)}
                )
                if stripe_customer:
                    stripe_customer_id = stripe_customer.id
        
        # Create payment intent
        metadata = {
            'client_id': str(client.id),
            'client_name': client.name,
            'payment_type': data.get('payment_type', 'membership')
        }
        
        intent = create_payment_intent(
            amount=data['amount'],
            currency=data.get('currency', 'usd'),
            metadata=metadata,
            customer_id=stripe_customer_id
        )
        
        if not intent:
            return jsonify({'error': 'Failed to create payment intent'}), 500
        
        # Create payment record
        payment = Payment(
            client_id=client.id,
            amount=data['amount'],
            payment_method='stripe',
            payment_type=data.get('payment_type', 'membership'),
            status='pending',
            stripe_payment_intent_id=intent.id,
            stripe_customer_id=stripe_customer_id,
            transaction_id=intent.id
        )
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'client_secret': intent.client_secret,
            'payment_id': payment.id,
            'payment_intent_id': intent.id
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    """Confirm a payment after successful Stripe payment"""
    if not is_stripe_configured():
        return jsonify({'error': 'Stripe is not configured'}), 503
    
    data = request.get_json()
    
    if not data or not data.get('payment_intent_id'):
        return jsonify({'error': 'payment_intent_id is required'}), 400
    
    try:
        stripe_client = get_stripe_client()
        payment_intent = stripe_client.PaymentIntent.retrieve(data['payment_intent_id'])
        
        # Find payment record
        payment = Payment.query.filter_by(
            stripe_payment_intent_id=data['payment_intent_id']
        ).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # Update payment status based on Stripe status
        if payment_intent.status == 'succeeded':
            payment.status = 'completed'
            payment.stripe_charge_id = payment_intent.latest_charge
            payment.payment_date = datetime.utcnow()
        elif payment_intent.status == 'canceled':
            payment.status = 'failed'
        else:
            payment.status = 'pending'
        
        db.session.commit()
        
        return jsonify({
            'payment_id': payment.id,
            'status': payment.status,
            'stripe_status': payment_intent.status
        }), 200
        
    except Exception as e:
        logger.error(f"Error confirming payment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/create-subscription', methods=['POST'])
def create_subscription_route():
    """Create a Stripe subscription"""
    if not is_stripe_configured():
        return jsonify({'error': 'Stripe is not configured'}), 503
    
    data = request.get_json()
    
    if not data or not data.get('client_id') or not data.get('price_id'):
        return jsonify({'error': 'client_id and price_id are required'}), 400
    
    try:
        client = Client.query.get(data['client_id'])
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Get or create Stripe customer
        stripe_customer_id = None
        if client.email:
            existing_payment = Payment.query.filter_by(
                client_id=client.id,
                stripe_customer_id=Payment.stripe_customer_id.isnot(None)
            ).first()
            
            if existing_payment and existing_payment.stripe_customer_id:
                stripe_customer_id = existing_payment.stripe_customer_id
            else:
                stripe_customer = create_customer(
                    email=client.email,
                    name=client.name,
                    phone=client.phone,
                    metadata={'client_id': str(client.id)}
                )
                if stripe_customer:
                    stripe_customer_id = stripe_customer.id
        
        if not stripe_customer_id:
            return jsonify({'error': 'Failed to create Stripe customer'}), 500
        
        # Create subscription
        metadata = {
            'client_id': str(client.id),
            'client_name': client.name
        }
        
        subscription = create_subscription(
            customer_id=stripe_customer_id,
            price_id=data['price_id'],
            metadata=metadata
        )
        
        if not subscription:
            return jsonify({'error': 'Failed to create subscription'}), 500
        
        # Create payment record for subscription
        amount = data.get('amount', 0)  # Amount from price
        payment = Payment(
            client_id=client.id,
            amount=amount,
            payment_method='stripe',
            payment_type='subscription',
            status='completed',
            stripe_customer_id=stripe_customer_id,
            transaction_id=subscription.id,
            notes=f"Subscription: {subscription.id}"
        )
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'subscription_id': subscription.id,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice else None,
            'payment_id': payment.id
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/cancel-subscription', methods=['POST'])
def cancel_subscription_route():
    """Cancel a Stripe subscription"""
    if not is_stripe_configured():
        return jsonify({'error': 'Stripe is not configured'}), 503
    
    data = request.get_json()
    
    if not data or not data.get('subscription_id'):
        return jsonify({'error': 'subscription_id is required'}), 400
    
    try:
        cancel_immediately = data.get('cancel_immediately', False)
        subscription = cancel_subscription(
            subscription_id=data['subscription_id'],
            cancel_immediately=cancel_immediately
        )
        
        if not subscription:
            return jsonify({'error': 'Failed to cancel subscription'}), 500
        
        return jsonify({
            'subscription_id': subscription.id,
            'status': subscription.status,
            'cancel_at_period_end': subscription.cancel_at_period_end
        }), 200
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/refund', methods=['POST'])
def refund_payment():
    """Create a refund for a payment"""
    if not is_stripe_configured():
        return jsonify({'error': 'Stripe is not configured'}), 503
    
    data = request.get_json()
    
    if not data or not data.get('payment_id'):
        return jsonify({'error': 'payment_id is required'}), 400
    
    try:
        payment = Payment.query.get(data['payment_id'])
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if not payment.stripe_charge_id:
            return jsonify({'error': 'Payment does not have a Stripe charge ID'}), 400
        
        refund = create_refund(
            charge_id=payment.stripe_charge_id,
            amount=data.get('amount'),  # Partial refund if specified
            reason=data.get('reason', 'requested_by_customer')
        )
        
        if not refund:
            return jsonify({'error': 'Failed to create refund'}), 500
        
        # Update payment status
        payment.status = 'refunded'
        db.session.commit()
        
        return jsonify({
            'refund_id': refund.id,
            'amount': refund.amount / 100,  # Convert from cents
            'status': refund.status
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating refund: {str(e)}")
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/payment-methods/<customer_id>', methods=['GET'])
def get_customer_payment_methods(customer_id):
    """Get saved payment methods for a customer"""
    if not is_stripe_configured():
        return jsonify({'error': 'Stripe is not configured'}), 503
    
    try:
        payment_methods = get_payment_methods(customer_id)
        
        if payment_methods is None:
            return jsonify({'error': 'Failed to get payment methods'}), 500
        
        methods = []
        for pm in payment_methods:
            methods.append({
                'id': pm.id,
                'type': pm.type,
                'card': {
                    'brand': pm.card.brand,
                    'last4': pm.card.last4,
                    'exp_month': pm.card.exp_month,
                    'exp_year': pm.card.exp_year
                } if pm.type == 'card' else None
            })
        
        return jsonify({'payment_methods': methods}), 200
        
    except Exception as e:
        logger.error(f"Error getting payment methods: {str(e)}")
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    if not is_stripe_configured():
        return jsonify({'error': 'Stripe is not configured'}), 503
    
    payload = request.data
    signature = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    if not webhook_secret:
        logger.warning("Stripe webhook secret not configured")
        return jsonify({'error': 'Webhook secret not configured'}), 500
    
    # Verify webhook signature
    event = verify_webhook_signature(payload, signature, webhook_secret)
    
    if not event:
        return jsonify({'error': 'Invalid webhook signature'}), 400
    
    try:
        # Handle different event types
        event_type = event['type']
        
        if event_type == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment = Payment.query.filter_by(
                stripe_payment_intent_id=payment_intent['id']
            ).first()
            
            if payment:
                payment.status = 'completed'
                payment.stripe_charge_id = payment_intent.get('latest_charge')
                payment.payment_date = datetime.utcnow()
                db.session.commit()
                logger.info(f"Payment {payment.id} confirmed via webhook")
        
        elif event_type == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            payment = Payment.query.filter_by(
                stripe_payment_intent_id=payment_intent['id']
            ).first()
            
            if payment:
                payment.status = 'failed'
                db.session.commit()
                logger.info(f"Payment {payment.id} failed via webhook")
        
        elif event_type == 'charge.refunded':
            charge = event['data']['object']
            payment = Payment.query.filter_by(
                stripe_charge_id=charge['id']
            ).first()
            
            if payment:
                payment.status = 'refunded'
                db.session.commit()
                logger.info(f"Payment {payment.id} refunded via webhook")
        
        elif event_type == 'customer.subscription.created':
            subscription = event['data']['object']
            logger.info(f"Subscription created: {subscription['id']}")
        
        elif event_type == 'customer.subscription.deleted':
            subscription = event['data']['object']
            logger.info(f"Subscription cancelled: {subscription['id']}")
        
        return jsonify({'received': True}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

